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
import {NamingMixin, EventRegistrationMixin} from "./common/utils";
//import {$} from "./common/utils";
import popup from "./components/popup.vue";
import {CookieHandler, BooleanCookieHandler, IntCookieHandler, CookiePlugin} from "./common/cookie";
import {MobileDetectionMixin} from "./plugins/mobileDetectionPlugin.js";

document.addEventListener("DOMContentLoaded", () => {
    const rejectUnauthorized = !params.debug && !params.ssl_disabled;
    const protocol = params.ssl_disabled ? "ws" : "wss";
    const url = `${protocol}://${window.location.host}`; // "ws://" + window.location.host;//.replace("https://", "http://");
    const socket = io({
        rejectUnauthorized: true,
    });
    const app = createApp(AmstramdamApp)

    // Setup plugins
    const istore = initStore(params);
    app.use(istore);
    app.use(SocketIOPlugin, socket);
    app.use(CookiePlugin, {
        pseudo: new CookieHandler("amstramdam-pseudo"),
        highScore: new IntCookieHandler( `ams-hs-${params.map}-${params.difficulty}`)
    });

    // Register mixins
    app.mixin(NamingMixin);
    app.mixin(EventRegistrationMixin);
    app.mixin(MobileDetectionMixin);

    // Register components
    app.component("popup", popup);

    // Mount!
    app.mount('#amstramdam');
});