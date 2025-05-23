import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import sys
import time
import json
import re

from mistralai import Mistral
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from plyer import notification

sys.stdout.reconfigure(encoding='utf-8')

# 🔑 Mistral API
os.environ["MISTRAL_API_KEY"] = "ELCHNSVzP5eRkZPCXejfMDVryanviNmV"  # ← remplace par ta clé
MISTRAL_MODEL = "mistral-large-latest"
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# 📧 Gmail scopes
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES_CALENDAR = ['https://www.googleapis.com/auth/calendar']

def get_gmail_service():
    creds = None
    if os.path.exists('token_gmail.json'):
        creds = Credentials.from_authorized_user_file('token_gmail.json', SCOPES_GMAIL)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_gmail.json', SCOPES_GMAIL)
            creds = flow.run_local_server(port=0)
        with open('token_gmail.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_calendar_service():
    creds = None
    if os.path.exists('token_calendar.json'):
        creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES_CALENDAR)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials_calendar.json', SCOPES_CALENDAR)
        creds = flow.run_local_server(port=0)
        with open('token_calendar.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def analyze_email_with_mistral_structured(subject, body):

    prompt = f"""
Tu es un assistant intelligent qui lit des emails de professeurs à propos de leurs cours.

Voici le sujet de l’email : "{subject}"
Voici son contenu : "{body}"

Ton but est de détecter si l’email indique un report, une annulation, ou aucun changement de cours.

Si le message concerne :
- l'annulation d'un cours : réponds avec {{ "action": "annuler", "titre": "...", "date": "AAAA-MM-JJ" }}
- le report d’un cours : réponds avec {{ "action": "reporter", "titre": "...", "ancienne_date": "AAAA-MM-JJ", "nouvelle_date": "AAAA-MM-JJ", "heure": "HH:MM" }}
- aucun changement : réponds avec {{ "action": "aucune" }}

🛑 Important :
- Ne commente rien.
- Réponds uniquement avec un JSON valide.
- N’ajoute aucune phrase autour.
- Dans titre: il faut mettre que le nom du module (ex: "Mathématiques", "Physique", "Anglais", etc.)
Exemples :
{{"action": "reporter", "titre": "Mathématiques", "ancienne_date": "2025-04-07", "nouvelle_date": "2025-04-10", "heure": "14:00"}}
{{"action": "annuler", "titre": "Physique", "date": "2025-04-15"}}
{{"action": "aucune"}}

Tu dois uniquement répondre si l'email parle d'un cours,TD ou TP annulé ou reporté par un professeur.  

"""

    try:
        response = client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        match = re.search(r'{.*}', reply, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            print(f"⚠️ Pas de JSON trouvé dans la réponse Mistral :\n{reply}")
            return {"action": "aucune"}
    except Exception as e:
        print(f"⚠️ Erreur Mistral : {e}")
        return {"action": "aucune"}

def delete_event(service, title, date):
    events = service.events().list(
        calendarId='primary',
        timeMin=date + 'T00:00:00Z',
        timeMax=date + 'T23:59:59Z'
    ).execute()
    for event in events.get('items', []):
        #if title.lower() in event.get('summary', '').lower():
        service.events().delete(calendarId='primary', eventId=event['id']).execute()
        print(f"🗑️ Supprimé : {event['summary']}")
        return True
    return False

def update_event(service, title, old_date, new_date, time_str):
    # Recherche les événements à la date ancienne (old_date)
    events = service.events().list(
        calendarId='primary',
        timeMin=old_date + 'T00:00:00Z',
        timeMax=old_date + 'T23:59:59Z'
    ).execute()
    
    for event in events.get('items', []):
        if title.lower() in event.get('summary', '').lower():
            # Crée les nouveaux horaires à la nouvelle date
            start = f"{new_date}T{time_str}:00"
            end_hour = str((int(time_str[:2]) + 1) % 24).zfill(2)  # ajout mod 24 pour sécurité
            end = f"{new_date}T{end_hour}:{time_str[3:]}:00"
            
            event['start']['dateTime'] = start
            event['end']['dateTime'] = end
            
            updated = service.events().update(
                calendarId='primary', eventId=event['id'], body=event
            ).execute()
            
            print(f"🔁 Événement modifié : {updated['summary']}")
            return True
    print("⚠️ Aucun événement trouvé à modifier.")
    return False


def get_unread_emails(gmail_service, calendar_service):
    results = gmail_service.users().messages().list(
        userId='me',
        labelIds=['INBOX', 'UNREAD'],
        maxResults=10
    ).execute()

    messages = results.get('messages', [])
    for msg in messages:
        msg_detail = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
        subject = ''
        for header in msg_detail['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
        snippet = msg_detail.get('snippet', '')
        print(f"\n📧 Sujet : {subject}\n📝 Aperçu : {snippet}")

        data = analyze_email_with_mistral_structured(subject, snippet)
        action = data.get("action")
        if action == "annuler":
            notification.notify(
            title=f"Nouveau mail : {subject}",
            message=snippet,
            timeout=5
            )
            print("🛠️ Détails complets Mistral pour annulation :")
            print(data)  # affiche le dict JSON reçu de Mistral
            deleted=delete_event(calendar_service, data.get("titre"), data.get("date"))
            if deleted:
                print("✅ Notification : Événement annulé supprimé du calendrier.")
            else:
                print("⚠️ Aucune suppression effectuée.")
        elif action == "reporter":
            notification.notify(
            title=f"Nouveau mail : {subject}",
            message=snippet,
            timeout=5
            )            
            if data.get("heure"):
                print("🛠️ Détails complets Mistral pour modification :")
                print(data)  # affiche le dict JSON reçu de Mistral
                update_event(calendar_service, data.get("titre"), data.get("ancienne_date"), data.get("nouvelle_date"), data.get("heure"))
        else:
            print("ℹ️ Aucun changement nécessaire.")
        time.sleep(2)  # limite les appels API

def main():
    gmail_service = get_gmail_service()
    calendar_service = get_calendar_service()
    while True:
        print("\n🔍 Vérification des e-mails non lus...")
        get_unread_emails(gmail_service, calendar_service)
        print("⏳ Prochaine vérification dans 10 minutes...\n")
        time.sleep(600)

if __name__ == '__main__':
    main()
