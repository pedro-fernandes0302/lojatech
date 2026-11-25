import sqlite3
import uuid
from decimal import Decimal

from flask import Blueprint, jsonify, render_template, request, session

from db import get_db
from routers.utils import converter_centavos, normalizar_cnpj

bp = Blueprint("api", __name__, url_prefix="/api")


class EstoqueInsuficiente(Exception):
    pass


def erro(mensagem, codigo=400):
    return jsonify({"erro": mensagem}), codigo


def inteiro_estrito(valor):
    if isinstance(valor, bool) or (isinstance(valor, float) and not valor.is_integer()):
        raise ValueError("Esperado um número inteiro.")
    if isinstance(valor, str) and not valor.strip().isdigit():
        raise ValueError("Esperado um número inteiro.")
    return int(valor)


@bp.get("/sessao")
def sessao_api():
    return jsonify({
        "id_usuario": session["id_usuario"],
        "nome": session["nome"],
        "email": session["email"],
        "perfil": session["perfil"],
    })


def _catalogo(conn):
    return conn.execute("""
        SELECT p.id_produto AS id, p.sku, p.nome_produto AS nome, p.fabricante, p.tipo,
               CASE WHEN p.tipo = 'Software' THEN 'Licença Digital' ELSE 'Hardware Físico' END AS tipo_catalogo,
               c.nome_categoria AS categoria, f.razao_social AS fornecedor, p.preco,
               p.estoque_atual, p.estoque_minimo, p.localizacao, p.modalidade AS modalidade_licenca,
               COALESCE(ef.quantidade, 0) AS quantidade_fisica,
               COALESCE(ad.chaves_disponiveis, 0) AS chaves_disponiveis
        FROM produtos p
        JOIN categoria c ON c.id_categoria = p.id_categoria
        JOIN fornecedor f ON f.id_fornecedor = p.id_fornecedor
        LEFT JOIN estoque_fisico ef ON ef.id_produto = p.id_produto
        LEFT JOIN (
            SELECT id_produto, COUNT(*) AS chaves_disponiveis
            FROM ativos_digitais WHERE id_venda IS NULL GROUP BY id_produto
        ) ad ON ad.id_produto = p.id_produto
        ORDER BY p.nome_produto
    """).fetchall()


@bp.get("/dashboard")
def dashboard_api():
    conn = get_db()
    try:
        return jsonify({
            "produtos": [dict(row) for row in _catalogo(conn)],
            "categorias": conn.execute("SELECT COUNT(*) FROM categoria").fetchone()[0],
            "fornecedores": conn.execute("SELECT COUNT(*) FROM fornecedor").fetchone()[0],
        })
    finally:
        conn.close()


@bp.get("/categorias")
def listar_categorias_api():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id_categoria AS id, nome_categoria AS nome FROM categoria ORDER BY nome_categoria")
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


