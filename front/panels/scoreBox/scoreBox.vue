<template>
  <div class="box" id="main-info-box">
    <div class="nav">
      <a href="/">Accueil</a><span></span>
    </div>
    <score-box-self></score-box-self>

    <div class="ranking">
      <score-box-ranking></score-box-ranking>
      <div class="controls">
        <button id="launch"
                @click="launchGame"
                :disabled="launched"
        >Commencer</button>
        <i class="fas fa-comments"
           id="chat-toggle-button"
           :class="{'unread-message': unreadMessages}"
           @click="toggleChatBox"></i>
      </div>
    </div>
  </div>
</template>
<script>
import {mapState} from "vuex";
import scoreBoxSelf from "./scoreBoxSelf.vue";
import scoreBoxRanking from "./scoreBoxRanking.vue";

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
    }
  },

  computed: {
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


#chat-toggle-button {
  position: absolute;
  top: 2px;
  right: 0;
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
</style>