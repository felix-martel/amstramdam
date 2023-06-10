# am·stram·dam

<a href="https://github.com/felix-martel/amstramdam/actions"><img src="https://img.shields.io/github/workflow/status/felix-martel/amstramdam/python-ci?label=checks"></a>
<a href="https://github.com/felix-martel/amstramdam/releases"><img src="https://img.shields.io/github/v/release/felix-martel/amstramdam"></a>
<a href="https://github.com/felix-martel/amstramdam/commits/master"><img src="https://img.shields.io/github/last-commit/felix-martel/amstramdam"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

*Le jeu original est accessible ici : [jeux-geographiques.com](https://www.jeux-geographiques.com/)*

Le but est de localiser des villes de France et du monde le plus précisément et le plus rapidement possible, 
sur le modèle de Jeux Géographiques. Hébergé par Heroku à l'adresse [amstramdam.com](https://www.amstramdam.com). 

Fonctionne avec `Python 3.11`, `Flask` et `SocketIO`. Le serveur est géré par `eventlet` 
et les fonds de carte proviennent de 
[Stamen](http://maps.stamen.com/#toner/12/37.7706/-122.3782)+[OpenStreetMap](http://openstreetmap.org/). 



## Source des données

am·stram·dam agrège des données provenant des sources suivantes :

| Source | Licence | Utilisation |
| :-     | :-      | :-          |
| [World Cities Database](https://simplemaps.com/data/world-cities) | [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Villes du monde (hors capitales) |
| [NosDonnées.FR](https://www.data.gouv.fr/fr/datasets/listes-des-communes-geolocalisees-par-regions-departements-circonscriptions-nd/) | [Open Database License](https://opendatacommons.org/licenses/odbl/summary/) | Villes de France |
| [DBpedia](http://dbpedia.org) | [Creative Commons BY-SA 3.0](http://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License) | Événements |
| [DBpedia FR](http://fr.dbpedia.org) | [Creative Commons BY-SA 3.0](http://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License) | Capitales, préfectures, monuments et métro parisiens |
| [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/aires-et-produits-aoc-aop-et-igp/) | [Licence Ouverte](https://www.etalab.gouv.fr/wp-content/uploads/2014/05/Licence_Ouverte.pdf) | Spécialités, vins, fromages |
| [Wikidata](https://www.wikidata.org) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Régions naturelles |

[👉 Signaler un oubli](https://github.com/felix-martel/amstramdam/issues/new/choose)


## Installation & développement

Installation:
```
pip install -r requirements-full.txt
npm install
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

Lancement du front:
```shell
NODE_OPTIONS=--openssl-legacy-provider npm run watch
```

(L'option est nécessaire localement en attendant de mettre à jour les dépendances du projet)