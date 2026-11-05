import sqlite3
from flask import Blueprint, abort, jsonify, request
from db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")


def erro(mensagem, codigo=400):
    return jsonify({"erro": mensagem}), codigo


@bp.get("/dashboard")
def dashboard_api():
    conn = get_db()
    try:
        produtos = conn.execute("""
            SELECT p.id_produto AS id, p.sku, p.nome_produto AS nome, p.fabricante, p.tipo,
                   c.nome_categoria AS categoria, f.razao_social AS fornecedor, p.preco,
                   p.estoque_atual, p.estoque_minimo, p.localizacao, p.modalidade AS modalidade_licenca
            FROM produtos p INNER JOIN categoria c ON c.id_categoria = p.id_categoria
            INNER JOIN fornecedor f ON f.id_fornecedor = p.id_fornecedor ORDER BY p.nome_produto
        """).fetchall()
        return jsonify({
            "produtos": [dict(p) for p in produtos],
            "categorias": conn.execute("SELECT COUNT(*) FROM categoria").fetchone()[0],
                        "fornecedores": conn.execute("SELECT COUNT(*) FROM fornecedor").fetchone()[0],
        })
    finally:
        conn.close()


@bp.get("/categorias")
def listar_categorias_api():
    conn = get_db()
    try:
        return jsonify([{"id": r["id_categoria"], "nome": r["nome_categoria"]} for r in conn.execute("SELECT id_categoria, nome_categoria FROM categoria ORDER BY nome_categoria")])
    finally:
        conn.close()


@bp.post("/categorias")
def criar_categoria_api():
    nome = request.get_json(silent=True) or {}
    nome = str(nome.get("nome", "")).strip()
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
        if not conn.execute("SELECT id_categoria FROM categoria WHERE id_categoria = ?", (id,)).fetchone():
            return erro("Categoria não encontrada.", 404)
        try:
            conn.execute("DELETE FROM categoria WHERE id_categoria = ?", (id,))
            conn.commit()
            return jsonify({"mensagem": "Categoria excluída com sucesso."})
        except sqlite3.IntegrityError:
            conn.rollback()
            return erro("Não é possível excluir esta categoria: existem ativos vinculados a ela.")
    finally:
        conn.close()


