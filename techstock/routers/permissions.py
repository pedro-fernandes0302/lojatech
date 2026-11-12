from flask import g, jsonify, request, session

from db import get_db


PERMISSOES_POR_PERFIL = {
    "OPERADOR": {
        "dashboard.visualizar",
        "categorias.visualizar",
        "fornecedores.visualizar",
        "produtos.visualizar",
        "movimentacoes.visualizar",
        "movimentacoes.registrar",
        "sessao.gerenciar",
    },
    "GERENTE": {
        "dashboard.visualizar",
        "categorias.visualizar",
        "categorias.gerenciar",
        "fornecedores.visualizar",
        "fornecedores.gerenciar",
        "produtos.visualizar",
        "produtos.gerenciar",
        "movimentacoes.visualizar",
        "movimentacoes.registrar",
        "sessao.gerenciar",
    },
}

PERMISSOES_DAS_ROTAS = {
    "api.dashboard_api": "dashboard.visualizar",
    "api.listar_categorias_api": "categorias.visualizar",
    "api.criar_categoria_api": "categorias.gerenciar",
    "api.excluir_categoria_api": "categorias.gerenciar",
    "api.listar_fornecedores_api": "fornecedores.visualizar",
    "api.criar_fornecedor_api": "fornecedores.gerenciar",
    "api.excluir_fornecedor_api": "fornecedores.gerenciar",
    "api.opcoes_produto_api": "produtos.visualizar",
    "api.criar_produto_api": "produtos.gerenciar",
    "api.excluir_produto_api": "produtos.gerenciar",
    "api.listar_movimentacoes_api": "movimentacoes.visualizar",
    "api.criar_movimentacao_api": "movimentacoes.registrar",
    "auth.me": "sessao.gerenciar",
    "auth.logout": "sessao.gerenciar",
}

ROTAS_PUBLICAS = {"auth.login", "auth.registrar"}


def proteger_rotas_api():
    if not request.path.startswith("/api/"):
        return None

    endpoint = request.endpoint
    if endpoint in ROTAS_PUBLICAS:
        return None
    if endpoint is None:
        return None

    permissao = PERMISSOES_DAS_ROTAS.get(endpoint)
    if permissao is None:
        return jsonify({"erro": "Esta rota não possui permissão configurada."}), 403

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"erro": "Autenticação necessária."}), 401

    conn = get_db()
    try:
        usuario = conn.execute(
            "SELECT id_usuario, nome_completo, email, perfil_acesso, status "
            "FROM usuarios WHERE id_usuario = ?",
            (usuario_id,),
        ).fetchone()
    finally:
        conn.close()

    if not usuario or usuario["status"] != "ATIVO":
        session.clear()
        return jsonify({"erro": "Sessão inválida. Faça login novamente."}), 401

    if permissao not in PERMISSOES_POR_PERFIL.get(usuario["perfil_acesso"], set()):
        return jsonify({"erro": "Você não tem permissão para acessar esta rota."}), 403

    g.usuario = dict(usuario)
    return None
