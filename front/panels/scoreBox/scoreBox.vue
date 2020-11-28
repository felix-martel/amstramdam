<template>
  <div class="box" id="main-info-box">
    <div class="nav">
      <a href="/">Accueil</a><span></span>
      <i class="fas fa-comments"
         id="chat-toggle-button"
         :class="{'unread-message': unreadMessages}"
         @click="toggleChatBox"></i>
    </div>
    <score-box-self></score-box-self>

    <div class="ranking">
      <score-box-ranking></score-box-ranking>
      <div class="controls">
        <button v-if="canViewResults"
          @click="openResultPopup"
          >
          Résultats
        </button>
        <button id="launch"
                v-if="!launched"
                @click="launchGame"
                :disabled="launched"
        >{{ launchButtonLabel }}
        </button>
      </div>
    </div>
  </div>
</template>
<script>
import {mapState} from "vuex";
import scoreBoxSelf from "./scoreBoxSelf.vue";
import scoreBoxRanking from "./scoreBoxRanking.vue";
import constants from "../../common/constants.js";

export default {
  components: {
    "score-box-self": scoreBoxSelf,
    "score-box-ranking": scoreBoxRanking,
  },
  methods: {
    launchGame(e) {
      e.preventDefault();
      e.stopPropagation();
      if (!this.launched) {
        this.$socketEmit("launch");
      }
    },

    toggleChatBox() {
      this.$store.dispatch("toggleChatBox");
    },

    openResultPopup() {
        if (this.canViewResults){
            this.$store.commit("hideGameCreator");
            this.$store.commit("displayResultPopup");
        }
      }
  },

  computed: {
    launchButtonLabel() {
      return this.$store.state.firstLaunch ? "Commencer" : "Recommencer"
    },
    score () {
      return this.$store.state.score.total
    },

    highScore () {
      return this.$store.state.score.high
    },

    diffScore () {
      const state = this.$store.state;
      if (!this.highScore || typeof this.score === "undefined" || !state.game.launched){
        return ""
      }
      const currHigh = (state.score.high / state.game.nRuns) * state.game.currentRun;
      return Math.round(this.score - currHigh);
    },

    launched () {
      return this.$store.state.game.launched;
    },

    playerName () {
      return this.$store.getters.playerName
    },

    unreadMessages () {
      return this.$store.state.chat.unread;
    },
    canViewResults() {
      return this.$store.state.game.status === constants.status.FINISHED
    },

    ...mapState(["leaderboard"])
  }
}
</script>
<style scoped>
.nav {
  text-align: left;
  margin-bottom: 15px;
  margin-top: -10px;
  color: blue;
}
.nav a, .nav a:visited, .nav a:active, .nav a:link {
  color: blue;
}


.controls {
  position: relative;
}

.controls button {
  margin-right: 5px;
}

#chat-toggle-button {
  position: absolute;
  top: 15px;
  right: 19px;
  color: blue;
  cursor:pointer;
}
#chat-toggle-button.unread-message:after {
  display: block;
  width: 6px;
  height:6px;
  border-radius: 3px;
  background: red;
  content: " ";
  position: absolute;
  top: 0;
  right: 0;
}
#chat-toggle-button:hover {
  color: #000085;
}

@media screen and (max-width: 600px) {
    #launch:not(:disabled) {
      z-index: 1001;
    }
}
</style>