from flask import Blueprint, render_template

bp = Blueprint("errors", __name__)


@bp.app_errorhandler(404)
def pagina_nao_encontrada(_erro):
    return render_template("404.html"), 404


@bp.app_errorhandler(500)
def erro_interno(_erro):
    return render_template("500.html"), 500
