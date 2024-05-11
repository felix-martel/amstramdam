import "leaflet/dist/leaflet.css";
import L from "leaflet";

import {$, GET} from "./common/utils";
import {LAYERS, getIcon, defaultView} from "./common/map";

import {createApp} from "vue";
import AmstramdamLobby from "./mainLobbyPage.vue";
import {MobileDetectionMixin} from "./plugins/mobileDetectionPlugin.js";

const USE_VUE = true;

if (USE_VUE) {
    document.addEventListener("DOMContentLoaded", () => {
        const app = createApp(AmstramdamLobby, {datasets, games, appConfig});
        app.mixin(MobileDetectionMixin);

        app.mount("#amstramdam-lobby");
    });
} else
{
    document.addEventListener("DOMContentLoaded", () => {
        const difficultySlider = $("diff-level");
        const gameNameInput = $("game-name");
        const gameJoinButton = $("join-game-button");
        const gameSelector = $("map-selector");

        /* MAP INITIALISATION */
        const map = L.map('leaflet').setView(defaultView.center, defaultView.zoom);
        const OSM = L.tileLayer(LAYERS.bwSSL, {zoomControl: false,});
        OSM.addTo(map);
        // Data points will be added to this layer later
        let pointLayer = L.featureGroup();
        pointLayer.addTo(map);

        // Initialize view when page loads
        updateView();

        // Changes on the game selector
        gameSelector.addEventListener("change", () => {
            updateView();
        });

        // Click on 'Join Game' button
        gameJoinButton.addEventListener("click", (e) => {
            e.preventDefault();
            const rawInput = gameNameInput.value;
            const gameName = rawInput.charAt(0).toUpperCase() + rawInput.slice(1).toLowerCase();
            window.location.href = `/game/${gameName}`;
        });

        // Update map when difficulty changes
        difficultySlider.addEventListener("change", () => {
            updateDifficulty();
        });

        // When typing enter in the `gameNameInput`
        gameNameInput.addEventListener("keydown", function (event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                gameJoinButton.click();
            }
        });

        /**
         * Update the map depending on the current game parameters:
         * - remove existing points
         * - retrieve relevant data points from the server
         * - add them to the map
         * - fit the map to the points
         */
        function updateView() {
            if (pointLayer) {
                map.removeLayer(pointLayer);
            }
            const dataset = gameSelector.value;
            GET(`/points/${dataset}`).then((data) => {
                pointLayer = L.featureGroup();
                const diff = difficultySlider.value / 100;
                const maxRank = Math.min(10, diff * data.points.length);
                data.points.forEach(point => {
                    const extraClass = (point.rank > maxRank) ? "hidden" : "";
                    let pointMarker = L.marker(point.coords, {icon: getIcon("blue", extraClass)});
                    pointMarker.rank = point.data.rank;
                    pointLayer.addLayer(pointMarker);
                });
                const bounds = pointLayer.getBounds();
                pointLayer.addTo(map);
                map.flyToBounds(bounds);
            });
        }


        /**
         * Update map (and more precisely, points) depending on current difficulty parameter
         */
        function updateDifficulty() {
            if (pointLayer) {
                const diff = difficultySlider.value / 100;
                const nLayers = pointLayer.getLayers().length;
                const maxRank = Math.max(10, diff * nLayers);

                pointLayer.eachLayer(point => {
                    if (point.rank > maxRank) {
                        point._icon.classList.add("hidden");
                    } else {
                        point._icon.classList.remove("hidden");
                    }
                })
            }
        }

    })
}