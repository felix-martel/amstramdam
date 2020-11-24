import {createStore} from "vuex";
import constants from "./common/constants";

const STATUS = constants.status;

function initScore(params) {
    return createStore({
        state() {
            return {
                params: params,
                //playerName: "",
                playerId: undefined,
                playerList: [],
                pseudos: {},
                leaderboard: [],
                playerParams: {
                    autozoom: true,
                    inverted: false
                },
                ui: {
                    // Panel visibility
                    chatBox: false,
                    scoreBox: true,
                    resultBox: false,
                    hintBox: false, // deprecated
                    resultPopup: false,
                    state: {
                        duration: -1,
                        transition: false,
                        hint: false,
                        message: "",
                    },
                    blinking: false,
                    blinkTimeout: undefined,
                },
                score: {
                    total: 0,
                    last: 0,
                    high: undefined,
                    newHigh: undefined,
                    beaten: false,
                },
                game: {
                    launched: false,
                    done: false,
                    hasAnswered: false,
                    resultsReceived: false,
                    currentRun: 0,
                    lastRun: -1,
                    currentPlace: "Paris",
                    currentHint: "France",
                    nRuns: undefined,
                    status: STATUS.NOT_LAUNCHED,
                    results: [],
                },
                chat: {
                    messages: [],
                    unread: false
                },
                lastRun: {
                    score: 0,
                    distance: 0,
                    sdistance: 0,
                    delay: 0,
                    sdelay: 0
                },
                guesses: []
            }
        },

        getters: {
            playerName (state) {
                return state.pseudos[state.playerId] || state.playerId
            },

            isMobile(state) {
                let check = false;
                (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
                return check;
            },

            autozoom(state, getters){
                return state.playerParams.autozoom && !getters.isMobile;
            },

            selfScore(state) {
                const selfResult = state.leaderboard.find(rec => (rec.player === state.playerId));
                if (selfResult) {
                    return selfResult.score || 0
                }
                return 0
            },

            finalScore(state, getters){
                if (state.game.status === constants.status.FINISHED) {
                    return getters.selfScore;
                } else {
                    return undefined;
                }
            },

            newHighScore(state, getters){
                const final = getters.finalScore;
                const high = state.score.high;
                return (typeof final !== "undefined" && (
                    typeof high === "undefined"
                    || final > high
                ));
            }
        },

        mutations: {
            updatePseudos (state, pseudos) {
                state.pseudos = pseudos;
            },

            resetCurrenRun (state) {
                state.game.currentRun = 0;
            },

            setGameResults(state, results) {
                state.game.results = results;
            },

            displayResultPopup(state) {
                state.ui.resultPopup = true;
            },

            hideResultPopup(state) {
                state.ui.resultPopup = false;
            },


            toggleResultPopup(state) {
                state.ui.resultPopup = !state.ui.resultPopup;
            },


            setCurrentRun(state, n) {
                state.game.currentRun = n;
            },


            incrementRun(state) {
                state.game.currentRun += 1;
            },

            setHint(state, {place, hint}) {
                state.game.currentPlace = place;
                state.game.currentHint = hint;
            },

            setNewHighScore(state, score) {
                state.score.newHigh = score;
                state.score.beaten = true;
            },

            resetHighScore(state) {
                if (state.score.beaten) {
                    state.score.high = state.score.newHigh;
                    state.score.newHigh = undefined;
                    state.score.beaten = false
                }
                //
            },

            setHighScore(state, score) {
                state.score.high = score;
            },

            setTotalRuns(state, n) {
                state.game.nRuns = n;
            },

            updateLeaderboard (state, leaderboard) {
                state.leaderboard = leaderboard;
            },

            setPlayer (state, playerId) {
                state.playerId = playerId;
            },

            updateParams (state, {key, value}) {
                // TODO: check key and value
                state.playerParams[key] = value;
            },

            addMessage (state, {author, message}) {
                const last = state.chat.messages[state.chat.messages.length - 1];
                if (last && last.author === author){
                    last.messages.push(message)
                }
                else {
                    state.chat.messages.push({
                        author: author,
                        messages: [message],
                        time: Date.now(),
                    })
                }
                // state.chat.messages.push({author, message, time: Date.now()});
                if (!state.ui.chatBox){
                    state.chat.unread = true;
                }
            },

            hideChatBox(state) {
                state.ui.chatBox = false;
            },

            showChatBox(state) {
                state.ui.chatBox = true;
                state.chat.unread = false;
            },

            setLastRun(state, {score, distance, sdistance, delay, sdelay}) {
                state.lastRun.score = score;
                state.lastRun.distance = distance;
                state.lastRun.sdistance = sdistance;
                state.lastRun.delay = delay;
                state.lastRun.sdelay = sdelay;
                state.game.resultsReceived = true;
                // state.ui.resultBox = true;
            },

            clearLastRun(state){
                state.game.resultsReceived = false;
                state.lastRun.score = 0;
                state.lastRun.distance = 0;
                state.lastRun.sdistance = 0;
                state.lastRun.delay = 0;
                state.lastRun.sdelay = 0;
            },

            addGuess(state, {name, distance}) {
                state.guesses.push({name, distance});
                // state.ui.resultBox = true;
            },

            clearGuesses(state) {
                state.guesses = []
            },

            setGameLaunched(state) {
                state.game.launched = true;
            },

            setGameNotLaunched(state) {
                state.game.launched = false;
            },

            setGameStatus(state, status){
                state.game.status = status;
            },

            startTransitionState(state, {message, duration=-1}) {
                state.ui.state.transition = true;
                state.ui.state.hint = false;
                state.ui.state.duration = duration;
                state.ui.state.message = message;
            },

            startHintState(state) {
                state.ui.state.transition = false;
                state.ui.state.hint = true;
                state.ui.state.duration = state.params.duration;
            },

            displayResultBox(state) {
                state.ui.resultBox = true;
            },

            hideResultBox(state) {
                state.ui.resultBox = false;
            },

            answerSubmitted(state) {
                state.game.hasAnswered = true;
            },

            answerRemoved(state) {
                state.game.hasAnswered = false;
            },

            startHiddenState(state, duration=-1) {
                state.ui.state.transition = false;
                state.ui.state.hint = false;
                state.ui.state.duration = duration;
            },

            emptyLeaderboard(state) {
                state.leaderboard.forEach(item => {
                    item.score = 0;
                    item.dist = 0;
                    item.delta = 0;
                });
            },

            addPlayer(state, {player, pseudo, score}) {
                if (state.leaderboard.find(item => item.player === player)) {
                    return
                }
                state.leaderboard.push(score);
                state.pseudos[player] = pseudo;
            },

            removePlayer(state, playerId) {
                const i = state.leaderboard.findIndex(rec => rec.player === playerId);
                if (i > 0) {
                    state.leaderboard.splice(i, 1);
                }
                if (playerId in state.pseudos){
                    delete[state.pseudos[playerId]];
                }
            },

            renamePlayer(state, {id, pseudo}) {
              state.pseudos[id] = pseudo;
            },

            startRunTimer(state) {
                const blinkDelay = 3; // in seconds
                state.ui.blinkTimeout = window.setTimeout(() => {
                    state.ui.blinking = true;
                }, (state.params.duration-blinkDelay) * 1000)
            },

            stopRunTimer(state) {
                if (typeof state.ui.blinkTimeout !== "undefined") {
                    window.clearTimeout(state.ui.blinkTimeout);
                    state.ui.blinkTimeout = undefined;
                }
                state.ui.blinking = false;
            }
        },

        actions: {
            toggleChatBox({state, commit}) {
                commit(state.ui.chatBox ? "hideChatBox" : "showChatBox")
            },

            startRun({state, commit}, {hint, runs}) {
                commit("startHintState");
                commit("hideResultBox");
                commit("answerRemoved");
                commit("clearGuesses");
                commit("clearLastRun");

                commit("setTotalRuns", runs);
                commit("incrementRun");
                commit("setHint", {place: hint});
            },

            resetState({state, commit}, data) {
                commit("hideResultBox");
                commit("clearGuesses");
                commit("clearLastRun");
                commit("resetHighScore");
                commit("resetCurrenRun");
                //commit("updateLeaderboard", []);
            },

            endGame({state, commit}, {leaderboard}) {
                commit("updateLeaderboard", leaderboard);
                //commit("setGameResults", full.results.summary);
                commit("displayResultPopup");
                // TODO: process high score
            },

            setGameStatus({state, commit, dispatch}, data) {
                let status, payload;
                if (typeof data === "string") {
                    status = data;
                    payload = undefined;
                }
                else {
                    status = data.status;
                    payload = data.payload;
                }
                const stat = constants.status;
                commit("setGameStatus", status);
                switch (status) {
                    case stat.NOT_LAUNCHED:
                        // do something
                        commit("setGameNotLaunched");
                        commit("startHiddenState");
                        break;
                    case stat.LAUNCHING:
                        console.log("Launching...");
                        commit("setGameLaunched");
                        dispatch("resetState", payload);
                        commit("startTransitionState", {
                            message: "Début de partie dans ",
                            duration: 3,
                        });
                        break;
                    case stat.RUNNING:
                        dispatch("startRun", {hint: payload.hint, runs: payload.total});
                        break;
                    case stat.CORRECTION:
                        const message = payload.done ?
                            constants.transitionText.beforeGameEnd :
                            constants.transitionText.beforeNewRun;
                        commit("startTransitionState", {
                            message: message,
                            duration: state.params.wait_time,
                        })
                        commit("updateLeaderboard", payload.leaderboard);
                        commit("displayResultBox");
                        break;
                    case stat.STOPPING:
                        break;
                    case stat.FINISHED:
                        dispatch("endGame", payload);
                        break;
                }
            },

            updateStatus({state, commit, dispatch}, {status, payload}) {
                const s = constants.status;
                const actions = {
                    [s.NOT_LAUNCHED]: "setNotLaunched",
                    [s.LAUNCHING]: "setLaunching",
                    [s.RUNNING]: "setRunning",
                    [s.CORRECTION]: "setCorrection",
                    [s.FINISHED]: "setFinished",
                }
                if (status in actions) {
                    dispatch(actions[status], payload);
                    commit("setGameStatus", status);
                } else {
                    console.warn(`Received invalid status: <${status}>`);
                }
            },

            setNotLaunched({state, commit, dispatch}, payload) {
                // Not sure this should exist, because we will never trigger
                // a <update-status:not-launched> event (we would trigger a
                // 'init' instead...
            },

            /**
             * Remove all traces of previous run:
             * - remove guesses from other players
             * - remove own results + scoring details
             * - clear map
             */
            clearAndHideResults({commit, state}) {
                // TODO: visibility of resultBox should be computed from hasAnswered and hasGuesses
                commit("hideResultBox");
                commit("clearGuesses");
                commit("clearLastRun");
                state.game.hasAnswered = false;
            },

            resetHighScore({state, commit, getters}) {
                if (getters.newHighScore){
                    state.score.high = getters.finalScore;
                }
            },

            setLaunching({state, commit, dispatch},
                         {game, runs, diff}) {
                state.game.currentRun = 1;
                state.game.nRuns = runs;
                state.game.launched = true;

                dispatch("resetHighScore");
                dispatch("clearAndHideResults");
                commit("emptyLeaderboard");
                commit("hideResultPopup");

                commit("startTransitionState", {
                    message: "Début de partie dans ",
                    duration: 3,
                });
            },

            /**
             * Start a new run:
             * - Remove traces from previous run (clear map...)
             * - Set new hint and new run number
             * - Display them
             * - Start the timer
             * - Start the blink timer
             *
             * @param hint: new run's hint
             * @param current: new run number
             * @param total: total run number
             */
            setRunning({state, commit, dispatch}, {hint, current, total}) {
                dispatch("clearAndHideResults");

                commit("setTotalRuns", total); // TODO: this should be set once (on init)
                commit("setCurrentRun", current + 1);
                commit("setHint", {place: hint});
                commit("startHintState");
                commit("startRunTimer");
            },

            /**
             * Start the correction step:
             * - Clear timer
             * - Display new message ("Run ended, next run in ...")
             * - Add guesses from other player (and display them?)
             * - Start timer for the correction step
             * - Update leaderboard with this run's scores
             * - Stop the blinking
             *
             * @param results
             * @param answer
             * @param leaderboard
             * @param done
             * @param payload
             */
            setCorrection({state, commit, dispatch},
                          {results, answer, leaderboard, done}) {
                commit("stopRunTimer");
                state.game.done = done;
                const message = done ?
                    constants.transitionText.beforeGameEnd :
                    constants.transitionText.beforeNewRun;
                commit("startTransitionState", {
                    message: message,
                    duration: state.params.wait_time,
                });
                commit("updateLeaderboard", leaderboard);
                commit("displayResultBox");
            },

            /**
             * Enter the finished state:
             * - Get the final leaderboard
             * - Get the final score for this game
             * - Set the game to 'not launched' (=> set 'launchable' to true)
             * - Disable answers?
             * - Display results popup
             * - (future) Display game summary
             *
             * @param leaderboard
             */
            setFinished({state, commit, dispatch}, {leaderboard, full}) {
                commit("updateLeaderboard", leaderboard);
                commit("displayResultPopup");
                console.log(full);
                state.game.hasAnswered = false;
            },

            initialize({state, commit, dispatch},
                       {player, pseudos, current, runs, launched, leaderboard}) {
                state.pseudos = pseudos;
                state.playerId = player;
                state.game.currentRun = current + 1;
                state.game.nRuns = runs;
                state.leaderboard = leaderboard;
                state.launched = launched;
                commit("startHiddenState");

                state.game.launched = launched;
            },
        }
    })
}

export default initScore;