from flask import Blueprint, render_template
from db import get_db

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def dashboard():
    conn = get_db()
    try:
        produtos = conn.execute("""
            SELECT p.id_produto AS id, p.sku, p.nome_produto AS nome, p.fabricante, p.tipo,
                   c.nome_categoria AS categoria, f.razao_social AS fornecedor, p.preco,
                   p.estoque_atual, p.estoque_minimo, p.localizacao, p.modalidade AS modalidade_licenca
            FROM produtos p
            INNER JOIN categoria c ON c.id_categoria = p.id_categoria
            INNER JOIN fornecedor f ON f.id_fornecedor = p.id_fornecedor
            ORDER BY p.nome_produto
        """).fetchall()
        return render_template("index.html", produtos=produtos)
    finally:
        conn.close()
