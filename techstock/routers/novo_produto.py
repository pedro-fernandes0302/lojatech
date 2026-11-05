import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_db
from routers.utils import converter_preco, validar_categoria_produto

bp = Blueprint("novo_produto", __name__)


@bp.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    conn = get_db()
    try:
        categorias = conn.execute("SELECT id_categoria AS id, nome_categoria AS nome FROM categoria ORDER BY nome_categoria").fetchall()
        fornecedores = conn.execute("SELECT id_fornecedor AS id, razao_social FROM fornecedor ORDER BY razao_social").fetchall()
        campos = ("sku", "nome", "fabricante", "tipo", "especificacao", "modalidade_licenca",
                  "preco", "estoque_atual", "estoque_minimo", "localizacao", "categoria_id", "fornecedor_id")
        dados = {campo: request.form.get(campo, "") for campo in campos}
        if request.method == "GET":
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados)

        obrigatorios = ("sku", "nome", "fabricante", "tipo", "preco", "localizacao", "categoria_id", "fornecedor_id")
        if any(not str(dados[campo]).strip() for campo in obrigatorios):
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados), 400
        if not validar_categoria_produto(dados["tipo"], dados["modalidade_licenca"]):
            flash("Tipo ou modalidade de licença inválido.", "danger")
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados), 400
        try:
            preco = converter_preco(dados["preco"])
            estoque = int(dados["estoque_atual"] or 0)
            minimo = int(dados["estoque_minimo"] or 0)
        except (ValueError, TypeError):
            flash("Preço ou estoques possuem valor inválido.", "danger")
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados), 400
        if preco <= 0:
            flash("O preço deve ser maior que zero.", "danger")
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados), 400
        if estoque < 0 or minimo < 0:
            flash("Os estoques atual e mínimo não podem ser negativos.", "danger")
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados), 400

        try:
            conn.execute("""
                INSERT INTO produtos
                (sku, nome_produto, fabricante, tipo, especificacao, modalidade, preco,
                 estoque_atual, estoque_minimo, localizacao, id_categoria, id_fornecedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (dados["sku"].strip(), dados["nome"].strip(), dados["fabricante"].strip(), dados["tipo"],
                  dados["especificacao"].strip() or None, dados["modalidade_licenca"] or None, preco, estoque,
                  minimo, dados["localizacao"].strip(), dados["categoria_id"], dados["fornecedor_id"]))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Não foi possível cadastrar: SKU já existente ou categoria/fornecedor inválido.", "danger")
            return render_template("produto_form.html", categorias=categorias, fornecedores=fornecedores, dados=dados), 400
        flash("Produto cadastrado com sucesso.", "success")
        return redirect(url_for("dashboard.dashboard"))
    finally:
        conn.close()
