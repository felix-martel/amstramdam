import {CountUp} from "countup.js";
import Countdown from "./ui/countdown";
import AmstramdamApp from "./mainGamePage.vue";

import { createApp } from 'vue'
import io from "socket.io-client";
//import store from './store';
import initStore from './store';
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import SocketIOPlugin from "./socket";
import {NamingMixin} from "./common/utils";
//import {$} from "./common/utils";



document.addEventListener("DOMContentLoaded", () => {
    const socket = io({
        rejectUnauthorized: false, // !params.debug,
    });
    const app = createApp(AmstramdamApp)
    const istore = initStore(params);
    app.use(istore);
    app.use(SocketIOPlugin, socket);
    app.mixin(NamingMixin);

    app.mount('#amstramdam');
});