from flask import jsonify, redirect, request, session, url_for

GERENTES = {"GERENTE"}
OPERADORES = {"OPERADOR", "GERENTE"}

# Rotas privadas sem política explícita são negadas para evitar permissões acidentais.
POLICIES = {
    "dashboard.dashboard": OPERADORES,
    "novo_produto.novo_produto": GERENTES,
    "excluir_produto.excluir_produto": GERENTES,
    "nova_movimentacao.nova_movimentacao": OPERADORES,
    "historico_movimentacoes.historico_movimentacoes": GERENTES,
    "categorias.categorias": GERENTES,
    "excluir_categoria.excluir_categoria": GERENTES,
    "fornecedores.fornecedores": GERENTES,
    "excluir_fornecedor.excluir_fornecedor": GERENTES,
    "api.dashboard_api": OPERADORES,
    "api.listar_categorias_api": OPERADORES,
    "api.criar_categoria_api": GERENTES,
    "api.excluir_categoria_api": GERENTES,
    "api.listar_fornecedores_api": OPERADORES,
    "api.criar_fornecedor_api": GERENTES,
    "api.excluir_fornecedor_api": GERENTES,
    "api.opcoes_produto_api": OPERADORES,
    "api.criar_produto_api": GERENTES,
    "api.excluir_produto_api": GERENTES,
    "api.listar_movimentacoes_api": GERENTES,
    "api.criar_movimentacao_api": OPERADORES,
    "api.listar_clientes_api": OPERADORES,
    "api.criar_venda_api": OPERADORES,
    "api.recibo_venda_api": OPERADORES,
    "api.recibo_venda_html": OPERADORES,
    "api.livro_razao_api": GERENTES,
    "api.atualizar_perfil_api": GERENTES,
    "api.sessao_api": OPERADORES,
    "auth.logout": OPERADORES,
    "auth.logout_api": OPERADORES,
}
PUBLIC_ENDPOINTS = {
    "auth.login",
    "auth.cadastro",
    "auth.login_api",
    "auth.cadastro_api",
}


def install_permissions(app):
    @app.before_request
    def verificar_permissao():
        endpoint = request.endpoint
        if endpoint is None or endpoint == "static" or endpoint in PUBLIC_ENDPOINTS:
            return None
        perfil = session.get("perfil")
        # Sem autenticação redirecionamos telas e retornamos 401 na API; cada endpoint exige papel.
        if not perfil:
            if request.path.startswith("/api/"):
                return jsonify({"erro": "Autenticação necessária."}), 401
            return redirect(url_for("auth.login", proxima=request.path))
        permitidos = POLICIES.get(endpoint)
        if permitidos is None or perfil not in permitidos:
            if request.path.startswith("/api/"):
                return jsonify({"erro": "Acesso negado."}), 403
            return "Acesso negado.", 403
        return None
