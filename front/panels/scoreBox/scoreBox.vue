<template>
  <div class="box" id="main-info-box">
    <div class="nav">
      <a href="/">Accueil</a><span></span>
    </div>
    <div class="self">
      <div class="name" id="player-name">{{ playerName || 'Non connecté'}}</div>
      <div class="total-score"><span id="total-score">{{ score }}</span> pts</div>
      <div class="high-score no-score" id="high-score-container">
        <i class="fas fa-trophy"></i>
        <span id="high-score">{{ highScore }}</span>pts
        <span id="high-score-diff" class="no-score">{{ diffScore }}</span>
      </div>
    </div>

    <div class="ranking">
      <ul id="player-list">
        <li v-for="el in leaderboard">
          <span class="pname">{{ getPlayerName(el.player) }}</span>
          <span class="pscore">{{el.score}} pts</span>
        </li>
      </ul>
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

export default {
  methods: {
    launchGame(e) {
      console.log("Launch");
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