"""Tests fonctionnels de base (SQLite en memoire)."""
import pytest

from app import create_app
from app.models import Ticket, User, db


@pytest.fixture()
def client():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://", "TESTING": True})
    with app.app_context():
        db.session.add_all([
            User(email="c1@test.local", full_name="Client Un", role="client", password="Test1234!"),
            User(email="c2@test.local", full_name="Client Deux", role="client", password="Test1234!"),
            User(email="agent@test.local", full_name="Agent", role="agent", password="Test1234!"),
        ])
        db.session.commit()
        db.session.add(Ticket(title="Ticket de c2", description="prive", created_by=2))
        db.session.commit()
    with app.test_client() as c:
        yield c


def login(client, email):
    return client.post("/login", data={"email": email, "password": "Test1234!"})


def test_healthz(client):
    assert client.get("/healthz").get_json() == {"status": "ok"}


def test_login_and_dashboard(client):
    assert login(client, "c1@test.local").status_code == 302
    page = client.get("/")
    assert page.status_code == 200
    assert "Tableau de bord" in page.get_data(as_text=True)


def test_bad_password(client):
    r = client.post("/login", data={"email": "c1@test.local", "password": "faux"})
    assert r.status_code == 401


def test_create_ticket(client):
    login(client, "c1@test.local")
    r = client.post("/tickets/new", data={"title": "Probleme", "description": "x", "priority": "haute"})
    assert r.status_code == 302


def test_client_list_shows_only_own_tickets(client):
    login(client, "c1@test.local")
    assert "Ticket de c2" not in client.get("/").get_data(as_text=True)


def test_api_login_returns_token(client):
    r = client.post("/api/login", json={"email": "agent@test.local", "password": "Test1234!"})
    assert r.status_code == 200 and r.get_json()["token"]


def test_admin_panel_forbidden_for_client(client):
    login(client, "c1@test.local")
    assert client.get("/admin/").status_code == 403
