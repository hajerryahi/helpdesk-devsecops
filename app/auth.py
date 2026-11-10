from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, url_for)

from .models import User, db
from .security import create_token

bp = Blueprint("auth", __name__)


def _set_session_cookie(resp, token):
    # F7 : cookie sans HttpOnly ni Secure -> lisible par JavaScript,
    # ce qui permet le vol de session via le XSS stocke (F2).
    resp.set_cookie("token", token, max_age=8 * 3600, samesite="Lax")
    return resp


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form.to_dict()
        if not data.get("email") or not data.get("password"):
            flash("Email et mot de passe obligatoires.", "error")
            return render_template("register.html"), 400
        if User.query.filter_by(email=data["email"]).first():
            flash("Un compte existe deja avec cet email.", "error")
            return render_template("register.html"), 400

        # F4 - Elevation de role (affectation de masse) :
        # tous les champs du formulaire sont passes au modele, y compris un
        # champ "role" ajoute par l'attaquant (ex. role=admin).
        user = User(**data)
        db.session.add(user)
        db.session.commit()

        flash("Compte cree, bienvenue !", "success")
        resp = make_response(redirect(url_for("tickets.dashboard")))
        return _set_session_cookie(resp, create_token(user))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Email ou mot de passe incorrect.", "error")
            return render_template("login.html", email=email), 401
        resp = make_response(redirect(request.args.get("next") or url_for("tickets.dashboard")))
        flash(f"Bonjour {user.full_name or user.email} !", "success")
        return _set_session_cookie(resp, create_token(user))
    if g.user:
        return redirect(url_for("tickets.dashboard"))
    return render_template("login.html")


@bp.get("/logout")
def logout():
    resp = make_response(redirect(url_for("auth.login")))
    resp.delete_cookie("token")
    flash("Tu es deconnecte.", "info")
    return resp
