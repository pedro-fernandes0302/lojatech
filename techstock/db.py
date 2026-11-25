import os
import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get("TECHSTOCK_DATABASE", os.path.join(BASE_DIR, "techstock.db"))
EXPECTED_TABLES = {
    "usuarios", "categoria", "fornecedor", "produtos", "movimentacoes",
    "ativos_digitais", "clientes", "vendas", "itens_venda",
}
EXPECTED_TRIGGERS = {
    "movimentacoes_sem_update", "movimentacoes_sem_delete",
    "itens_venda_sem_update", "itens_venda_sem_delete",
    "vendas_sem_delete", "vendas_total_imutavel",
}


def get_db():
    """Abre uma conexão SQLite com chaves estrangeiras obrigatórias."""
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def seed_usuarios(conn):
    """Mantém as contas de demonstração fora do SQL para armazenar só hashes."""
    usuarios = (
        ("Gerente TechStore", "gerente@techstore.com", "demo-techstore-2026", "GERENTE"),
        ("Operador TechStore", "operador@techstore.com", "operador-techstore-2026", "OPERADOR"),
    )
    for nome, email, senha, perfil in usuarios:
        conn.execute(
            """INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil)
               VALUES (?, ?, ?, ?)""",
            (nome, email, generate_password_hash(senha), perfil),
        )


def init_db():
    """Cria o esquema e os dados de demonstração em banco vazio."""
    conn = get_db()
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        # A versão antiga materializava este saldo; removemos só a tabela derivada antes de criar a VIEW.
        tipo_estoque = conn.execute(
            "SELECT type FROM sqlite_master WHERE name = 'estoque_fisico'"
        ).fetchone()
        if tipo_estoque and tipo_estoque["type"] == "table":
            conn.execute("DROP TABLE estoque_fisico")
        script = Path(BASE_DIR, "database.sql").read_text(encoding="utf-8-sig")
        conn.executescript("BEGIN IMMEDIATE;\n" + script)
        seed_usuarios(conn)
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_database():
    """Recria o esquema de demonstração quando qualquer objeto obrigatório falta."""
    if not os.path.exists(DATABASE):
        init_db()
        return
    conn = get_db()
    try:
        tabelas = {
            row["name"] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
        triggers = {
            row["name"] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        precisa_inicializar = (
            not EXPECTED_TABLES.issubset(tabelas)
            or "estoque_fisico" not in tabelas
            or not EXPECTED_TRIGGERS.issubset(triggers)
        )
    finally:
        conn.close()
    if precisa_inicializar:
        if EXPECTED_TABLES & tabelas:
            raise RuntimeError(
                "Banco existente está incompleto. Para evitar perda de dados, nada foi apagado; "
                "faça backup e remova o arquivo do banco para recriá-lo do zero."
            )
        init_db()
    else:
        conn = get_db()
        try:
            seed_usuarios(conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
