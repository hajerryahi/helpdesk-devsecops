import yaml
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .models import ROLES, Comment, Ticket, User, db
from .security import login_required, role_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/")
@role_required("admin")
def panel():
    users = User.query.order_by(User.id).all()
    counts = {
        "users": len(users),
        "tickets": Ticket.query.count(),
        "comments": Comment.query.count(),
        "open": Ticket.query.filter_by(status="ouvert").count(),
    }
    return render_template("admin.html", users=users, roles=ROLES, counts=counts)


@bp.post("/users/<int:user_id>/role")
@login_required  # F4 - Elevation de role : il manque @role_required("admin") ici.
def change_role(user_id):
    user = db.get_or_404(User, user_id)
    role = request.form.get("role")
    if role in ROLES:
        user.role = role
        db.session.commit()
        flash(f"{user.email} est maintenant {role}.", "success")
    return redirect(url_for("admin.panel"))


@bp.post("/import")
@role_required("admin")
def import_users():
    """Import d'utilisateurs depuis un fichier YAML.

    F6 - Dependance vulnerable : PyYAML 5.3.1 (CVE-2020-14343) + yaml.load
    avec le chargeur complet -> execution de code via un YAML malveillant.
    """
    raw = request.files.get("file")
    if not raw:
        flash("Aucun fichier recu.", "error")
        return redirect(url_for("admin.panel"))
    data = yaml.load(raw.read(), Loader=yaml.FullLoader)
    created = 0
    for entry in data or []:
        if isinstance(entry, dict) and entry.get("email") and not User.query.filter_by(email=entry["email"]).first():
            db.session.add(User(email=entry["email"], full_name=entry.get("full_name", ""),
                                role=entry.get("role", "client"),
                                password=entry.get("password", "ChangeMe123!")))
            created += 1
    db.session.commit()
    flash(f"{created} utilisateur(s) importe(s).", "success")
    return redirect(url_for("admin.panel"))
