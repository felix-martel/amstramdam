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
