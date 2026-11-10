"""Jetons JWT, utilisateur courant et decorateurs de role."""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import abort, current_app, flash, g, redirect, request, url_for

from .models import User, db


def create_token(user):
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=current_app.config["JWT_EXPIRES_HOURS"]),
    }
    return jwt.encode(
        payload, current_app.config["SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def _token_from_request():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:]
    return request.cookies.get("token")


def load_current_user():
    g.user = None
    token = _token_from_request()
    if not token:
        return
    try:
        data = jwt.decode(
            token, current_app.config["SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.PyJWTError:
        return
    g.user = db.session.get(User, int(data["sub"]))


def wants_json():
    return request.path.startswith("/api/")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            if wants_json():
                abort(401)
            flash("Connecte-toi pour continuer.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