@bp.get("/fornecedores")
def listar_fornecedores_api():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id_fornecedor AS id, razao_social, cnpj, telefone, email FROM fornecedor ORDER BY razao_social")
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@bp.post("/fornecedores")
def criar_fornecedor_api():
    dados = request.get_json(silent=True) or {}
    razao = str(dados.get("razao_social", "")).strip()
    cnpj = "".join(c for c in str(dados.get("cnpj", "")) if c.isdigit())
    if not razao or len(cnpj) != 14:
        return erro("Informe a razão social e um CNPJ válido com 14 dígitos.")
    conn = get_db()
    try:
        conn.execute("INSERT INTO fornecedor (razao_social, cnpj, telefone, email) VALUES (?, ?, ?, ?)",
                     (razao, cnpj, dados.get("telefone") or None, dados.get("email") or None))
        conn.commit()
        return jsonify({"mensagem": "Fornecedor cadastrado com sucesso."}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return erro("Já existe um fornecedor cadastrado com esse CNPJ.")
    finally:
        conn.close()


@bp.delete("/fornecedores/<int:id>")
def excluir_fornecedor_api(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT id_fornecedor FROM fornecedor WHERE id_fornecedor = ?", (id,)).fetchone():
            return erro("Fornecedor não encontrado.", 404)
        try:
            conn.execute("DELETE FROM fornecedor WHERE id_fornecedor = ?", (id,))
            conn.commit()
            return jsonify({"mensagem": "Fornecedor excluído com sucesso."})
        except sqlite3.IntegrityError:
            conn.rollback()
            return erro("Não é possível excluir este fornecedor: existem produtos vinculados a ele.")
    finally:
        conn.close()


@bp.get("/produtos/opcoes")
def opcoes_produto_api():
    conn = get_db()
    try:
        categorias = conn.execute("SELECT id_categoria AS id, nome_categoria AS nome FROM categoria ORDER BY nome_categoria")
        fornecedores = conn.execute("SELECT id_fornecedor AS id, razao_social FROM fornecedor ORDER BY razao_social")
        produtos = conn.execute("SELECT id_produto AS id, sku, nome_produto AS nome, estoque_atual FROM produtos ORDER BY nome_produto")
        return jsonify({"categorias": [dict(r) for r in categorias], "fornecedores": [dict(r) for r in fornecedores], "produtos": [dict(r) for r in produtos]})
    finally:
        conn.close()


@bp.post("/produtos")
def criar_produto_api():
    d = request.get_json(silent=True) or {}
    obrigatorios = ("sku", "nome", "fabricante", "tipo", "preco", "localizacao", "categoria_id", "fornecedor_id")
    if any(not str(d.get(c, "")).strip() for c in obrigatorios):
        return erro("Preencha todos os campos obrigatórios.")
    try:
        preco = float(str(d["preco"]).replace(".", "").replace(",", "."))
        estoque = int(d.get("estoque_atual", 0))
        minimo = int(d.get("estoque_minimo", 0))
    except (ValueError, TypeError):
        return erro("Preço ou estoques possuem valor inválido.")
    if preco <= 0 or estoque < 0 or minimo < 0:
        return erro("Preço deve ser positivo e estoques não podem ser negativos.")
    conn = get_db()
    try:
        conn.execute("""INSERT INTO produtos (sku,nome_produto,fabricante,tipo,especificacao,modalidade,preco,
                       estoque_atual,estoque_minimo,localizacao,id_categoria,id_fornecedor)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (d["sku"].strip(), d["nome"].strip(), d["fabricante"].strip(), d["tipo"],
                      d.get("especificacao") or None, d.get("modalidade_licenca") or None, preco,
                      estoque, minimo, d["localizacao"].strip(), d["categoria_id"], d["fornecedor_id"]))
        conn.commit()
        return jsonify({"mensagem": "Produto cadastrado com sucesso."}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return erro("Não foi possível cadastrar: SKU já existente ou categoria/fornecedor inválido.")
    finally:
        conn.close()


@bp.delete("/produtos/<int:id>")
def excluir_produto_api(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT id_produto FROM produtos WHERE id_produto = ?", (id,)).fetchone():
            return erro("Produto não encontrado.", 404)
        try:
            conn.execute("DELETE FROM produtos WHERE id_produto = ?", (id,))
            conn.commit()
            return jsonify({"mensagem": "Produto descontinuado com sucesso."})
        except sqlite3.IntegrityError:
            conn.rollback()
            return erro("O item não pode ser removido pois possui histórico de movimentações.")
    finally:
        conn.close()


@bp.get("/movimentacoes")
def listar_movimentacoes_api():
    conn = get_db()
    try:
        rows = conn.execute("""SELECT m.id_movimentacao AS id,p.sku,p.nome_produto AS produto_nome,m.tipo,m.quantidade,m.data_hora,m.observacao
                               FROM movimentacoes m INNER JOIN produtos p ON p.id_produto=m.id_produto
                               ORDER BY m.data_hora DESC, m.id_movimentacao DESC""")
        resultado=[]
        for r in rows:
            item=dict(r)
            item["tipo"] = "ENTRADA" if item["tipo"] == "Entrada" else "SAIDA"
            resultado.append(item)
        return jsonify(resultado)
    finally:
        conn.close()


@bp.post("/movimentacoes")
def criar_movimentacao_api():
    d = request.get_json(silent=True) or {}
    try:
        produto_id, quantidade = int(d["produto_id"]), int(d["quantidade"])
    except (KeyError, TypeError, ValueError):
        return erro("Produto e quantidade devem ser válidos.")
    if quantidade <= 0:
        return erro("A quantidade deve ser um número inteiro maior que zero.")
    if d.get("tipo") not in ("ENTRADA", "SAIDA"):
        return erro("Tipo de movimentação inválido.")
    conn = get_db()
    try:
        produto = conn.execute("SELECT estoque_atual,estoque_minimo FROM produtos WHERE id_produto=?", (produto_id,)).fetchone()
        if not produto:
            return erro("Produto não encontrado.", 404)
        if d["tipo"] == "SAIDA" and quantidade > produto["estoque_atual"]:
            return erro(f"Estoque insuficiente: saldo atual {produto['estoque_atual']}, solicitado {quantidade}")
        incremento = quantidade if d["tipo"] == "ENTRADA" else -quantidade
        conn.execute("UPDATE produtos SET estoque_atual=estoque_atual+? WHERE id_produto=?", (incremento, produto_id))
        tipo_banco = "Entrada" if d["tipo"] == "ENTRADA" else "Saida"
        conn.execute("INSERT INTO movimentacoes (id_produto,tipo,quantidade,observacao) VALUES (?, ?, ?, ?)",
                     (produto_id, tipo_banco, quantidade, d.get("observacao") or None))
        conn.commit()
        novo = conn.execute("SELECT estoque_atual,estoque_minimo FROM produtos WHERE id_produto=?", (produto_id,)).fetchone()
        aviso = novo["estoque_atual"] <= novo["estoque_minimo"]
        return jsonify({"mensagem": "Movimentação registrada com sucesso.", "aviso_estoque": aviso}), 201
    except sqlite3.Error:
        conn.rollback()
        return erro("Não foi possível registrar a movimentação.")
    finally:
        conn.close()
