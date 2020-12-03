import { createApp } from 'vue'
import io from "socket.io-client";
import 'leaflet/dist/leaflet.css';

// Plugins and mixins
import initStore from './store';
import SocketIOPlugin from "./socket";
import {NamingMixin, EventRegistrationMixin} from "./common/utils";
import {MobileDetectionMixin} from "./plugins/mobileDetectionPlugin.js";
import {CookieHandler, IntCookieHandler, CookiePlugin} from "./common/cookie";

// Components
import AmstramdamApp from "./mainGamePage.vue";
import PopupComponent from "./components/popup.vue";

document.addEventListener("DOMContentLoaded", () => {
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
    app.component("popup", PopupComponent);

    // Mount!
    app.mount('#amstramdam');
});