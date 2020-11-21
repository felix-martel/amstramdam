<template>
  <div class="box" id="main-info-box">
    <div class="nav">
      <a href="/">Accueil</a><span></span>
    </div>
    <score-box-self></score-box-self>

    <div class="ranking">
      <score-box-ranking></score-box-ranking>
      <div class="controls">
        <button id="launch" @click="launchGame">Commencer</button>
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
      if (!this.$store.state.game.launched) {
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