"""API JSON : utilisee par le pipeline (connexion de ZAP) et par les demos curl."""
from flask import Blueprint, g, jsonify, request

from .models import Ticket, User, db
from .security import create_token, login_required
from .tickets import search_tickets, visible_tickets_query

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.post("/login")
def api_login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=data.get("email", "")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify(error="identifiants invalides"), 401
    return jsonify(token=create_token(user), role=user.role)


@bp.post("/register")
def api_register():
    data = request.get_json(silent=True) or {}
    if not data.get("email") or not data.get("password"):
        return jsonify(error="email et password obligatoires"), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify(error="email deja utilise"), 409
    user = User(**data)  # F4 : affectation de masse, "role" accepte
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id, email=user.email, role=user.role), 201


@bp.get("/me")
@login_required
def me():
    return jsonify(id=g.user.id, email=g.user.email, role=g.user.role)


@bp.get("/tickets")
@login_required
def list_tickets():
    term = request.args.get("q")
    if term:
        return jsonify(search_tickets(term))  # F1
    return jsonify([t.to_dict() for t in visible_tickets_query().all()])


@bp.get("/tickets/<int:ticket_id>")
@login_required
def get_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)  # F3 : pas de controle du proprietaire
    return jsonify(ticket.to_dict())
