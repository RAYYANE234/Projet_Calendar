import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Scopes autorisés pour Gmail (lecture, envoi…)
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']

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

    # Ici tu pourras ajouter l’envoi d’un mail plus tard
    print("Connexion à l'API Gmail réussie.")

if __name__ == '__main__':
    main()
