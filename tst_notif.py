import sys
sys.stdout.reconfigure(encoding='utf-8')  # Pour éviter les erreurs d'encodage dans le terminal

import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from plyer import notification

# Scopes autorisés pour lire les e-mails Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token_gmail.json'):
        creds = Credentials.from_authorized_user_file('token_gmail.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_gmail.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(service):
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX', 'UNREAD'],
        maxResults=10
    ).execute()

    messages = results.get('messages', [])
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        subject = ''
        for header in msg_detail['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
        snippet = msg_detail.get('snippet', '')
        print(f"\n📧 Sujet : {subject}\n📝 Aperçu : {snippet}")
        notification.notify(
            title=f"Nouveau mail : {subject}",
            message=snippet,
            timeout=5
        )

def main():
    service = get_gmail_service()
    while True:
        print("\n🔍 Vérification des e-mails non lus...")
        get_unread_emails(service)
        print("⏳ Prochaine vérification dans 10 minutes...\n")
        time.sleep(600)

if __name__ == '__main__':
    main()
