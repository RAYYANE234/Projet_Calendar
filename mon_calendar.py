import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64

# Scopes autorisés pour Gmail (lecture, envoi…)
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw_message.decode()}

def main():
    creds = None
    if os.path.exists('token_gmail.json'):
        creds = Credentials.from_authorized_user_file('token_gmail.json', SCOPES_GMAIL)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_gmail.json', SCOPES_GMAIL)
            creds = flow.run_local_server(port=0)
        with open('token_gmail.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Création et envoi du message
    sender = "43013167@parisnanterre.fr"
    to = "44009648@parisnanterre.fr"
    subject = "Test MIAGE via Python"
    message_text = "Bonjour ! Ceci est un message de test envoyé depuis l’API Gmail via Python 🎉."

    message = create_message(sender, to, subject, message_text)
    send_message = service.users().messages().send(userId="me", body=message).execute()
    print(f"✅ Message envoyé avec l'ID : {send_message['id']}")

if __name__ == '__main__':
    main()
