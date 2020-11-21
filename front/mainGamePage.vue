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
      <result-popup></result-popup>
      <div class="column" id="left-column-display">
        <score-box></score-box>
        <chat-box :hidden="!panelVisibility.chatBox"></chat-box>
        <result-box v-if="showResults"></result-box>
      </div>

      <div class="right-corner" id="game-box">
        <game-state-box></game-state-box>
      </div>
      <map-container></map-container>
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
import ResultPopup from "./panels/resultPopup/resultPopup.vue";
import {goToHash, unproxify} from "./common/utils";
import {CookieHandler, IntCookieHandler} from "./common/cookie";
import {mapState} from "vuex";

export default {
    components: {
      'score-box': scoreBox,
      "chat-box": chatBox,
      "result-box": resultBox,
      "game-footer": gameFooter,
      "game-state-box": gameStateBox,
      "map-container": Map,
      "result-popup": ResultPopup,
    },
    data () {
      return {
        demo: "demo",
        params: {},
        visibleResults: false,
        highscoreCookie: undefined,
      }
    },

  computed: {
      panelVisibility () {
        return this.$store.state.ui;
      },

    ...mapState({
      showResults: state => {
        return ((state.game.status === constants.status.FINISHED)
            || (state.game.status === constants.status.CORRECTION)
            || ((state.game.status === constants.status.RUNNING)
                && (state.game.resultsReceived || state.guesses.length > 0)))
      }
    })
  },

  methods: {
      route: function() {
        const hash = window.location.hash;
        switch (hash) {
            case "#results":
              this.$store.commit("displayResultPopup");
              break;
            case "":
            default:
              this.$store.commit("hideResultPopup");
              break;
        }
      },

      routeToResults: function(){
        goToHash("#results");
      },

      routeToMain: function() {
        goToHash(" ");
      },

    updateHighScore(results) {
        const res = results.find(rec => (rec.player === this.$store.state.playerId));
        if (!res) { return }
        const latestScore = res.score;
        const currentHighScore = this.$store.state.score.high;
        if (!currentHighScore
          || (latestScore && latestScore > currentHighScore)) {
          // new high score!
          this.$store.commit("setNewHighScore", latestScore);
          console.log("New high score", latestScore);
          this.highscoreCookie.write(latestScore);
        }
    },
  },

    created () {
      const gameParams = unproxify(this.$store.state.params);
      console.log("Game params:", gameParams);
      this.highscoreCookie = new IntCookieHandler("amstramdam-" + gameParams.map);
      const highScore = this.highscoreCookie.read();
      if (highScore){
        console.log("Read high score from cookie", highScore);
        this.$store.commit("setHighScore", highScore);
      }

      this.route();

      window.addEventListener("popstate", event => {
        this.route();
      })
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
        this.$store.dispatch("initialize", data);
      },

      "new-player": function ({player, pseudo, score}) {
        if (player === this.$store.playerId) { return }
        this.$store.commit("addPlayer", {player, pseudo, score});
      },

      "game-end": function(data){
        this.$store.dispatch("setGameStatus", {
          status: constants.status.FINISHED,
          payload: data,
        });
        //this.routeToResults();
        this.updateHighScore(data.leaderboard);
      },

      "player-left": function ({player}) {
        console.debug("Bye,", this.getPlayerName(player));
        this.$store.commit("removePlayer", player);
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
        this.$store.commit("displayResultBox");
      },

      "new-guess": function ({player, dist}) {
        this.$store.commit("addGuess", {name: player, distance: Math.round(dist)});
      },

      "new-name": function({player, pseudo}) {
        console.debug(`Player <${player}> has a new nickname: "${pseudo}"`);
        this.$store.commit("renamePlayer", {id: player, pseudo: pseudo});
      },

      "status-update": function(data) {
        this.$store.dispatch("updateStatus", data);
      },
    }
}
</script>
<style>

</style>