import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from db import get_db


def snapshot():
    conn = get_db()
    try:
        return {
            "estoques": [dict(row) for row in conn.execute(
                "SELECT sku, estoque_atual FROM produtos ORDER BY id_produto"
            )],
            "vendas": conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0],
            "itens_venda": conn.execute("SELECT COUNT(*) FROM itens_venda").fetchone()[0],
            "movimentacoes": conn.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0],
        }
    finally:
        conn.close()


def main():
    conn = get_db()
    try:
        limitado = conn.execute(
            "SELECT id_produto, nome_produto, estoque_atual FROM produtos "
            "WHERE sku = 'PER001' AND estoque_atual > 0"
        ).fetchone()
        if limitado:
            com_estoque = conn.execute(
                "SELECT id_produto FROM produtos WHERE estoque_atual >= 1 AND id_produto != ? "
                "ORDER BY id_produto LIMIT 1",
                (limitado["id_produto"],),
            ).fetchone()
        else:
            com_estoque = None
        cliente = conn.execute("SELECT id_cliente FROM clientes ORDER BY id_cliente LIMIT 1").fetchone()
        if not com_estoque or not limitado or not cliente or com_estoque["id_produto"] == limitado["id_produto"]:
            raise RuntimeError("Não há cliente e dois produtos com saldo para demonstrar o rollback.")
        produto_regular = com_estoque["id_produto"]
        produto_excedido = limitado["id_produto"]
        nome = limitado["nome_produto"]
        disponivel = limitado["estoque_atual"]
    finally:
        conn.close()

    antes = snapshot()
    client = app.test_client()
    login = client.post("/api/login", json={
        "email": "operador@techstore.com", "senha": "operador-techstore-2026",
    })
    if login.status_code != 200:
        raise RuntimeError(f"Falha ao autenticar operador de demonstração: HTTP {login.status_code}")
    resposta = client.post("/api/vendas", json={
        "id_cliente": cliente["id_cliente"],
        "itens": [
            {"id_produto": produto_regular, "quantidade": 1},
            {"id_produto": produto_excedido, "quantidade": disponivel + 1},
        ],
    })
    depois = snapshot()
    print("ANTES:\n" + json.dumps(antes, indent=2, ensure_ascii=False))
    print(f"\nRESPOSTA: HTTP {resposta.status_code} — {resposta.get_json()}")
    print("\nDEPOIS:\n" + json.dumps(depois, indent=2, ensure_ascii=False))
    if resposta.status_code != 409 or antes != depois:
        raise SystemExit("FALHA: estado mudou ou a venda não foi bloqueada.")
    print(f"\nROLLBACK comprovado: venda de {disponivel + 1} × {nome} (saldo {disponivel}) não persistiu.")


if __name__ == "__main__":
    main()
