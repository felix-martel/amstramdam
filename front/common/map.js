import "leaflet/dist/leaflet.css";
import L from "leaflet";

const LAYERS = {
    default: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    alt: 'https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
    watercolor: 'http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
    terrain: 'http://c.tile.stamen.com/terrain-background/{z}/{x}/{y}.jpg',
    labelled: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    terrainSSL: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
    bw: 'http://tile.stamen.com/toner-background/{z}/{x}/{y}.png',
    bwSSL: 'https://tiles.stadiamaps.com/tiles/stamen_toner_background/{z}/{x}/{y}{r}.png',
    satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
};

const CREDITS = `Map tiles by <a href="http://stamen.com">Stamen Design</a>,
under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.
Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,
under <a href="http://www.openstreetmap.org/copyright">ODbL</a> and
<a href="https://simplemaps.com/data/world-cities">World Cities Database</a>
under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>`;

const CREDITS_SHORT = `Credits: <a href="http://stamen.com">Stamen</a> and <a href="https://github.com/felix-martel/amstramdam">more</a>`;

function jitter(X, Y, amount=15){
    x = 2* (Math.random()-0.5);
    y = Math.sqrt(1 - Math.pow(x, 2));
    if (Math.random() > 0.5){
        y = -y;
    }
    x = Math.round(X * (1 + Math.random()*x));
    y = Math.round(Y * (1 + Math.random()*y));
    return [x, y];
}


function getIcon(color= "red",
                 name= "",
                 {
                     labelOnly = false,
                     random = false,
                     extraClasses = [],
                     small = false,
                 } = {}){
    const iconColor = labelOnly ? "transparent" : color;
    const html = name ?  `<span class="icon-label">${name}</span>` : "";
    const className = extraClasses.concat(["ams-icon", iconColor]).join(" ");
    const iconSize = small ? 5 : 10;
    return L.divIcon({
        className,
        iconSize,
        html
    })
}



const defaultView = {
        center: [23.7, 7.6],
        zoom: 1
    };

const defaultBounds = [
    [66.95, 179.2166],
    [-54.2806, -178.1583]
];

export {
    LAYERS, CREDITS, CREDITS_SHORT, getIcon, defaultView, defaultBounds
}
