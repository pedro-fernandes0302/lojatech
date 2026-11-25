import sqlite3
from flask import Blueprint, abort, flash, make_response, redirect, url_for
from db import get_db

bp = Blueprint("excluir_produto", __name__)


@bp.route("/produtos/<int:id>/excluir", methods=["POST"])
def excluir_produto(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT id_produto FROM produtos WHERE id_produto = ?", (id,)).fetchone():
            abort(404)
        try:
            conn.execute("DELETE FROM produtos WHERE id_produto = ?", (id,))
            conn.commit()
            flash("Produto descontinuado com sucesso.", "success")
        except sqlite3.IntegrityError:
            conn.rollback()
            return make_response("O produto não pode ser excluído: há histórico, itens de venda ou licenças vinculadas.", 409)
        return redirect(url_for("dashboard.dashboard"))
    finally:
        conn.close()
