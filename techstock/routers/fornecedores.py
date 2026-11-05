import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_db
from routers.utils import normalizar_cnpj

bp = Blueprint("fornecedores", __name__)


@bp.route("/fornecedores", methods=["GET", "POST"])
def fornecedores():
    conn = get_db()
    try:
        if request.method == "POST":
            razao_social = request.form.get("razao_social", "").strip()
            cnpj = normalizar_cnpj(request.form.get("cnpj", ""))
            telefone = request.form.get("telefone", "").strip()
            email = request.form.get("email", "").strip()
            if not razao_social or len(cnpj) != 14:
                flash("Informe a razão social e um CNPJ válido com 14 dígitos.", "danger")
            else:
                try:
                    conn.execute("INSERT INTO fornecedor (razao_social, cnpj, telefone, email) VALUES (?, ?, ?, ?)",
                                 (razao_social, cnpj, telefone or None, email or None))
                    conn.commit()
                    flash("Fornecedor cadastrado com sucesso.", "success")
                    return redirect(url_for("fornecedores.fornecedores"))
                except sqlite3.IntegrityError:
                    conn.rollback()
                    flash("Já existe um fornecedor cadastrado com esse CNPJ.", "danger")
        lista = conn.execute("SELECT id_fornecedor AS id, razao_social, cnpj, telefone, email FROM fornecedor ORDER BY razao_social").fetchall()
        return render_template("fornecedores.html", fornecedores=lista)
    finally:
        conn.close()
