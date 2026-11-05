import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_db

bp = Blueprint("nova_movimentacao", __name__)


@bp.route("/movimentacoes/nova", methods=["GET", "POST"])
def nova_movimentacao():
    conn = get_db()
    try:
        produtos = conn.execute("SELECT id_produto AS id, sku, nome_produto AS nome, estoque_atual FROM produtos ORDER BY nome").fetchall()
        if request.method == "GET":
            return render_template("movimentacao_form.html", produtos=produtos, dados={})
        dados = {campo: request.form.get(campo, "") for campo in ("produto_id", "tipo", "quantidade", "observacao")}
        try:
            produto_id = int(dados["produto_id"])
            quantidade = int(dados["quantidade"])
        except (TypeError, ValueError):
            flash("Produto e quantidade devem ser válidos.", "danger")
            return render_template("movimentacao_form.html", produtos=produtos, dados=dados), 400
        if quantidade <= 0:
            flash("A quantidade deve ser um número inteiro maior que zero.", "danger")
            return render_template("movimentacao_form.html", produtos=produtos, dados=dados), 400
        if dados["tipo"] not in ("ENTRADA", "SAIDA"):
            flash("Tipo de movimentação inválido.", "danger")
            return render_template("movimentacao_form.html", produtos=produtos, dados=dados), 400

        produto = conn.execute("SELECT estoque_atual, estoque_minimo FROM produtos WHERE id_produto = ?", (produto_id,)).fetchone()
        if not produto:
            flash("Produto não encontrado.", "danger")
            return render_template("movimentacao_form.html", produtos=produtos, dados=dados), 404
        if dados["tipo"] == "SAIDA" and quantidade > produto["estoque_atual"]:
            conn.rollback()
            flash(f"Estoque insuficiente: saldo atual {produto['estoque_atual']}, solicitado {quantidade}", "danger")
            return render_template("movimentacao_form.html", produtos=produtos, dados=dados), 400
        try:
            incremento = quantidade if dados["tipo"] == "ENTRADA" else -quantidade
            conn.execute("UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id_produto = ?", (incremento, produto_id))
            conn.execute("INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao) VALUES (?, ?, ?, ?)",
                         (produto_id, "Entrada" if dados["tipo"] == "ENTRADA" else "Saida", quantidade, dados["observacao"].strip() or None))
            conn.commit()
            novo_saldo = conn.execute("SELECT estoque_atual, estoque_minimo FROM produtos WHERE id_produto = ?", (produto_id,)).fetchone()
            if novo_saldo["estoque_atual"] <= novo_saldo["estoque_minimo"]:
                flash("Movimentação registrada. Atenção: o novo saldo atingiu o nível mínimo e precisa ser reposto.", "warning")
            else:
                flash("Movimentação registrada com sucesso.", "success")
            return redirect(url_for("historico_movimentacoes.historico_movimentacoes"))
        except (sqlite3.Error, ValueError):
            conn.rollback()
            flash("Não foi possível registrar a movimentação. Verifique os dados e tente novamente.", "danger")
            return render_template("movimentacao_form.html", produtos=produtos, dados=dados), 400
    finally:
        conn.close()
