from mistral import Client
from plyer import notification

def main():
    # Initialisation client Mistral
    client = Client()

    # Récupérer les 15 derniers emails
    emails = client.get_latest_emails(limit=15)

    # Filtrer les emails non lus et liés aux modifications
    for email in emails:
        # Supposons que email a les attributs : is_read, type_modification, subject, content
        if not email.is_read and email.type_modification in ['annulation', 'report', 'changement de salle']:
            # Affichage console
            print(f"Type: {email.type_modification}")
            print(f"Contenu: {email.content}\n")

            # Notification système
            notification.notify(
                title=f"Nouvelle {email.type_modification}",
                message=email.subject,
                timeout=5  # secondes
            )

if __name__ == "__main__":
    main()
