import sqlite3
from flask import Blueprint, abort, flash, redirect, url_for
from db import get_db

bp = Blueprint("excluir_fornecedor", __name__)


@bp.route("/fornecedores/<int:id>/excluir", methods=["POST"])
def excluir_fornecedor(id):
    conn = get_db()
    try:
        if not conn.execute("SELECT id_fornecedor FROM fornecedor WHERE id_fornecedor = ?", (id,)).fetchone():
            abort(404)
        try:
            conn.execute("DELETE FROM fornecedor WHERE id_fornecedor = ?", (id,))
            conn.commit()
            flash("Fornecedor excluído com sucesso.", "success")
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Não é possível excluir este fornecedor: existem produtos vinculados a ele.", "danger")
        return redirect(url_for("fornecedores.fornecedores"))
    finally:
        conn.close()
