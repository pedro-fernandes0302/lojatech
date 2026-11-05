from datetime import datetime
from flask import Blueprint, render_template
from db import get_db

bp = Blueprint("historico_movimentacoes", __name__)


@bp.route("/movimentacoes")
def historico_movimentacoes():
    conn = get_db()
    try:
        movimentos = conn.execute("""
            SELECT m.id_movimentacao AS id, p.sku, p.nome_produto AS produto_nome, m.tipo, m.quantidade,
                   m.data_hora, m.observacao
            FROM movimentacoes m
                        INNER JOIN produtos p ON p.id_produto = m.id_produto
            ORDER BY m.data_hora DESC, m.id_movimentacao DESC
        """).fetchall()
        resultado = []
        for movimento in movimentos:
            item = dict(movimento)
            try:
                item["data_formatada"] = datetime.strptime(item["data_hora"], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            except (TypeError, ValueError):
                item["data_formatada"] = str(item["data_hora"])
            resultado.append(item)
        return render_template("movimentacoes.html", movimentacoes=resultado)
    finally:
        conn.close()
