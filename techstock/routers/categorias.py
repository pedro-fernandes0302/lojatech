import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_db

bp = Blueprint("categorias", __name__)


@bp.route("/categorias", methods=["GET", "POST"])
def categorias():
    conn = get_db()
    try:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            if not nome:
                flash("Informe o nome da categoria.", "danger")
            else:
                try:
                    conn.execute("INSERT INTO categoria (nome_categoria, descricao) VALUES (?, '')", (nome,))
                    conn.commit()
                    flash("Categoria cadastrada com sucesso.", "success")
                    return redirect(url_for("categorias.categorias"))
                except sqlite3.IntegrityError:
                    conn.rollback()
                    flash("Já existe uma categoria com esse nome.", "danger")
        lista = conn.execute("SELECT id_categoria AS id, nome_categoria AS nome FROM categoria ORDER BY nome_categoria").fetchall()
        return render_template("categorias.html", categorias=lista)
    finally:
        conn.close()
