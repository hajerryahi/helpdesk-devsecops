from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, url_for)
from sqlalchemy import text

from .models import PRIORITIES, STATUSES, Comment, Ticket, User, db
from .security import login_required, role_required

bp = Blueprint("tickets", __name__)


def visible_tickets_query():
    """Liste normale : un client ne voit que ses tickets."""
    q = Ticket.query
    if g.user.role == "client":
        q = q.filter_by(created_by=g.user.id)
    return q


def search_tickets(term):
    # F1 - Injection SQL : le texte saisi est colle tel quel dans la requete.
    # De plus, la recherche ignore le proprietaire du ticket.
    sql = (
        "SELECT id, title, status, priority, created_by FROM tickets "
        f"WHERE title LIKE '%{term}%' OR description LIKE '%{term}%' "
        "ORDER BY id DESC"
    )
    rows = db.session.execute(text(sql)).fetchall()
    return [dict(r._mapping) for r in rows]


@bp.get("/")
@login_required
def dashboard():
    term = request.args.get("q", "").strip()
    status = request.args.get("status", "")

    results = None
    if term:
        results = search_tickets(term)

    q = visible_tickets_query()
    if status in STATUSES:
        q = q.filter_by(status=status)
    tickets = q.order_by(Ticket.created_at.desc()).all()

    base = visible_tickets_query()
    stats = {s: base.filter_by(status=s).count() for s in STATUSES}
    stats["total"] = sum(stats.values())

    return render_template(
        "dashboard.html", tickets=tickets, results=results, term=term,
        status=status, stats=stats, statuses=STATUSES,
    )


@bp.route("/tickets/new", methods=["GET", "POST"])
@login_required
def new_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "normale")
        if not title:
            flash("Le titre est obligatoire.", "error")
            return render_template("new_ticket.html", priorities=PRIORITIES), 400
        if priority not in PRIORITIES:
            priority = "normale"
        ticket = Ticket(title=title, description=description,
                        priority=priority, created_by=g.user.id)
        db.session.add(ticket)
        db.session.commit()
        flash(f"Ticket #{ticket.id} cree.", "success")
        return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))
    return render_template("new_ticket.html", priorities=PRIORITIES)


@bp.get("/tickets/<int:ticket_id>")
@login_required
def view_ticket(ticket_id):
    # F3 - IDOR : aucun controle du proprietaire. Un client peut lire
    # n'importe quel ticket en changeant l'identifiant dans l'URL.
    ticket = db.get_or_404(Ticket, ticket_id)
    agents = User.query.filter(User.role.in_(["agent", "admin"])).all()
    return render_template("ticket.html", ticket=ticket, statuses=STATUSES, agents=agents)


@bp.post("/tickets/<int:ticket_id>/comments")
@login_required
def add_comment(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)  # F3 egalement : commenter le ticket d'autrui
    content = request.form.get("content", "").strip()
    if content:
        # F2 - XSS stocke : le contenu est enregistre sans filtrage et
        # affiche avec |safe dans ticket.html.
        db.session.add(Comment(ticket_id=ticket.id, author_id=g.user.id, content=content))
        db.session.commit()
        flash("Commentaire ajoute.", "success")
    return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id) + "#comments")


@bp.post("/tickets/<int:ticket_id>/status")
@role_required("agent", "admin")
def change_status(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    status = request.form.get("status")
    assignee = request.form.get("assigned_to")
    if status in STATUSES:
        ticket.status = status
    if assignee:
        ticket.assigned_to = int(assignee) if assignee != "none" else None
    db.session.commit()
    flash("Ticket mis a jour.", "success")
    return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))


@bp.post("/tickets/<int:ticket_id>/delete")
@login_required
def delete_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if g.user.role != "admin" and ticket.created_by != g.user.id:
        abort(403)
    db.session.delete(ticket)
    db.session.commit()
    flash("Ticket supprime.", "info")
    return redirect(url_for("tickets.dashboard"))
