"""Point d'entree WSGI pour Gunicorn (utilise apres correction de F7)."""
from app import create_app

app = create_app()
