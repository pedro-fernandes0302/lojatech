from flask import Blueprint, render_template
from db import get_db

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def dashboard():
    conn = get_db()
    try:
        produtos = conn.execute("""
            SELECT p.id_produto AS id, p.sku, p.nome_produto AS nome, p.fabricante, p.tipo,
                   CASE WHEN p.tipo = 'Software' THEN 'Licença Digital' ELSE 'Hardware Físico' END AS tipo_catalogo,
                   c.nome_categoria AS categoria, f.razao_social AS fornecedor, p.preco,
                   p.estoque_atual, p.estoque_minimo, p.localizacao, p.modalidade AS modalidade_licenca,
                   COALESCE(ef.quantidade, 0) AS quantidade_fisica,
                   COALESCE(ad.chaves_disponiveis, 0) AS chaves_disponiveis
            FROM produtos p
            INNER JOIN categoria c ON c.id_categoria = p.id_categoria
            INNER JOIN fornecedor f ON f.id_fornecedor = p.id_fornecedor
            LEFT JOIN estoque_fisico ef ON ef.id_produto = p.id_produto
            LEFT JOIN (
                SELECT id_produto, COUNT(*) AS chaves_disponiveis
                FROM ativos_digitais WHERE id_venda IS NULL GROUP BY id_produto
            ) ad ON ad.id_produto = p.id_produto
            ORDER BY p.nome_produto
        """).fetchall()
        return render_template("index.html", produtos=produtos)
    finally:
        conn.close()
