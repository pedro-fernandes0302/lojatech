import os
import sqlite3
import tempfile
import threading
import unittest

_TEMP = tempfile.TemporaryDirectory()
os.environ["TECHSTOCK_DATABASE"] = os.path.join(_TEMP.name, "import.db")

import db
from app import app
from permissions import POLICIES, PUBLIC_ENDPOINTS
from routers.utils import converter_centavos, converter_preco


app.testing = True
GERENTE = {"id_usuario": 1, "nome": "Gerente", "email": "gerente@techstore.com", "perfil": "GERENTE"}
OPERADOR = {"id_usuario": 2, "nome": "Operador", "email": "operador@techstore.com", "perfil": "OPERADOR"}


def autenticar_cliente(cliente, usuario=OPERADOR):
    with cliente.session_transaction() as sessao:
        sessao.update(usuario)


def estado_venda():
    conn = db.get_db()
    try:
        return {
            "saldos": [tuple(row) for row in conn.execute("SELECT id_produto, estoque_atual FROM produtos ORDER BY id_produto")],
            "vendas": conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0],
            "itens": conn.execute("SELECT COUNT(*) FROM itens_venda").fetchone()[0],
            "movimentacoes": conn.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0],
        }
    finally:
        conn.close()


class TechStockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        db.DATABASE = os.path.join(self.temp.name, "techstock.db")
        db.init_db()
        app.config["TESTING"] = True

    def tearDown(self):
        self.temp.cleanup()

    def cliente(self, usuario=OPERADOR):
        cliente = app.test_client()
        autenticar_cliente(cliente, usuario)
        return cliente

    def test_init_db(self):
        conn = db.get_db()
        try:
            objetos = {row["name"]: row["type"] for row in conn.execute(
                "SELECT name, type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
            )}
            self.assertTrue({
                "usuarios", "categoria", "fornecedor", "produtos", "movimentacoes",
                "ativos_digitais", "estoque_fisico", "clientes", "vendas", "itens_venda",
                "movimentacoes_sem_update", "movimentacoes_sem_delete",
            }.issubset(objetos))
            gatilhos = {row["name"] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )}
            self.assertTrue({
                "itens_venda_sem_update", "itens_venda_sem_delete",
                "vendas_sem_delete", "vendas_total_imutavel",
            }.issubset(gatilhos))
            self.assertEqual(objetos["estoque_fisico"], "view")
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT perfil FROM usuarios WHERE email = 'gerente@techstore.com'").fetchone()[0], "GERENTE")
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM ativos_digitais").fetchone()[0], 3)
        finally:
            conn.close()

    def test_ensure_database_preserva_banco_parcial(self):
        anterior = db.DATABASE
        parcial = os.path.join(self.temp.name, "parcial.db")
        try:
            db.DATABASE = parcial
            conn = sqlite3.connect(parcial)
            conn.execute("CREATE TABLE produtos (id_produto INTEGER PRIMARY KEY, marcador TEXT)")
            conn.execute("INSERT INTO produtos VALUES (1, 'preservar')")
            conn.commit()
            conn.close()
            with self.assertRaisesRegex(RuntimeError, "Banco existente está incompleto"):
                db.ensure_database()
            conn = sqlite3.connect(parcial)
            self.assertEqual(conn.execute("SELECT marcador FROM produtos").fetchone()[0], "preservar")
            conn.close()
        finally:
            db.DATABASE = anterior

    def test_venda_ok(self):
        resposta = self.cliente().post("/api/vendas", json={
            "id_cliente": 1,
            "itens": [
                {"id_produto": 1, "quantidade": 1},
                {"id_produto": 2, "quantidade": 2},
                {"id_produto": 4, "quantidade": 1},
            ],
        })
        self.assertEqual(resposta.status_code, 201, resposta.json)
        venda_id = resposta.json["id_venda"]
        conn = db.get_db()
        try:
            self.assertEqual(conn.execute("SELECT estoque_atual FROM produtos WHERE id_produto=1").fetchone()[0], 9)
            self.assertEqual(conn.execute("SELECT estoque_atual FROM produtos WHERE id_produto=2").fetchone()[0], 18)
            self.assertEqual(conn.execute("SELECT estoque_atual FROM produtos WHERE id_produto=4").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM itens_venda WHERE id_venda=?", (venda_id,)).fetchone()[0], 3)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM movimentacoes WHERE id_venda=?", (venda_id,)).fetchone()[0], 3)
            self.assertEqual(conn.execute("SELECT valor_total_centavos FROM vendas WHERE id_venda=?", (venda_id,)).fetchone()[0], 152999)
        finally:
            conn.close()
        recibo = self.cliente().get(f"/api/vendas/{venda_id}/recibo")
        self.assertEqual(recibo.status_code, 200)
        self.assertEqual(recibo.json["valor_total_centavos"], 152999)
        self.assertEqual(len(recibo.json["itens"]), 3)
        self.assertEqual(recibo.json["cliente_cnpj"], "45678900000193")
        self.assertEqual(self.cliente().get(f"/api/vendas/{venda_id}/recibo/imprimir").status_code, 200)

    def test_venda_rollback(self):
        antes = estado_venda()
        resposta = self.cliente().post("/api/vendas", json={
            "id_cliente": 1,
            "itens": [{"id_produto": 1, "quantidade": 1}, {"id_produto": 6, "quantidade": 2}],
        })
        self.assertEqual(resposta.status_code, 409)
        self.assertIn("Estoque insuficiente para Mouse USB: disponível 1", resposta.json["erro"])
        self.assertEqual(estado_venda(), antes)

    def test_venda_falha_no_meio(self):
        conn = db.get_db()
        try:
            conn.execute("""
                CREATE TRIGGER falha_movimentacao_venda BEFORE INSERT ON movimentacoes
                WHEN NEW.id_venda IS NOT NULL
                BEGIN SELECT RAISE(ABORT, 'falha injetada'); END
            """)
            conn.commit()
        finally:
            conn.close()
        antes = estado_venda()
        resposta = self.cliente().post("/api/vendas", json={
            "id_cliente": 1,
            "itens": [{"id_produto": 1, "quantidade": 1}],
        })
        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(estado_venda(), antes)

    def test_concorrencia_venda(self):
        resultados = []
        lock = threading.Lock()

        def vender():
            resposta = self.cliente().post("/api/vendas", json={
                "id_cliente": 1, "itens": [{"id_produto": 6, "quantidade": 1}],
            })
            with lock:
                resultados.append(resposta.status_code)

        threads = [threading.Thread(target=vender) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=40)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(resultados.count(201), 1)
        self.assertEqual(resultados.count(409), 19)
        conn = db.get_db()
        try:
            self.assertEqual(conn.execute("SELECT estoque_atual FROM produtos WHERE id_produto=6").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0], 1)
        finally:
            conn.close()

    def test_rbac(self):
        rotas = []
        for regra in app.url_map.iter_rules():
            endpoint = regra.endpoint
            if endpoint == "static":
                continue
            rotas.append((regra, endpoint))
            if endpoint not in PUBLIC_ENDPOINTS:
                self.assertIn(endpoint, POLICIES, f"Política ausente: {endpoint}")

        for regra, endpoint in rotas:
            metodo = next((m for m in ("GET", "POST", "PATCH", "DELETE") if m in regra.methods), "GET")
            caminho = regra.rule.replace("<int:id>", "1").replace("<id>", "1")
            if endpoint not in PUBLIC_ENDPOINTS:
                anonimo = app.test_client().open(caminho, method=metodo)
                self.assertIn(anonimo.status_code, (401, 302), f"{metodo} {caminho}: {anonimo.status_code}")
            if endpoint in POLICIES and "OPERADOR" not in POLICIES[endpoint]:
                resposta = self.cliente(OPERADOR).open(caminho, method=metodo, json={})
                self.assertEqual(resposta.status_code, 403, f"Operador {metodo} {caminho}: {resposta.status_code}")
            gerente = self.cliente(GERENTE).open(caminho, method=metodo, json={})
            self.assertNotEqual(gerente.status_code, 403, f"Gerente {metodo} {caminho}")

    def test_livro_razao_imutavel(self):
        conn = db.get_db()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE movimentacoes SET quantidade=2 WHERE id_movimentacao=1")
            conn.rollback()
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM movimentacoes WHERE id_movimentacao=1")
            conn.rollback()
        finally:
            conn.close()

    def test_venda_e_itens_imutaveis(self):
        response = self.cliente().post("/api/vendas", json={
            "id_cliente": 1, "itens": [{"id_produto": 1, "quantidade": 1}],
        })
        self.assertEqual(response.status_code, 201)
        venda_id = response.json["id_venda"]
        conn = db.get_db()
        try:
            for sql, args in (
                ("UPDATE itens_venda SET quantidade=2 WHERE id_venda=?", (venda_id,)),
                ("DELETE FROM itens_venda WHERE id_venda=?", (venda_id,)),
                ("DELETE FROM vendas WHERE id_venda=?", (venda_id,)),
                ("UPDATE vendas SET valor_total_centavos=1 WHERE id_venda=?", (venda_id,)),
            ):
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(sql, args)
                conn.rollback()
        finally:
            conn.close()

    def test_perfil_atualizado_revoga_sessao_antiga(self):
        conn = db.get_db()
        try:
            conn.execute("UPDATE usuarios SET perfil='OPERADOR' WHERE id_usuario=1")
            conn.commit()
        finally:
            conn.close()
        response = self.cliente(GERENTE).post("/api/categorias", json={"nome": "Bloqueada"})
        self.assertEqual(response.status_code, 403)

    def test_recibo_privado_e_perfil_sem_auto_promocao(self):
        venda = self.cliente().post("/api/vendas", json={
            "id_cliente": 1, "itens": [{"id_produto": 1, "quantidade": 1}],
        })
        outro = self.cliente()
        cadastro = outro.post("/api/cadastro", json={
            "nome": "Outro operador", "email": "outro@techstore.com", "senha": "senha-segura-123",
        })
        self.assertEqual(cadastro.status_code, 201)
        login = outro.post("/api/login", json={
            "email": "outro@techstore.com", "senha": "senha-segura-123",
        })
        self.assertEqual(login.status_code, 200)
        self.assertEqual(outro.get(f"/api/vendas/{venda.json['id_venda']}/recibo").status_code, 403)
        self.assertEqual(outro.get(f"/api/vendas/{venda.json['id_venda']}/recibo/imprimir").status_code, 403)
        self.assertEqual(outro.patch("/api/usuarios/3/perfil", json={"perfil": "GERENTE"}).status_code, 403)
        dono = self.cliente(OPERADOR)
        with dono.session_transaction() as sessao:
            sessao.update({"id_usuario": 2, "perfil": "OPERADOR"})
        self.assertEqual(dono.patch("/api/usuarios/2/perfil", json={"perfil": "GERENTE"}).status_code, 403)
        gerente = self.cliente(GERENTE)
        self.assertEqual(gerente.patch("/api/usuarios/1/perfil", json={"perfil": "OPERADOR"}).status_code, 409)

    def test_validacao_inteiro_estrito_e_movimentacao_digital(self):
        cliente = self.cliente()
        self.assertEqual(cliente.post("/api/vendas", json={
            "id_cliente": 1.5, "itens": [{"id_produto": 1, "quantidade": 1}],
        }).status_code, 400)
        self.assertEqual(cliente.post("/api/vendas", json={
            "id_cliente": 1, "itens": [{"id_produto": 1, "quantidade": 1.5}],
        }).status_code, 400)
        self.assertEqual(cliente.post("/api/movimentacoes", json={
            "produto_id": 4, "tipo": "SAIDA", "quantidade": 1,
        }).status_code, 409)

    def test_livro_razao_join_e_filtro(self):
        self.cliente().post("/api/vendas", json={
            "id_cliente": 1, "itens": [{"id_produto": 1, "quantidade": 1}],
        })
        conn = db.get_db()
        try:
            venda_id = conn.execute("SELECT id_venda FROM vendas").fetchone()[0]
        finally:
            conn.close()
        resposta = self.cliente(GERENTE).get(f"/api/livro-razao?venda={venda_id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.json), 1)
        self.assertEqual(resposta.json[0]["cliente"], "TechStore Cliente A")
        self.assertEqual(resposta.json[0]["usuario"], "Operador TechStore")

    def test_parser_preco(self):
        self.assertEqual(converter_preco("529.99"), 529.99)
        self.assertEqual(converter_preco("1.299,90"), 1299.9)
        self.assertEqual(converter_centavos("1.299,90"), 129990)
        self.assertEqual(converter_centavos("529.99"), 52999)


if __name__ == "__main__":
    unittest.main()
