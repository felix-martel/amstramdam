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
                 {labelOnly = false,
                     random = false,
                 extraClasses = []
                 } = {}){
        const iconColor = labelOnly ? "transparent" : color;
        const markerHtmlStyles = `
          background: ${iconColor};
          width: 10px;
          height: 10px;
          display: block;
          border-radius: 5px;`;
        var inner;
        if (name) {
            let x = 15;
            let y = 15;
            if (random){
                x = 2* (Math.random()-0.5);
                y = Math.sqrt(1 - Math.pow(x, 2));
                if (Math.random() > 0.5){
                    y = -y;
                }
                x = Math.round((15 + 15*Math.random())*x);
                y = Math.round((15 + 15*Math.random())*y);
            }
            const labelStyle = `
            background-color: ${color};
            color: white;
            padding: 3px;
            top: ${x}px;
            left: ${y}px;
            position: absolute;
            font-family: "Roboto", monospace;
            `;
            inner = `<span class="icon-label" style="${labelStyle}">${name}</span>`;
        }
        else {
            inner = "";
        }
        const classes = extraClasses.join(" ");

        return L.divIcon({
            className: "my-custom-pin",
            iconAnchor: [5, 5],
            html: `<span class="icon ${classes}" style="${markerHtmlStyles}">${inner}</span>`
        })
    }

function oldGetIcon(color="red", extraClass="", opacity=0.8){
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

const defaultBounds = [
    [66.95, 179.2166],
    [-54.2806, -178.1583]
];

export {
    LAYERS, CREDITS, CREDITS_SHORT, getIcon, defaultView, defaultBounds
}