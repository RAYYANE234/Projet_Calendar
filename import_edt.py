from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle
from icalendar import Calendar
import pytz

# === CONFIG ===
SCOPES = ['https://www.googleapis.com/auth/calendar']
COULEURS = {
    "CM": "5",       # Jaune
    "Anglais": "9",  # Bleu
    "TD": "2",       # Vert
    "CC": "4"        # Marron clair
}

# === AUTHENTIFICATION ===
def authenticate_google_account():
    creds = None
    if os.path.exists('token_calendar.pkl'):
        with open('token_calendar.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/oussa/Desktop/projet_ray/Projet_Calendar/credentials_calendar.json', SCOPES)
            creds = flow.run_local_server(port=0)
            #creds = flow.run_console() 
        with open('token_calendar.pkl', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# === SUPPRESSION DES ANCIENS ÉVÉNEMENTS ===
def delete_all_events(service, calendar_id='primary'):
    page_token = None
    while True:
        events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
        for event in events['items']:
            try:
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
                print(f"Supprimé : {event.get('summary')}")
            except Exception as e:
                print(f"Erreur suppression : {e}")
        page_token = events.get('nextPageToken')
        if not page_token:
            break

# === AJOUT DES ÉVÉNEMENTS ===
def add_event(service, title, start_time, end_time, location, couleur_id):
    event = {
        'summary': title,
        'location': location,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Paris',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Paris',
        },
        'colorId': couleur_id,
    }
    service.events().insert(calendarId='primary', body=event).execute()
    print(f"Ajouté : {title} le {start_time}")

# === DÉTERMINER LA COULEUR EN FONCTION DU COURS ===
def get_color_id(title, location):
    if "CC" in title:
        return COULEURS["CC"]
    elif "AMPHI" in location:
        return COULEURS["CM"]
    elif "Anglais" in title:
        return COULEURS["Anglais"]
    else:
        return COULEURS["TD"]

# === LIRE LE FICHIER ICS ET EXTRAIRE LES ÉVÉNEMENTS ===
def read_ics_and_add_events(service, ics_path):
    with open(ics_path, 'rb') as f:
        cal = Calendar.from_ical(f.read())
        for component in cal.walk():
            if component.name == "VEVENT":
                title = str(component.get('summary'))
                location = str(component.get('location'))
                start = component.get('dtstart').dt
                end = component.get('dtend').dt

                # Convertir en string ISO avec timezone si besoin
                if isinstance(start, datetime):
                    start = start.astimezone(pytz.timezone('Europe/Paris')).isoformat()
                else:
                    start = datetime.combine(start, datetime.min.time()).astimezone(pytz.timezone('Europe/Paris')).isoformat()
                if isinstance(end, datetime):
                    end = end.astimezone(pytz.timezone('Europe/Paris')).isoformat()
                else:
                    end = datetime.combine(end, datetime.min.time()).astimezone(pytz.timezone('Europe/Paris')).isoformat()

                couleur_id = get_color_id(title, location)
                add_event(service, title, start, end, location, couleur_id)

# === MAIN ===
def main():
    creds = authenticate_google_account()
    service = build('calendar', 'v3', credentials=creds)

    # Supprimer tous les anciens événements
    delete_all_events(service)

    # Ajouter les événements du fichier ICS
    read_ics_and_add_events(service, 'C:/Users/oussa/Desktop/projet_ray/Projet_Calendar/edt_miage.ics')

if __name__ == '__main__':
    main()
