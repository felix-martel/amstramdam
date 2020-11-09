import {$} from "./utils";

document.addEventListener("DOMContentLoaded", () => {
    const LAYERS = {
        default: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        alt: 'https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
        watercolor: 'http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
        terrain: 'http://c.tile.stamen.com/terrain-background/{z}/{x}/{y}.jpg',
        bw: 'http://tile.stamen.com/toner-background/{z}/{x}/{y}.png',
        bwSSL: 'https://stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png'
    };
    const defaultView = {
            center: [23.7, 7.6],
            zoom: 1
        };
    const difficultySlider = $("diff-level");

    function getIcon(color="red", extraClass="", opacity=0.8){
        const markerHtmlStyles = `
          background: ${color};
          width: 6px;
          height: 6px;
          display: block;
          border-radius: 3px;`;

        return L.divIcon({
            className: "my-custom-pin",
            iconAnchor: [3, 3],
            html: `<span class="icon ${extraClass}" style="${markerHtmlStyles}"></span>`
        })
    }


     var map = L.map('leaflet').setView(defaultView.center, defaultView.zoom);
     var OSM = L.tileLayer(LAYERS.bwSSL, {zoomControl:  false, });
     OSM.addTo(map);

     /* HANDLE DATA POINTS */
     var pointLayer = L.featureGroup();
    pointLayer.addTo(map);

    const gameSelector = document.getElementById("map-selector");
    function GET(theUrl, callback)
    {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
                callback(JSON.parse(xmlHttp.responseText));
        };
        xmlHttp.open("GET", theUrl, true); // true for asynchronous
        xmlHttp.send(null);
    }

    function updateView(){
        if (pointLayer){
            map.removeLayer(pointLayer);
        }
        const dataset = gameSelector.value;
        GET(`/points/${dataset}`, (data) => {
            pointLayer = L.featureGroup();
            var diff = difficultySlider.value / 100;
            var maxRank = Math.min(10, diff * data.points.length);
            data.points.forEach(point => {
                var extraClass = (point.rank > maxRank) ? "hidden" : "";
                var pointMarker = L.marker(point.coords, {icon: getIcon("blue", extraClass)});
                pointMarker.rank = point.data.rank;
                pointLayer.addLayer(pointMarker);
            });
            const bounds = pointLayer.getBounds();
            pointLayer.addTo(map);
            map.flyToBounds(bounds);

        });
    }

    gameSelector.addEventListener("change", () => {
        updateView();
    });

    function updateDifficulty(){
        if (pointLayer){
            var diff = difficultySlider.value / 100;
            var minValue = 0;
            var nLayers = pointLayer.getLayers().length;
            var maxRank = Math.max(10, diff * nLayers);

            pointLayer.eachLayer(point => {
                if (point.rank > maxRank){
                    point._icon.classList.add("hidden");
                } else {
                    point._icon.classList.remove("hidden");
                }
            })
        }
    }
    updateView();
    var gameNameInput = document.getElementById("game-name");
    var gameJoinButton = document.getElementById("join-game-button");
    gameNameInput.addEventListener("keydown", function(event){
        if (event.keyCode === 13){
            event.preventDefault();
            gameJoinButton.click();
        }
    });
    gameJoinButton.addEventListener("click", (e) => {
        e.preventDefault();
        const rawInput = gameNameInput.value;
        const gameName = rawInput.charAt(0).toUpperCase() + rawInput.slice(1).toLowerCase();
        window.location.href = `/game/${gameName}`;
    });
    difficultySlider.addEventListener("change", (e) => {
        updateDifficulty();
    });
})