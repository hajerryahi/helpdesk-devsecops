# Failles volontaires de la version `v0-vulnerable`

À utiliser comme base pour les fiches de faille (une fiche par faille, **avant** correction).
Toutes les démonstrations se font **uniquement** sur notre instance locale (`http://localhost:8000`).

| ID | Faille | Fichier | OWASP Top 10:2025 | Détectée par |
| --- | --- | --- | --- | --- |
| F1 | Injection SQL dans la recherche | `app/tickets.py` → `search_tickets()` | A05 Injection | Semgrep, ZAP |
| F2 | XSS stocké dans les commentaires | `app/templates/ticket.html` (`\|safe`) | A05 Injection | ZAP |
| F3 | Accès aux tickets d'autrui (IDOR) | `app/tickets.py` → `view_ticket()`, `app/api.py` → `get_ticket()` | A01 Broken Access Control | Démo manuelle |
| F4 | Élévation de rôle | `app/auth.py` → `register()` (`User(**data)`), `app/admin.py` → `change_role()` sans `@role_required` | A01 Broken Access Control | Démo manuelle |
| F5 | Secrets en dur | `app/config.py` (`SECRET_KEY`, `DB_PASSWORD`), `docker-compose.yml` | A04 Cryptographic Failures | Gitleaks |
| F6 | Dépendance vulnérable | `requirements.txt` : PyYAML 5.3.1 (CVE-2020-14343), utilisée par `admin.py` → `import_users()` | A03 Software Supply Chain Failures | Trivy |
| F7 | Mauvaise configuration | `run.py` / `config.py` (debug actif), aucun en-tête de sécurité, cookie sans `HttpOnly` | A02 Security Misconfiguration | ZAP |

## Démonstrations

Obtenir un jeton de client (pour les démos API) :

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/login -H 'Content-Type: application/json' \
  -d '{"email":"client1@test.local","password":"Test1234!"}' | python -c 'import sys,json;print(json.load(sys.stdin)["token"])')
```

**F1 : injection SQL.** Dans la barre de recherche, en tant que client1, taper `' OR 1=1 --`.
Résultat : les 6 tickets s'affichent, dont ceux de client2 (normalement 3 seulement).
Variante qui extrait les comptes : `zzz' UNION SELECT id, email, role, password_hash, id FROM users --`
(les emails, rôles et hachages apparaissent dans le tableau de résultats).

**F2 : XSS stocké.** En tant que client1, poster sur son ticket le commentaire
`<img src=x onerror="alert(document.cookie)">`. Se connecter ensuite en agent et ouvrir le ticket :
le script s'exécute dans le navigateur de l'agent et affiche son cookie de session (lisible car sans `HttpOnly`, F7).

**F3 : IDOR.** En tant que client1, ouvrir `http://localhost:8000/tickets/4` : c'est le ticket de client2,
avec son IBAN. Même chose par l'API : `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tickets/4`.

**F4 : élévation de rôle.** Deux variantes :

```bash
# 1. S'inscrire directement en admin (affectation de masse)
curl -X POST http://localhost:8000/api/register -H 'Content-Type: application/json' \
  -d '{"email":"evil@test.local","password":"Evil12345","role":"admin"}'

# 2. Un client se donne le rôle admin (route sans contrôle de rôle) - client1 a l'id 4
curl -X POST -H "Authorization: Bearer $TOKEN" -d role=admin http://localhost:8000/admin/users/4/role
```

**F5 : secrets en dur.** Lancer Gitleaks sur le dépôt : `gitleaks detect --source . --redact -v`.
Si la règle générique ne remonte pas la clé, ajouter une règle dans `security/.gitleaks.toml`.

**F6 : dépendance vulnérable.** `trivy fs . --scanners vuln` remonte CVE-2020-14343 (critique) sur PyYAML 5.3.1.
L'impact (exécution de code à l'import d'un YAML malveillant par un admin) est décrit dans l'avis de sécurité de la CVE.

**F7 : mauvaise configuration.** Provoquer une erreur (ex. `POST /tickets/1/status` en agent avec `assigned_to=abc`) :
la page de debug Werkzeug s'affiche avec la trace complète. `curl -I http://localhost:8000/login` montre
l'absence de `Content-Security-Policy`, `X-Frame-Options` et `X-Content-Type-Options`.

## Pistes de correction (pour plus tard)

| ID | Correction |
| --- | --- |
| F1 | Requête paramétrée (`:q`) + filtre par propriétaire |
| F2 | Retirer `\|safe` + en-tête CSP |
| F3 | Vérifier `ticket.created_by == g.user.id` pour un client, sinon 404 |
| F4 | Liste blanche des champs, rôle `client` imposé ; `@role_required("admin")` sur `change_role` |
| F5 | `os.environ["JWT_SECRET"]` / `os.environ["DATABASE_URL"]`, révoquer puis purger l'historique |
| F6 | PyYAML à jour + `yaml.safe_load` |
| F7 | Gunicorn (`wsgi.py`), debug désactivé, en-têtes de sécurité, cookie `HttpOnly` + `Secure` |
