export default {
    colors: {
        TRUE: "blue",
        SELF: "red",
        BASE: "purple"
    },
    animations: {
        map: {
            duration: 0.5,
            deltaPad: 0.5,
        },
    },
    status: {
        NOT_LAUNCHED: "not-launched",
        LAUNCHING: "before-start",
        RUNNING: "running",
        CORRECTION: "correction",
        STOPPING: "before-stop",
        FINISHED: "finished",
    },
    transitionText: {
         beforeNewRun: "Prochaine manche dans ",
         beforeGameEnd: "Partie finie, palmarès dans ",
         beforeGameStart: "Début de partie dans "
     },
    chatItemTypes: {
        MESSAGE: "message",
        NOTIFICATION: "notification",
        NOTIF_NEW_SCORE: "notif-new-score",
        NOTIF_LAUNCH: "notif-launch",
        NOTIF_RELAUNCH: "notif-relaunch",
        NOTIF_WINNER: "notif-winner",
        NOTIF_NEW_HINT: "notif-new-hint",
    }
}