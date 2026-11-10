"""HelpDesk - systeme de tickets de support.

!!! VERSION VOLONTAIREMENT VULNERABLE (v0-vulnerable) !!!
Projet pedagogique DevSecOps : a executer uniquement en local ou dans un
environnement dedie que l'equipe possede. Voir docs/FAILLES.md.
"""
from flask import Flask, g, jsonify, render_template, request

from . import config
from .models import db
from .security import load_current_user, wants_json


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=config.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_ALGORITHM=config.JWT_ALGORITHM,
        JWT_EXPIRES_HOURS=config.JWT_EXPIRES_HOURS,
        DEBUG=config.DEBUG,  # F7
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,
    )
    if overrides:
        app.config.update(overrides)

    db.init_app(app)

    from .admin import bp as admin_bp
    from .api import bp as api_bp
    from .auth import bp as auth_bp
    from .tickets import bp as tickets_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    app.before_request(load_current_user)

    # F7 : aucun en-tete de securite n'est ajoute (pas de CSP, X-Frame-Options,
    # X-Content-Type-Options, HSTS). La correction se fera dans un after_request.

    labels = {"ouvert": "ouvert", "en_cours": "en cours", "resolu": "résolu", "ferme": "fermé"}
    app.jinja_env.filters["status_label"] = lambda s: labels.get(s, s)

    @app.context_processor
    def inject_user():
        return {"current_user": g.get("user")}

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    def error_page(code, title, message):
        if wants_json():
            return jsonify(error=title), code
        return render_template("error.html", code=code, title=title, message=message), code

    @app.errorhandler(401)
    def unauthorized(_):
        return error_page(401, "Non authentifie", "Connecte-toi pour acceder a cette page.")

    @app.errorhandler(403)
    def forbidden(_):
        return error_page(403, "Acces refuse", "Ton role ne permet pas d'acceder a cette page.")

    @app.errorhandler(404)
    def not_found(_):
        return error_page(404, "Introuvable", "Cette page ou ce ticket n'existe pas.")

    with app.app_context():
        db.create_all()

    return app
