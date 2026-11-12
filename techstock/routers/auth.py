import re
import sqlite3

from flask import Blueprint, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _usuario_publico(usuario):
    return {
        "id": usuario["id_usuario"],
        "nome": usuario["nome_completo"],
        "email": usuario["email"],
        "perfil": usuario["perfil_acesso"],
    }


@bp.post("/registrar")
def registrar():
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip().lower()
    senha = dados.get("senha", "")

    if not nome or len(nome) > 100:
        return jsonify({"erro": "Informe um nome válido com até 100 caracteres."}), 400
    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"erro": "Informe um e-mail válido."}), 400
    if not isinstance(senha, str) or len(senha) < 8 or len(senha) > 128:
        return jsonify({"erro": "A senha deve ter entre 8 e 128 caracteres."}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO usuarios "
            "(nome_completo, email, senha_hash, perfil_acesso, status) "
            "VALUES (?, ?, ?, 'OPERADOR', 'ATIVO')",
            (nome, email, generate_password_hash(senha)),
        )
        conn.commit()
        return jsonify({"mensagem": "Usuário registrado com perfil OPERADOR."}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"erro": "Já existe um usuário registrado com esse e-mail."}), 409
    finally:
        conn.close()


@bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = str(dados.get("email", "")).strip().lower()
    senha = dados.get("senha", "")
    if not email or not isinstance(senha, str):
        return jsonify({"erro": "E-mail ou senha inválidos."}), 401

    conn = get_db()
    try:
        usuario = conn.execute(
            "SELECT id_usuario, nome_completo, email, senha_hash, perfil_acesso, status "
            "FROM usuarios WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if (
        not usuario
        or usuario["status"] != "ATIVO"
        or not check_password_hash(usuario["senha_hash"], senha)
    ):
        return jsonify({"erro": "E-mail ou senha inválidos."}), 401

    session.clear()
    session["usuario_id"] = usuario["id_usuario"]
    return jsonify({"usuario": _usuario_publico(usuario)})


@bp.get("/me")
def me():
    return jsonify({"usuario": g.usuario})


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})
