<template>
  <div @keyup.alt.enter.prevent="showChatBox">
    <blink-component v-if="blinking"></blink-component>
    <div class="main">
      <game-footer v-if="!isMobile"></game-footer>
      <result-popup></result-popup>
      <div class="column" id="left-column-display">
        <div id="left-corner">
          <score-box></score-box>
          <transition name="slide">
            <div id="chat-box-container"  v-if="panelVisibility.chatBox">
              <chat-box></chat-box>
            </div>
          </transition>
        </div>
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
import gameFooter from "./ui/gameFooter/footer.vue";
import gameStateBox from "./panels/hintBox/gameStateBox.vue";
import Map from "./map/map.vue";
import constants from "./common/constants";
import ResultPopup from "./panels/resultPopup/resultPopup.vue";
import {goToHash, unproxify} from "./common/utils";
import {CookieHandler, IntCookieHandler} from "./common/cookie";
import {mapState} from "vuex";
import blinkComponent from "./components/blinkComponent.vue";

export default {
    components: {
      'score-box': scoreBox,
      "chat-box": chatBox,
      "result-box": resultBox,
      "game-footer": gameFooter,
      "game-state-box": gameStateBox,
      "map-container": Map,
      "result-popup": ResultPopup,
      "blink-component": blinkComponent,
    },
    data () {
      return {
        demo: "demo",
        params: {},
        visibleResults: false,
        // highscoreCookie: undefined,
      }
    },

  computed: {
      panelVisibility () {
        return this.$store.state.ui;
      },

    ...mapState({
      showResults: state => {
        return ((state.game.status === constants.status.CORRECTION)
            || ((state.game.status === constants.status.RUNNING)
                && (state.game.resultsReceived || state.guesses.length > 0)))
      },
      blinking: state => state.ui.blinking,
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

    showChatBox: function() {
      this.$store.commit("showChatBox");
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
          //
          // this.highscoreCookie.write(latestScore);
          this.$cookie.highScore.write(latestScore);
        }
    },
  },

    created () {
      const gameParams = unproxify(this.$store.state.params);
      if (this.$store.state.debug){
        console.debug("Game params:", gameParams);
      }

      const highScore = this.$cookie.highScore.read();
      if (highScore){
        this.$store.commit("setHighScore", highScore);
      }

      this.route();

      window.addEventListener("popstate", event => {
        this.route();
      })
    },

    events: {
      "connect": function () {
        // let pseudo; // TODO: read from cookie
        let pseudo = this.$cookie.pseudo.read();
        if (!pseudo) { pseudo = undefined}

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
        console.log("Received <event:game-end>")
        this.$store.dispatch("setGameStatus", {
          status: constants.status.FINISHED,
          payload: data,
        });
        //this.routeToResults();
        this.updateHighScore(data.leaderboard);
      },

      "game-change": function ({name, url, map_name, player}) {
        console.log(`Player '${this.getPlayerName(player)} created a new game at ${url}`);
        window.location = url;
      },

      "player-left": function ({player}) {
        console.debug("Bye,", this.getPlayerName(player));
        this.$store.commit("removePlayer", player);
      },

      "score": function (data){
        // TODO: store correct answer and add marker + circle
        this.$store.commit("setLastRun", {
          score: Math.round(data.score),
          distance: data.dist,
          sdistance: Math.round(data.sd),
          delay: Math.round(data.delta * 100) / 100,
          sdelay: Math.round(data.st)
        });
        this.$store.commit("displayResultBox");
      },

      "new-guess": function ({player, dist, score}) {
        this.$store.commit("addGuess", {name: player, distance: dist});
        if (score > 0) {
          this.$store.commit("addNotification", {
            type: constants.chatItemTypes.NOTIF_NEW_SCORE,
            player,
            score
          });
        }
      },

      "new-name": function({player, pseudo}) {
        console.debug(`Player <${player}> has a new nickname: "${pseudo}"`);
        this.$store.commit("renamePlayer", {id: player, pseudo: pseudo});
      },

      "status-update": function(data) {
        console.debug("main@status-change", data.status);
        this.$store.dispatch("updateStatus", data);
      },

      "chat:new": function(data){
        if (data.author !== this.$store.state.playerId){
          this.$store.commit("addMessage", data);
        }
      }
    }
}
</script>
<style>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.15s ease-out;
}

.slide-enter-from,
.slide-leave-to  {
  transform: translateX(-250px);
  opacity: 0.5;
}

.column {
  position: fixed;
  top: 20px;
  left: 20px;
    z-index: 1000;
  width: 250px;
}

#left-corner {
  position: relative;
}

#chat-box-container {
  position: absolute;
  top: 0;
  left: 270px;
  width: 250px;
  bottom: 0;
  z-index: -1;
}

.right-corner {
  position: fixed;
  top: 15px;
  right: 15px;
  z-index: 1000;
}

@media screen and (max-width: 600px) {
  .column {
    position: fixed;
    top: -5px;
    left: auto;
    right: -5px;
    bottom: auto;
    width: auto;
  }

  .right-corner {
    bottom: -5px;
    right: -5px;
    left: -5px;
    top: auto;
  }

  .right-corner .box {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: space-evenly;
    margin-bottom: 0;
  }
}
</style>