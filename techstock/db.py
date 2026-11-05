import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "techstock.db")


def get_db():
    """Abre uma conexão SQLite com chaves estrangeiras obrigatórias."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Recria o banco usando o script SQL fornecido pelo projeto."""
    conn = get_db()
    try:
        with open(os.path.join(BASE_DIR, "database.sql"), "r", encoding="utf-8") as arquivo:
            conn.executescript(arquivo.read())
        conn.commit()
    finally:
        conn.close()


def ensure_database():
    """Inicializa ou migra o banco para o modelo SQLite fornecido."""
    precisa_inicializar = not os.path.exists(DATABASE)
    if not precisa_inicializar:
        conn = get_db()
        try:
            tabelas = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            nomes = {tabela["name"] for tabela in tabelas}
            precisa_inicializar = "categoria" not in nomes or "produtos" not in nomes
        finally:
            conn.close()
    if precisa_inicializar:
        init_db()
