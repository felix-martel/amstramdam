<template>
<div class="self">
      <div class="name" id="player-name" :contenteditable="nameExists"
      @keydown.enter="updateName" @focusout="updateName">
        {{ playerName || 'Non connecté'}}
      </div>
      <div class="total-score"><span id="total-score">{{ score }}</span> pts</div>
      <div class="high-score no-score" id="high-score-container">
        <i class="fas fa-trophy"></i>
        <span id="high-score">{{ highScore }}</span>pts
        <span id="high-score-diff" class="no-score">{{ diffScore }}</span>
      </div>
    </div>
</template>

<script>
import {mapState} from "vuex";
import {CookieHandler} from "../../common/cookie";

export default {
  name: "scoreBoxSelf",
  data () {
    return {
      pseudoCache: new CookieHandler("amstramdam-pseudo"),
    }
  },
  created() {
    const storedPseudo = this.pseudoCache.read();
    if (storedPseudo){
      this.playerName = storedPseudo;
    }
  },
  computed: {
    playerName: {
      get: function() {
        return this.getPlayerName(this.$store.state.playerId);
      },

      set: function(value) {
        const newPseudo = value.trim();
        this.$socketEmit("name-change", {name: newPseudo});
        if (newPseudo){
          this.pseudoCache.write(newPseudo);
        } else {
          this.pseudoCache.remove();
        }
      }
    },
    nameExists: function(){
      return (typeof this.playerName !== "undefined") && (this.playerName.length > 0)
    },
    diffScore() {
      const game = this.$store.state.game;
        if (!this.highScore || (typeof this.score === "undefined") || !game.launched){
          return ""
        }
        const currHigh = (this.highScore / game.nRuns) * game.currentRun;
        return Math.round(this.score - currHigh);
    },

    ...mapState({
      score: state => state.score.total,
      highScore: state => state.score.high,
    })
  },

  methods: {
    updateName: function(event){
      if (event.type === "keydown"){
        event.preventDefault();
        event.target.blur();
      } else {
        this.playerName = event.target.innerText;
      }
    }
  }
}
</script>

<style scoped>

</style>