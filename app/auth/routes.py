import logging

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models import User

logger = logging.getLogger(__name__)
bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Informe usuário/e-mail e senha.", "error")
            return render_template("login.html")

        try:
            user = User.query.filter(
                (User.username == identifier) | (User.email == identifier)
            ).first()
        except SQLAlchemyError:
            # Cenário: erro de conexão com o banco de dados.
            logger.exception("Erro de conexão com o banco de dados ao validar login.")
            flash(
                "Não foi possível validar suas credenciais no momento. Tente novamente em instantes.",
                "error",
            )
            return render_template("login.html")

        if user is None or not user.check_password(password):
            # Cenário: credenciais de login inválidas.
            logger.info("Tentativa de login inválida para identificador '%s'.", identifier)
            flash("Usuário/e-mail ou senha inválidos.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        return redirect(url_for("agenda.index"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
