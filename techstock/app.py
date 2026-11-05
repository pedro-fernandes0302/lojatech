import os
from flask import Flask
from db import ensure_database
from routers.dashboard import bp as dashboard_bp
from routers.novo_produto import bp as novo_produto_bp
from routers.excluir_produto import bp as excluir_produto_bp
from routers.nova_movimentacao import bp as nova_movimentacao_bp
from routers.historico_movimentacoes import bp as historico_movimentacoes_bp
from routers.categorias import bp as categorias_bp
from routers.excluir_categoria import bp as excluir_categoria_bp
from routers.fornecedores import bp as fornecedores_bp
from routers.excluir_fornecedor import bp as excluir_fornecedor_bp
from routers.errors import bp as errors_bp
from routers.api import bp as api_bp

app = Flask(__name__)
app.secret_key = os.environ.get("TECHSTOCK_SECRET_KEY", "techstock-desenvolvimento-local")
ensure_database()

@app.template_filter("brl")
def formatar_brl(valor):
    try:
        texto = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return "R$ " + texto
    except (TypeError, ValueError):
        return "R$ 0,00"

# Blueprints mantêm cada rota isolada na pasta routers.
app.register_blueprint(dashboard_bp)
app.register_blueprint(novo_produto_bp)
app.register_blueprint(excluir_produto_bp)
app.register_blueprint(nova_movimentacao_bp)
app.register_blueprint(historico_movimentacoes_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(excluir_categoria_bp)
app.register_blueprint(fornecedores_bp)
app.register_blueprint(excluir_fornecedor_bp)
app.register_blueprint(errors_bp)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(debug=True)
