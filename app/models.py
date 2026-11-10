from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

ROLES = ("client", "agent", "admin")
STATUSES = ("ouvert", "en_cours", "resolu", "ferme")
PRIORITIES = ("basse", "normale", "haute", "critique")


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False, default="")
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    def __init__(self, **kwargs):
        # Accepte n'importe quel champ (dont "role") : utilise par F4.
        password = kwargs.pop("password", None)
        super().__init__(**kwargs)
        if password:
            self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        src = self.full_name or self.email
        parts = [p for p in src.replace("@", " ").split() if p]
        return "".join(p[0].upper() for p in parts[:2]) or "?"


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="ouvert")
    priority = db.Column(db.String(20), nullable=False, default="normale")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)

    author = db.relationship("User", foreign_keys=[created_by])
    assignee = db.relationship("User", foreign_keys=[assigned_to])
    comments = db.relationship(
        "Comment", backref="ticket", order_by="Comment.created_at",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "status": self.status, "priority": self.priority,
            "created_by": self.created_by, "assigned_to": self.assigned_to,
            "author_email": self.author.email if self.author else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    author = db.relationship("User")
