# am·stram·dam

*Le jeu original est accessible ici : [jeux-geographiques.com](https://www.jeux-geographiques.com/)*

Le but est de localiser des villes de France et du monde le plus précisément et le plus rapidement possible, 
sur le modèle de Jeux Géographiques. Hébergé par Heroku à l'adresse [amstramdam.com](https://www.amstramdam.com). 

Fonctionne avec `Python 3.8`, `Flask` et `SocketIO`. Le serveur est géré par `eventlet` 
et les fonds de carte proviennent de 
[Stamen](http://maps.stamen.com/#toner/12/37.7706/-122.3782)+[OpenStreetMap](http://openstreetmap.org/). 

Source des données : [World Cities Database](https://simplemaps.com/data/world-cities) sous licence [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/) pour les villes hors France, [NosDonnées.FR](https://www.data.gouv.fr/fr/datasets/listes-des-communes-geolocalisees-par-regions-departements-circonscriptions-nd/) sous licence [Open Database License](https://opendatacommons.org/licenses/odbl/summary/) pour les villes de France.

## Installation & développement

Installation:
```
pip install -r requirements.txt
```

Création d'un certificat SSL auto-signé pour développer localement en HTTPS (nécessite OpenSSL) : 
```
mkdir extra
openssl req -x509 -newkey rsa:4096 -keyout extra/certif.key -out extra/certif.crt -days 365 -nodes
```

Lancement du serveur 
```
python server.py [--debug] [--threading]
```
Le flag `--debug` lance le serveur Flask de débug, avec auto-reload et débugger. Sinon, `eventlet` est utilisé.

