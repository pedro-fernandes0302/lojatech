from db import get_db
from werkzeug.security import check_password_hash

def validar_login(email, senha):
    conn = get_db()
    try:
        usuario = conn.execute(
            "SELECT senha_hash, status FROM usuarios WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
        return bool(
            usuario
            and usuario["status"] == "ATIVO"
            and check_password_hash(usuario["senha_hash"], senha)
        )
    finally:
        conn.close()