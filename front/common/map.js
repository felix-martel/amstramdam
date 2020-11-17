import "leaflet/dist/leaflet.css";
import L from "leaflet";

const LAYERS = {
    default: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    alt: 'https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
    watercolor: 'http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
    terrain: 'http://c.tile.stamen.com/terrain-background/{z}/{x}/{y}.jpg',
    bw: 'http://tile.stamen.com/toner-background/{z}/{x}/{y}.png',
    bwSSL: 'https://stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png'
};

const CREDITS = `Map tiles by <a href="http://stamen.com">Stamen Design</a>,
under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.
Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,
under <a href="http://www.openstreetmap.org/copyright">ODbL</a> and
<a href="https://simplemaps.com/data/world-cities">World Cities Database</a>
under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>`;


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



const defaultView = {
        center: [23.7, 7.6],
        zoom: 1
    };

export {
    LAYERS, CREDITS, getIcon, defaultView
}