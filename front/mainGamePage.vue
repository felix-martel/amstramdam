<template>
  <div>
    <div class="blink-wrapper off" id="blink-wrapper">
        <div class="blink-item" id="left"></div>
        <div class="blink-item" id="right"></div>
        <div class="blink-item" id="top"></div>
        <div class="blink-item" id="bottom"></div>
    </div>
    <div class="main">
        <game-footer></game-footer>
        <div class="popup-container" id="popup-container" hidden>
            <div id="mask">

            </div>
            <div id="popup" class="box">
                <div class="popup-left">
                    <div class="box no-border" id="chat-box-popup">
                    <div class="inner-chat">

                        <div class="messages-wrapper">
                            <div id="chat-messages-popup" class="chat-messages">

                            </div>

                        </div>
                        <div class="input">
                            <textarea name="chat-input" id="chat-input-popup" class="chat-input" placeholder="Envoyez un message"></textarea>
                        </div>
                        </div>
                    </div>
                </div>
                <div class="popup-main">
                    <h2 class="blue">Partie terminée</h2>
                    <h4 class="high-score-notif no-score" id="new-highscore-notif">C'est votre meilleur score !</h4>
                <table id="final-results">

                </table>
                <button id="relaunch-from-popup">Nouvelle partie</button>
                <div style="margin-top:15px;">
                    <a  href="/">
                        Retour à l'accueil
                    </a>
                </div>
                </div>

            </div>
        </div>
      <div class="column" id="left-column-display">
        <score-box></score-box>
        <chat-box :hidden="!panelVisibility.chatBox"></chat-box>
        <result-box :hidden="!panelVisibility.resultBox"></result-box>
      </div>

        <div class="right-corner" id="game-box">
            <game-state-box></game-state-box>
        </div>
      <map-container></map-container>
<!--        <div id="mapid"></div>-->
        <!--<audio id="beep" hidden src="[[ url_for('static',filename='bip.mp3') ]]"></audio>-->
    </div>
  </div>
</template>
<script>
//import store from "./store"
import scoreBox from "./panels/scoreBox/scoreBox.vue";
import chatBox from "./panels/chatBox/chatBox.vue";
import resultBox from "./panels/resultBox/resultBox.vue";
import gameFooter from "./ui/footer.vue";
import gameStateBox from "./panels/hintBox/gameStateBox.vue";
import Map from "./ui/map.vue";
import constants from "./common/constants";

export default {
    components: {
      'score-box': scoreBox,
      "chat-box": chatBox,
      "result-box": resultBox,
      "game-footer": gameFooter,
      "game-state-box": gameStateBox,
      "map-container": Map
    },
    data () {
      return {
        demo: "demo",
        params: {},
      }
    },

  computed: {
      panelVisibility () {
        return this.$store.state.ui;
      }
  },

    created () {
      const gameParams = Object.assign({}, this.$store.state.params);
      console.log("Game params:", gameParams);
    },

    events: {
      "connect": function () {
        let pseudo; // TODO: read from cookie
        console.debug("Connecting... Current pseudo is", pseudo);
        this.$socketEmit("connection", {data: "connected", pseudo: pseudo});
      },

      "log": function (data) {
        console.log(data);
      },

      "init": function (data) {
        console.debug(`You're now connected as <${data.pseudo}> (id=${data.player})`);
        this.$store.commit("updatePseudos", data.pseudos);
        this.$store.commit("setPlayer", data.player);
      },

      "new-player": function ({leaderboard, pseudos}) {
        this.$store.commit("updatePseudos", pseudos);
        this.$store.commit("updateLeaderboard", leaderboard);
      },

      "game-launched": function (data) {
        // TODO: retrieve high score
        console.debug("Received <game-launched>");
        const {game, runs, diff} = data;

        this.$store.dispatch("setGameStatus", constants.status.LAUNCHING);
      },

      "run-start": function (data) {
        this.$store.dispatch("setGameStatus", {
          status: constants.status.RUNNING,
          payload: data,
        });
      },

      "run-end": function (data) {
        this.$store.dispatch("setGameStatus", {
          status: constants.status.CORRECTION,
          payload: data
        });
      },

      "player-left": function ({player, leaderboard}) {
        console.debug("Bye,", player);
        this.$store.commit("updateLeaderboard", leaderboard);
      },

      "score": function (data){
        // TODO: store correct answer and add marker + circle
        this.$store.commit("setLastRun", {
          score: Math.round(data.score),
          distance: Math.round(data.dist),
          sdistance: Math.round(data.sd),
          delay: Math.round(data.delta * 100) / 100,
          sdelay: Math.round(data.st)
        });
      },

      "new-guess": function ({player, dist}) {
        this.$store.commit("addGuess", {name: player, distance: Math.round(dist)});
      },

      "new-name": function({change, pseudos}) {
        console.log(`Player <${change.player}> has a new nickname: "${change.pseudo}"`);
        this.$store.commit("updatePseudos", pseudos);
      }
    }
}
</script>
<style>

</style>