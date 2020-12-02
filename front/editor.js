import "leaflet/dist/leaflet.css";
import {createApp} from "vue";
import AmstramdamLobby from "./mainLobbyPage.vue";
import datasetEditor from "./datasetBuilder/datasetEditor.vue";

document.addEventListener("DOMContentLoaded", () => {
    const app = createApp(datasetEditor);

    app.mount("#amstramdam-builder");
});