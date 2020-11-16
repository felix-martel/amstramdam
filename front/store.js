import {createStore} from "vuex";

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
                    hintBox: true,
                    resultPopup: false,
                },
                score: {
                    total: 0,
                    last: 0,
                    high: undefined
                },
                game: {
                    launched: false,
                    currentRun: 0,
                    nRuns: undefined,
                },
                chat: {
                    messages: [],
                    unread: false
                }
            }
        },

        getters: {
            playerName (state) {
                return state.pseudos[state.playerId] || state.playerId
            }
        },

        mutations: {
            updatePseudos (state, pseudos) {
                state.pseudos = pseudos;
            },

            setPlayer (state, playerId) {
                state.playerId = playerId;
            },

            updateParams (state, {key, value}) {
                // TODO: check key and value
                state.playerParams[key] = value;
            },

            addMessage (state, {author, message}) {
                state.chat.messages.push({author, message, time: Date.now()});
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
        },

        actions: {
            toggleChatBox({state, commit}) {
                commit(state.ui.chatBox ? "hideChatBox" : "showChatBox")
            }
        }
    })
}

export default initScore;