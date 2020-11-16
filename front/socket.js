export default {
    install: (app, socketClient) => {
        app.config.globalProperties.$socketOn = (event, handler) => {
            socketClient.on(event, handler);
        }
        app.config.globalProperties.$socketEmit = (event, data) => {
            socketClient.emit(event, data);
        }
        console.log("Added `$socketOn` and `$socketEmit` to app!")
    }
}