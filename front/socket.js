export default {
    install: (app, socketClient) => {
        app.config.globalProperties.$socketOn = (event, handler) => {
            socketClient.on(event, handler);
        }
        app.config.globalProperties.$socketEmit = (event, data) => {
            if (typeof data === "undefined") {
                socketClient.emit(event);
            } else {
                socketClient.emit(event, data);
            }
        }
    }
}