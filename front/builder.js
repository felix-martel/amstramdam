import "leaflet/dist/leaflet.css";
import {createApp} from "vue";
import AmstramdamLobby from "./mainLobbyPage.vue";
import datasetBuilder from "./datasetBuilder/datasetBuilder.vue";

document.addEventListener("DOMContentLoaded", () => {
    const app = createApp(datasetBuilder);

    app.mount("#amstramdam-builder");
});