@bp.post("/categorias")
def criar_categoria_api():
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()
    if not nome:
        return erro("Informe o nome da categoria.")
    conn = get_db()
    try:
        conn.execute("INSERT INTO categoria (nome_categoria, descricao) VALUES (?, '')", (nome,))
        conn.commit()
        return jsonify({"mensagem": "Categoria cadastrada com sucesso."}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return erro("Já existe uma categoria com esse nome.")
    finally:
        conn.close()


@bp.delete("/categorias/<int:id>")
def excluir_categoria_api(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT 1 FROM categoria WHERE id_categoria = ?", (id,)).fetchone():
            return erro("Categoria não encontrada.", 404)
        try:
            conn.execute("DELETE FROM categoria WHERE id_categoria = ?", (id,))
            conn.commit()
            return jsonify({"mensagem": "Categoria excluída com sucesso."})
        except sqlite3.IntegrityError:
            conn.rollback()
            return erro("Não é possível excluir: existem produtos vinculados à categoria.", 409)
    finally:
        conn.close()


@bp.get("/fornecedores")
def listar_fornecedores_api():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id_fornecedor AS id, razao_social, cnpj, telefone, email FROM fornecedor ORDER BY razao_social")
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


@bp.post("/fornecedores")
def criar_fornecedor_api():
    dados = request.get_json(silent=True) or {}
    razao = str(dados.get("razao_social", "")).strip()
    cnpj = normalizar_cnpj(dados.get("cnpj", ""))
    telefone = str(dados.get("telefone", "")).strip()
    email = str(dados.get("email", "")).strip()
    if not razao or len(cnpj) != 14 or not telefone or not email:
        return erro("Informe razão social, CNPJ válido, telefone e e-mail.")
    conn = get_db()
    try:
        conn.execute("INSERT INTO fornecedor (razao_social, cnpj, telefone, email) VALUES (?, ?, ?, ?)",
                     (razao, cnpj, telefone, email))
        conn.commit()
        return jsonify({"mensagem": "Fornecedor cadastrado com sucesso."}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return erro("CNPJ ou e-mail já cadastrado.")
    finally:
        conn.close()


@bp.delete("/fornecedores/<int:id>")
def excluir_fornecedor_api(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT 1 FROM fornecedor WHERE id_fornecedor = ?", (id,)).fetchone():
            return erro("Fornecedor não encontrado.", 404)
        try:
            conn.execute("DELETE FROM fornecedor WHERE id_fornecedor = ?", (id,))
            conn.commit()
            return jsonify({"mensagem": "Fornecedor excluído com sucesso."})
        except sqlite3.IntegrityError:
            conn.rollback()
            return erro("Não é possível excluir: existem produtos vinculados ao fornecedor.", 409)
    finally:
        conn.close()


@bp.get("/produtos/opcoes")
def opcoes_produto_api():
    conn = get_db()
    try:
        categorias = conn.execute("SELECT id_categoria AS id, nome_categoria AS nome FROM categoria ORDER BY nome_categoria")
        fornecedores = conn.execute("SELECT id_fornecedor AS id, razao_social FROM fornecedor ORDER BY razao_social")
        produtos = conn.execute("""
            SELECT id_produto AS id, sku, nome_produto AS nome, tipo, preco, estoque_atual
            FROM produtos ORDER BY nome_produto
        """)
        clientes = conn.execute("SELECT id_cliente AS id, nome, cnpj FROM clientes ORDER BY nome")
        return jsonify({
            "categorias": [dict(row) for row in categorias],
            "fornecedores": [dict(row) for row in fornecedores],
            "produtos": [dict(row) for row in produtos],
            "clientes": [dict(row) for row in clientes],
        })
    finally:
        conn.close()


@bp.post("/produtos")
def criar_produto_api():
    dados = request.get_json(silent=True) or {}
    obrigatorios = ("sku", "nome", "fabricante", "tipo", "preco", "localizacao", "categoria_id", "fornecedor_id")
    if any(not str(dados.get(campo, "")).strip() for campo in obrigatorios):
        return erro("Preencha todos os campos obrigatórios.")
    try:
        preco = converter_centavos(dados["preco"]) / 100
        estoque = int(dados.get("estoque_atual", 0))
        minimo = int(dados.get("estoque_minimo", 0))
        categoria_id = int(dados["categoria_id"])
        fornecedor_id = int(dados["fornecedor_id"])
    except (ValueError, TypeError):
        return erro("Preço, estoques ou vínculos possuem valor inválido.")
    if preco <= 0 or estoque < 0 or minimo < 0:
        return erro("Preço deve ser positivo e estoques não podem ser negativos.")
    tipo = str(dados["tipo"]).strip()
    if tipo == "Periférico":
        tipo = "Periferico"
    if tipo not in {"Hardware", "Software", "Periferico"}:
        return erro("Tipo de produto inválido.")
    modalidade = str(dados.get("modalidade_licenca") or "").strip() or None
    if modalidade and modalidade not in {"Assinatura Anual", "Assinatura anual", "Perpétua/ESD", "OEM"}:
        return erro("Modalidade de licença inválida.")
    if tipo != "Software":
        modalidade = None
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO produtos
            (sku, nome_produto, fabricante, tipo, especificacao, modalidade, preco, estoque_atual,
             estoque_minimo, localizacao, id_categoria, id_fornecedor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(dados["sku"]).strip(), str(dados["nome"]).strip(), str(dados["fabricante"]).strip(),
            tipo, str(dados.get("especificacao") or "").strip(), modalidade, preco, estoque, minimo,
            str(dados["localizacao"]).strip(), categoria_id, fornecedor_id,
        ))
        conn.commit()
        return jsonify({"mensagem": "Produto cadastrado com sucesso."}), 201
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "sku" in str(exc).lower():
            return erro("Já existe um produto cadastrado com esse SKU.")
        return erro("Não foi possível cadastrar o produto: dados inválidos ou vínculos inexistentes.")
    finally:
        conn.close()


@bp.delete("/produtos/<int:id>")
def excluir_produto_api(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT 1 FROM produtos WHERE id_produto = ?", (id,)).fetchone():
            return erro("Produto não encontrado.", 404)
        try:
            conn.execute("DELETE FROM produtos WHERE id_produto = ?", (id,))
            conn.commit()
            return jsonify({"mensagem": "Produto descontinuado com sucesso."})
        except sqlite3.IntegrityError:
            conn.rollback()
            return erro("O produto não pode ser removido porque possui histórico ou licenças vinculadas.", 409)
    finally:
        conn.close()


@bp.get("/movimentacoes")
def listar_movimentacoes_api():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT m.id_movimentacao AS id, p.sku, p.nome_produto AS produto_nome, m.tipo,
                   m.quantidade, m.data_hora, m.observacao
            FROM movimentacoes m JOIN produtos p ON p.id_produto = m.id_produto
            ORDER BY m.data_hora DESC, m.id_movimentacao DESC
        """)
        resultado = [dict(row) for row in rows]
        return jsonify(resultado)
    finally:
        conn.close()


@bp.post("/movimentacoes")
def criar_movimentacao_api():
    dados = request.get_json(silent=True) or {}
    try:
        produto_id = inteiro_estrito(dados["produto_id"])
        quantidade = inteiro_estrito(dados["quantidade"])
    except (KeyError, TypeError, ValueError):
        return erro("Produto e quantidade devem ser válidos.")
    if quantidade <= 0 or dados.get("tipo") not in ("ENTRADA", "SAIDA"):
        return erro("Informe tipo de movimentação e quantidade positiva.")
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        produto = conn.execute(
            "SELECT estoque_atual, estoque_minimo, tipo FROM produtos WHERE id_produto = ?",
            (produto_id,),
        ).fetchone()
        if not produto:
            conn.rollback()
            return erro("Produto não encontrado.", 404)
        if produto["tipo"] == "Software":
            conn.rollback()
            return erro("Licença digital só movimenta por venda ou cadastro de chaves.", 409)
        incremento = quantidade if dados["tipo"] == "ENTRADA" else -quantidade
        cursor = conn.execute(
            "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id_produto = ? AND estoque_atual + ? >= 0",
            (incremento, produto_id, incremento),
        )
        if cursor.rowcount != 1:
            conn.rollback()
            return erro(f"Estoque insuficiente: disponível {produto['estoque_atual']}.", 409)
        conn.execute("""
            INSERT INTO movimentacoes (id_produto, id_usuario, tipo, quantidade, observacao)
            VALUES (?, ?, ?, ?, ?)
        """, (produto_id, session["id_usuario"], "ENTRADA" if incremento > 0 else "SAIDA",
              quantidade, dados.get("observacao") or None))
        conn.commit()
        saldo = conn.execute("SELECT estoque_atual, estoque_minimo FROM produtos WHERE id_produto = ?", (produto_id,)).fetchone()
        return jsonify({"mensagem": "Movimentação registrada.", "aviso_estoque": saldo["estoque_atual"] <= saldo["estoque_minimo"]}), 201
    except sqlite3.Error:
        conn.rollback()
        return erro("Não foi possível registrar a movimentação.", 500)
    finally:
        conn.close()


@bp.get("/clientes")
def listar_clientes_api():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id_cliente AS id, nome, cnpj, email FROM clientes ORDER BY nome")
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


@bp.post("/vendas")
def criar_venda_api():
    dados = request.get_json(silent=True) or {}
    try:
        cliente_id = inteiro_estrito(dados["id_cliente"])
        itens_recebidos = dados["itens"]
        if not isinstance(itens_recebidos, list) or not itens_recebidos:
            return erro("A venda precisa conter ao menos um item.")
        quantidades = {}
        for item in itens_recebidos:
            produto_id = inteiro_estrito(item["id_produto"])
            quantidade = inteiro_estrito(item["quantidade"])
            if quantidade <= 0:
                return erro("A quantidade de cada item deve ser maior que zero.")
            quantidades[produto_id] = quantidades.get(produto_id, 0) + quantidade
    except (KeyError, TypeError, ValueError):
        return erro("Informe cliente e itens válidos.")

    conn = get_db()
    try:
        # BEGIN IMMEDIATE serializa as vendas antes da leitura/baixa para impedir saldo negativo concorrente.
        conn.execute("BEGIN IMMEDIATE")
        if not conn.execute("SELECT 1 FROM clientes WHERE id_cliente = ?", (cliente_id,)).fetchone():
            conn.rollback()
            return erro("Cliente não encontrado.", 404)
        user_id = session.get("id_usuario")
        if not user_id:
            conn.rollback()
            return erro("Sessão sem usuário autenticado.", 401)
        numero_pedido = "TS-" + uuid.uuid4().hex[:12].upper()
        cursor = conn.execute(
            "INSERT INTO vendas (numero_pedido, id_cliente, id_usuario) VALUES (?, ?, ?)",
            (numero_pedido, cliente_id, user_id),
        )
        venda_id = cursor.lastrowid
        total_centavos = 0
        for produto_id, quantidade in quantidades.items():
            produto = conn.execute(
                "SELECT sku, nome_produto, preco FROM produtos WHERE id_produto = ?",
                (produto_id,),
            ).fetchone()
            if not produto:
                raise ValueError(f"Produto {produto_id} não encontrado.")
            saldo = conn.execute("SELECT estoque_atual FROM produtos WHERE id_produto = ?", (produto_id,)).fetchone()[0]
            cursor = conn.execute("""
                UPDATE produtos SET estoque_atual = estoque_atual - ?
                WHERE id_produto = ? AND estoque_atual >= ?
            """, (quantidade, produto_id, quantidade))
            if cursor.rowcount != 1:
                raise EstoqueInsuficiente(
                    f"Estoque insuficiente para {produto['nome_produto']}: disponível {saldo}"
                )
            tipo_produto = conn.execute("SELECT tipo FROM produtos WHERE id_produto = ?", (produto_id,)).fetchone()["tipo"]
            if tipo_produto == "Software":
                licencas = conn.execute("""
                    SELECT id_licenca FROM ativos_digitais
                    WHERE id_produto = ? AND id_venda IS NULL ORDER BY id_licenca LIMIT ?
                """, (produto_id, quantidade)).fetchall()
                if len(licencas) < quantidade:
                    disponiveis = len(licencas)
                    raise EstoqueInsuficiente(
                        f"Estoque insuficiente para {produto['nome_produto']}: disponíveis {disponiveis} licença(s)"
                    )
                conn.executemany(
                    "UPDATE ativos_digitais SET id_venda = ? WHERE id_licenca = ?",
                    [(venda_id, licenca["id_licenca"]) for licenca in licencas],
                )
            preco_centavos = converter_centavos(Decimal(str(produto["preco"])))
            subtotal_centavos = quantidade * preco_centavos
            conn.execute("""
                INSERT INTO itens_venda
                (id_venda, id_produto, quantidade, preco_unitario_centavos, subtotal_centavos)
                VALUES (?, ?, ?, ?, ?)
            """, (venda_id, produto_id, quantidade, preco_centavos, subtotal_centavos))
            conn.execute("""
                INSERT INTO movimentacoes (id_produto, id_venda, id_usuario, tipo, quantidade, observacao)
                VALUES (?, ?, ?, 'SAIDA', ?, ?)
            """, (produto_id, venda_id, user_id, quantidade, f"Venda {numero_pedido}"))
            total_centavos += subtotal_centavos
        conn.execute(
            "UPDATE vendas SET valor_total_centavos = ? WHERE id_venda = ?",
            (total_centavos, venda_id),
        )
        conn.commit()
        return jsonify({"id_venda": venda_id, "numero_pedido": numero_pedido, "valor_total_centavos": total_centavos}), 201
    except EstoqueInsuficiente as exc:
        conn.rollback()
        return erro(str(exc), 409)
    except ValueError as exc:
        conn.rollback()
        return erro(str(exc), 400)
    except sqlite3.Error:
        conn.rollback()
        return erro("Falha no banco de dados; a venda foi revertida integralmente.", 500)
    except Exception:
        conn.rollback()
        return erro("Falha inesperada; a venda foi revertida integralmente.", 500)
    finally:
        conn.close()


def _dados_recibo(conn, venda_id):
    venda = conn.execute("""
        SELECT v.id_venda, v.id_usuario, v.numero_pedido, v.data_venda, v.valor_total_centavos,
               c.nome AS cliente_nome, c.cnpj AS cliente_cnpj, c.email AS cliente_email,
               u.nome AS operador, u.email AS operador_email
        FROM vendas v JOIN clientes c ON c.id_cliente = v.id_cliente
        JOIN usuarios u ON u.id_usuario = v.id_usuario
        WHERE v.id_venda = ?
    """, (venda_id,)).fetchone()
    if not venda:
        return None
    itens = conn.execute("""
        SELECT p.sku, p.nome_produto AS produto, i.quantidade,
               i.preco_unitario_centavos, i.subtotal_centavos
        FROM itens_venda i JOIN produtos p ON p.id_produto = i.id_produto
        WHERE i.id_venda = ? ORDER BY i.id_item
    """, (venda_id,)).fetchall()
    result = dict(venda)
    result["itens"] = [dict(item) for item in itens]
    return result


@bp.get("/vendas/<int:id>/recibo")
def recibo_venda_api(id):
    conn = get_db()
    try:
        recibo = _dados_recibo(conn, id)
        if not recibo:
            return erro("Venda não encontrada.", 404)
        if session["perfil"] != "GERENTE" and recibo["id_usuario"] != session["id_usuario"]:
            return erro("Você não pode consultar o recibo desta venda.", 403)
        return jsonify(recibo)
    finally:
        conn.close()


@bp.get("/vendas/<int:id>/recibo/imprimir")
def recibo_venda_html(id):
    conn = get_db()
    try:
        recibo = _dados_recibo(conn, id)
        if not recibo:
            return "Venda não encontrada.", 404
        if session["perfil"] != "GERENTE" and recibo["id_usuario"] != session["id_usuario"]:
            return "Você não pode consultar o recibo desta venda.", 403
        return render_template("recibo.html", recibo=recibo)
    finally:
        conn.close()


@bp.get("/livro-razao")
def livro_razao_api():
    conn = get_db()
    try:
        venda_id = request.args.get("venda", type=int)
        consulta = """
            SELECT m.id_movimentacao AS id, m.data_hora, m.tipo, m.quantidade, m.observacao,
                   p.sku, p.nome_produto AS produto, v.numero_pedido, v.id_venda,
                   c.nome AS cliente, c.cnpj, u.nome AS usuario, u.perfil
            FROM movimentacoes m
            JOIN produtos p ON p.id_produto = m.id_produto
            LEFT JOIN vendas v ON v.id_venda = m.id_venda
            LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
            LEFT JOIN usuarios u ON u.id_usuario = m.id_usuario
        """
        rows = conn.execute(consulta + (" WHERE m.id_venda = ?" if venda_id else "") +
                            " ORDER BY m.data_hora DESC, m.id_movimentacao DESC",
                            (venda_id,) if venda_id else ())
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


@bp.patch("/usuarios/<int:id>/perfil")
def atualizar_perfil_api(id):
    dados = request.get_json(silent=True) or {}
    perfil = str(dados.get("perfil", "")).upper()
    if perfil not in {"GERENTE", "OPERADOR"}:
        return erro("Perfil deve ser GERENTE ou OPERADOR.")
    if id == session["id_usuario"] and perfil != "GERENTE":
        return erro("Você não pode rebaixar o próprio perfil.", 409)
    conn = get_db()
    try:
        cursor = conn.execute("UPDATE usuarios SET perfil = ? WHERE id_usuario = ?", (perfil, id))
        if cursor.rowcount != 1:
            conn.rollback()
            return erro("Usuário não encontrado.", 404)
        conn.commit()
        return jsonify({"mensagem": "Perfil atualizado.", "perfil": perfil})
    except sqlite3.Error:
        conn.rollback()
        return erro("Não foi possível atualizar o perfil.", 500)
    finally:
        conn.close()
