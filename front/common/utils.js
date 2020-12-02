/**
 * Wrapper around `document.getElementById`
 *
 * @param identifier
 * @returns {HTMLElement}
 */
export function $(identifier){
    return document.getElementById(identifier);
}

/**
 * Make an AJAX GET request and return a Promise
 *
 * @param url
 * @returns {Promise}
 */
export function GET(url) {
    return new Promise(((resolve, reject) => {
        const req = new XMLHttpRequest();
        req.onreadystatechange = () => {
            if (req.readyState === 4 && req.status === 200) {
                const data = JSON.parse(req.responseText);
                resolve(data);
            }
            else if (req.readyState === 4 && req.status >= 400) {
                console.log("Invalid response received");
                console.log(req);
                reject(req);
            }
        }
        req.open("GET", url, true);
        req.send(null);
    }))
}

export function POST(url, data) {
    return new Promise((resolve, reject) => {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200){
                const data = JSON.parse(xhr.responseText);
                resolve(data);
            } else if (xhr.readyState === 4 && xhr.status >= 400) {
                console.warn("Invalid response received for", url);
                reject(xhr)
            }
        }
    })

}

export const NamingMixin = {
    methods: {
        getPlayerName (id) {
            return this.$store.state.pseudos[id] || id;
        }
    }
}

/**
 * Register custom handler for socketio events when defining a component. Example:
 * export default {
 *     data () {
 *         return {
 *             connected: false
 *         }
 *     },
 *     events: {
 *         'connect': function () {
 *             this.connected = true
 *         }
 *     }
 * }
 * @type {{created(): void}}
 */
export const EventRegistrationMixin = {
    created() {
        const hasSocketIO = (typeof this.$socketOn!== "undefined");
        const hasEvents = (typeof this.$options.events !== "undefined");
        if (hasSocketIO && hasEvents) {
            for (const [event, handler] of Object.entries(this.$options.events)) {
                this.$socketOn(event, handler.bind(this));
            }
        }
    }
}

export function goToHash (url, state = {}) {
    history.pushState(state, '', url);
    const popStateEvent = new PopStateEvent('popstate', { state: state });
    dispatchEvent(popStateEvent);
}

export function unproxify (obj) {
    return Object.assign({}, obj);
}

export function geoJitter(lonlatObject, {how="gaussian", lonFactor=10, latFactor=5}={}) {
    const rand = (how === "gaussian") ? (() => {
        // Gaussian N(0, 1)
        let u = 0, v = 0;
        while(u === 0) u = Math.random(); //Converting [0,1) to (0,1)
        while(v === 0) v = Math.random();
        return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
    }) : (() => {
        // Uniform U(-1, +1)
        return 2 * (Math.random() - 0.5);
    });
    return {
        //...lonlatObject,
        lon: lonlatObject.lon + lonFactor * rand(),
        lat: lonlatObject.lat + latFactor * rand(),
    }
}


export const VueSelectCompatibilityPlugin = {
    install: (app) => {
        app.config.globalProperties.$on = function(e) {
            console.log(e);
        }
    }
}
