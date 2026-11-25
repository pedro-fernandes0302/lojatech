import sqlite3

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

bp = Blueprint("auth", __name__)


def autenticar(email, senha):
    conn = get_db()
    try:
        usuario = conn.execute(
            "SELECT id_usuario, nome, email, senha_hash, perfil FROM usuarios WHERE email = ? COLLATE NOCASE",
            (email.strip(),),
        ).fetchone()
    finally:
        conn.close()
    if not usuario or not check_password_hash(usuario["senha_hash"], senha):
        return None
    session.clear()
    session.update(
        id_usuario=usuario["id_usuario"],
        nome=usuario["nome"],
        email=usuario["email"],
        perfil=usuario["perfil"],
    )
    return usuario


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", erro=None)
    if not autenticar(request.form.get("email", ""), request.form.get("senha", "")):
        return render_template("login.html", erro="E-mail ou senha inválidos."), 401
    proxima = request.args.get("proxima", "")
    if not proxima.startswith("/") or proxima.startswith("//"):
        proxima = url_for("dashboard.dashboard")
    return redirect(proxima)


@bp.post("/api/login")
def login_api():
    dados = request.get_json(silent=True) or {}
    usuario = autenticar(str(dados.get("email", "")), str(dados.get("senha", "")))
    if not usuario:
        return jsonify({"erro": "E-mail ou senha inválidos."}), 401
    return jsonify({"id_usuario": usuario["id_usuario"], "nome": usuario["nome"], "perfil": usuario["perfil"]})


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html", erro=None)
    nome, email, senha = (request.form.get(chave, "").strip() for chave in ("nome", "email", "senha"))
    resposta = criar_operador(nome, email, senha)
    if isinstance(resposta, str):
        return render_template("cadastro.html", erro=resposta), 400
    autenticar(email, senha)
    return redirect(url_for("dashboard.dashboard"))


@bp.post("/api/cadastro")
def cadastro_api():
    dados = request.get_json(silent=True) or {}
    resposta = criar_operador(
        str(dados.get("nome", "")).strip(),
        str(dados.get("email", "")).strip(),
        str(dados.get("senha", "")),
    )
    if isinstance(resposta, str):
        return jsonify({"erro": resposta}), 400
    return jsonify({"mensagem": "Cadastro realizado com perfil OPERADOR."}), 201


def criar_operador(nome, email, senha):
    if not nome or "@" not in email or len(senha) < 8:
        return "Informe nome, e-mail válido e senha com pelo menos 8 caracteres."
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, 'OPERADOR')",
            (nome, email, generate_password_hash(senha)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return "Este e-mail já está cadastrado."
    finally:
        conn.close()


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.post("/api/logout")
def logout_api():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})
