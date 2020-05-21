# am·stram·dam

*Le jeu original est accessible ici : [jeux-geographiques.com](https://www.jeux-geographiques.com/)*

Le but est de localiser des villes de France et du monde le plus précisément et le plus rapidement possible, 
sur le modèle de Jeux Géographiques. Hébergé par Heroku à l'adresse [amstramdam.com](https://www.amstramdam.com). 

Fonctionne avec `Python 3.8`, `Flask` et `SocketIO`. Le serveur est géré par `eventlet` 
et les fonds de carte proviennent de 
[Stamen](http://maps.stamen.com/#toner/12/37.7706/-122.3782)+[OpenStreetMap](http://openstreetmap.org/).

## Installation & développement

Installation:
```
pip install -r requirements.txt
```

Lancement du serveur 
```
python server.py [--debug] [--threading]
```
Le flag `--debug` lance le serveur Flask de débug, avec auto-reload et débugger. Sinon, `eventlet` est utilisé et peut suffire en production.


## À faire

- [x] Traduire l'interface en français

- [x] Bug: répétition de certaines vilels

- [x] Ré-équilibrer le dataset France

- [x] Zoomer sur les résultats à la fin d'une manche

- [x] Multi-room support

- [x] Editable player names

- [x] Add more countries/regions

- [ ] Add custom games (choose map boundaries, and select all cities in the bbox)

- [x] Add proper locks for multithreading (not needed with `eventlet` apparently)

- [x] Add a `home` link in results page

- [x] Mobile version

- [x] Fix HTTPS issue

- [x] Add a timer when launching a game ("game will start in 3..2..1")

- [x] Disable/fix zoom animations on mobile

- [ ] Add a "Signaler un bug" button, linking to [the project issue page](https://github.com/felix-martel/multigeo/issues/new)

