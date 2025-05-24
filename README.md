
Pour lancer le projet, il suffit d’exécuter le fichier main.py Ce script réalise automatiquement les étapes suivantes :
 
  - Il exécute d’abord import_edt.py, qui importe l’emploi du temps contenu dans le fichier edt_miage.ics vers Google Calendar.
  - Ensuite, il exécute mistral.py, qui filtre les emails reçus des professeurs pour détecter d’éventuelles modifications ou annulations de cours.
   Grâce à l’intelligence artificielle de Mistral AI, le contenu des emails est analysé afin d’en extraire les informations pertinentes. Ces données sont ensuite enregistrées dans un fichier JSON, utilisé pour mettre à jour automatiquement Google Calendar.

Avant de lancer le projet, assurez-vous d’installer les bibliothèques suivantes :

pip install mistralai
pip install google-auth
pip install google-auth-oauthlib
pip install google-api-python-client
pip install plyer
pip install icalendar
pip install pytz

 Remarques importante !

 Le projet utilise la bibliothèque mistralai version 1.7.1 , Il est recommandé d’installer cette version pour assurer la compatibilité :

  pip install mistralai==1.7.1
  
La clé API Mistral AI utilisée dans ce projet est valide jusqu’au 28 août 2025.

