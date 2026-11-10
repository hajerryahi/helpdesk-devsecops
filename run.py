"""Lancement en mode developpement.

F7 - Mauvaise configuration : serveur de developpement Flask, mode debug actif
et ecoute sur toutes les interfaces. La console de debug Werkzeug et les traces
d'erreur completes sont exposees. A remplacer par Gunicorn (wsgi.py) a la correction.
"""
from app import config, create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=config.DEBUG)
