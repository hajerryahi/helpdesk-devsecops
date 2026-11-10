"""Cree les comptes et les tickets de demonstration (idempotent).

Le mot de passe des comptes de test vient de la variable SEED_PASSWORD
(valeur par defaut uniquement pour le developpement local).
"""
import os

from app import create_app
from app.models import Comment, Ticket, User, db

PASSWORD = os.environ.get("SEED_PASSWORD", "Test1234!")

USERS = [
    ("admin@test.local", "Amira Admin", "admin"),
    ("agent@test.local", "Karim Agent", "agent"),
    ("agent2@test.local", "Salma Support", "agent"),
    ("client1@test.local", "Sami Ben Ali", "client"),
    ("client2@test.local", "Leila Trabelsi", "client"),
]

TICKETS = [
    ("client1@test.local", "Impossible de me connecter à l'espace client",
     "Depuis ce matin j'ai le message 'compte bloqué'. Mon numéro de contrat est CTR-2026-00418.",
     "haute", "ouvert"),
    ("client1@test.local", "Facture d'octobre introuvable",
     "Je ne trouve pas ma facture d'octobre dans la rubrique Documents.",
     "normale", "en_cours"),
    ("client1@test.local", "Changer mon adresse de livraison",
     "Nouvelle adresse : 12 rue de Marseille, 1000 Tunis.",
     "basse", "resolu"),
    ("client2@test.local", "Remboursement non reçu",
     "J'attends un remboursement de 245 DT. IBAN : TN59 1000 6035 1835 9847 8831.",
     "critique", "ouvert"),
    ("client2@test.local", "Mot de passe Wi-Fi du bureau",
     "Le mot de passe du Wi-Fi invité ne fonctionne plus.",
     "normale", "en_cours"),
    ("client2@test.local", "Imprimante du 2e étage bloquée",
     "Bourrage papier récurrent sur l'imprimante HP du 2e étage.",
     "basse", "ferme"),
]

COMMENTS = [
    (0, "agent@test.local", "Bonjour Sami, je débloque votre compte, pouvez-vous réessayer dans 5 minutes ?"),
    (0, "client1@test.local", "Merci, je réessaie tout de suite."),
    (1, "agent2@test.local", "Je transmets au service facturation."),
    (3, "agent@test.local", "Le remboursement est en cours de validation."),
]


def run():
    app = create_app()
    with app.app_context():
        if User.query.filter_by(email="admin@test.local").first():
            print("Données déjà présentes, rien a faire.")
            return
        users = {}
        for email, name, role in USERS:
            u = User(email=email, full_name=name, role=role, password=PASSWORD)
            db.session.add(u)
            users[email] = u
        db.session.flush()

        tickets = []
        for author, title, desc, prio, status in TICKETS:
            t = Ticket(title=title, description=desc, priority=prio, status=status,
                       created_by=users[author].id)
            if status != "ouvert":
                t.assigned_to = users["agent@test.local"].id
            db.session.add(t)
            tickets.append(t)
        db.session.flush()

        for idx, author, content in COMMENTS:
            db.session.add(Comment(ticket_id=tickets[idx].id,
                                   author_id=users[author].id, content=content))
        db.session.commit()
        print(f"{len(USERS)} comptes et {len(TICKETS)} tickets créés.")


if __name__ == "__main__":
    run()
