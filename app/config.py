"""Configuration de HelpDesk.

!!! VERSION VOLONTAIREMENT VULNERABLE (v0-vulnerable) !!!
F5 - Secret expose : la cle JWT et le mot de passe de la base sont ecrits en dur
     dans le code et donc pousses dans le depot Git. Ce sont des secrets DE TEST.
"""
import os

# F5 : secrets en dur (a remplacer par os.environ["..."] lors de la correction)
SECRET_KEY = "hd_jwt_9f3Kq2LxV7pRt8WmZ4bN6cY1sA5eU0dH"
DB_PASSWORD = "Passw0rd!"

# La variable d'environnement permet de lancer en local avec SQLite,
# mais la valeur par defaut contient toujours le mot de passe en clair.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql+psycopg2://helpdesk:{DB_PASSWORD}@db:5432/helpdesk",
)

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS = 8

# F7 : mauvaise configuration - mode debug active
DEBUG = True
