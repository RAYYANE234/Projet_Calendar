import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from plyer import notification
from mistralai import Mistral

# === CONFIGURATION ===
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MISTRAL_API_KEY = "ELCHNSVzP5eRkZPCXejfMDVryanviNmV"
MISTRAL_MODEL = "mistral-large-latest"

# === INIT MISTRAL ===
client = Mistral(api_key=MISTRAL_API_KEY)

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

def analyze_email_with_mistral(subject, snippet):
    prompt = f"""Tu es un assistant qui lit des e-mails envoyés par des professeurs d'université.
Voici un sujet et un extrait d'email :

Sujet : {subject}
Aperçu : {snippet}

Est-ce que ce message annonce une annulation ou un report de cours, TD ou CM ?
Réponds uniquement par "oui" ou "non"."""
    
    response = client.chat.complete(
        model=MISTRAL_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    reply = response.choices[0].message.content.strip().lower()
    return "oui" in reply

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
        time.sleep(2)  # éviter les erreurs 429
        # Analyse via Mistral
        if analyze_email_with_mistral(subject, snippet):
            print(f"\n📧 Sujet : {subject}\n📝 Aperçu : {snippet}")
            notification.notify(
                title="🚨 Annulation ou report détecté",
                message=f"{subject} - {snippet}",
                timeout=10
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
