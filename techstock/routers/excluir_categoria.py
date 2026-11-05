import sqlite3
from flask import Blueprint, abort, flash, redirect, url_for
from db import get_db

bp = Blueprint("excluir_categoria", __name__)


@bp.route("/categorias/<int:id>/excluir", methods=["POST"])
def excluir_categoria(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT id_categoria FROM categoria WHERE id_categoria = ?", (id,)).fetchone():
            abort(404)
        try:
            conn.execute("DELETE FROM categoria WHERE id_categoria = ?", (id,))
            conn.commit()
            flash("Categoria excluída com sucesso.", "success")
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Não é possível excluir esta categoria: existem ativos vinculados a ela.", "danger")
        return redirect(url_for("categorias.categorias"))
    finally:
        conn.close()
