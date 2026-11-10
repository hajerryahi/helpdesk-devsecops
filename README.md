# HelpDesk : système de tickets de support (projet DevSecOps)

> **⚠️ Version `v0-vulnerable`.** Cette application contient **7 failles volontaires** pour le projet DevSecOps ING-5-SSIR (TEK-UP).
> Ne l'exécutez qu'en local ou dans un environnement dédié qui appartient à l'équipe, jamais exposée sur Internet.
> Les secrets présents dans le code sont des **secrets de test**.

Équipe : Wissal Rezgui, Tasnim, Hajer.

## Fonctionnalités

- Inscription, connexion, jeton JWT (cookie `token` ou en-tête `Authorization: Bearer`)
- 3 rôles : **client** (crée et suit ses tickets), **agent** (traite tous les tickets), **admin** (gère les comptes)
- Tickets : création avec priorité, liste, recherche, filtres par statut, suivi d'avancement
- Discussion par commentaires sur chaque ticket
- Panneau d'administration : changement de rôle, import d'utilisateurs en YAML
- API JSON (`/api/...`) pour le pipeline et les démonstrations
- Route `/healthz` pour les sondes Kubernetes
- Interface animée : fond en aurore, cartes en cascade, compteurs et anneaux animés, notifications, barre de progression du ticket

## Lancer l'application

### Avec Docker (recommandé : PostgreSQL inclus)

```bash
docker compose up --build
```

Puis ouvrir http://localhost:8000.

### Sans Docker (SQLite, pour développer vite)

```bash
python -m venv venv && source venv/bin/activate     # Windows : venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///helpdesk.db           # Windows PowerShell : $env:DATABASE_URL="sqlite:///helpdesk.db"
python seed.py
python run.py
```

### Comptes de test

Mot de passe de tous les comptes : valeur de `SEED_PASSWORD` (par défaut `Test1234!`).

| Email | Rôle |
| --- | --- |
| admin@test.local | admin |
| agent@test.local | agent |
| agent2@test.local | agent |
| client1@test.local | client |
| client2@test.local | client |

### Tests

```bash
pip install pytest
python -m pytest -q
```

## Structure

```text
app/
  __init__.py      création de l'application, gestion des erreurs
  config.py        configuration (F5, F7)
  models.py        User, Ticket, Comment
  security.py      JWT, utilisateur courant, @login_required, @role_required
  auth.py          inscription, connexion (F4)
  tickets.py       tableau de bord, recherche (F1), ticket (F3), commentaires (F2)
  admin.py         rôles (F4), import YAML (F6)
  api.py           API JSON
  templates/       pages HTML (Jinja2)
  static/          style.css, app.js (animations)
seed.py            données de démonstration
run.py             serveur de développement (F7)
wsgi.py            point d'entrée Gunicorn (pour la version corrigée)
Dockerfile, docker-compose.yml
tests/             tests pytest
docs/FAILLES.md    liste des failles volontaires
```

## Les failles

Voir [`docs/FAILLES.md`](docs/FAILLES.md). Chaque emplacement vulnérable est aussi signalé dans le code par un commentaire `F1` à `F7`.
