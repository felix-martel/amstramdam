<template>
<div class="self">
      <div class="name" id="player-name" :contenteditable="nameExists"
      @keydown.enter="updateName" @focusout="updateName">
        {{ playerName || 'Non connecté'}}
      </div>
      <div class="total-score"><span id="total-score">{{ score }}</span> pts</div>
      <div class="high-score" id="high-score-container" v-if="highScore">
        <i class="fas fa-trophy high-score-icon"></i>
        <span id="high-score">{{ highScore }}</span>pts
        <span id="high-score-diff"
              v-if="diffScore"
              :class="diffScoreClass">{{ diffScore }}</span>
      </div>
    </div>
</template>

<script>
import {mapState} from "vuex";
import {CookieHandler} from "../../common/cookie";
import constants from "../../common/constants";

export default {
  name: "scoreBoxSelf",
  data () {
    return {
      //pseudoCache: new CookieHandler("amstramdam-pseudo"),
    }
  },
  created() {
    // const storedPseudo = this.pseudoCache.read();
    // if (storedPseudo){
    //   this.playerName = storedPseudo;
    // }
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
          this.$cookie.pseudo.write(newPseudo);
        } else {
          this.$cookie.pseudo.remove();
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
        const currHigh = (this.highScore / game.nRuns) * this.currentRun;
        return Math.round(this.score - currHigh);
    },

    diffScoreClass() {
      return this.diffScore > 0 ? "pos-score" : "neg-score";
    },

    trueCurrentRun() {
      return this.$store.state.game.currentRun;
    },

    nRuns(){
      return this.$store.state.game.nRuns;
    },

    currentRun() {
      const run = this.$store.state.game.currentRun;
      return (this.status === constants.status.CORRECTION  || this.status === constants.status.FINISHED) ? run : (run - 1);
    },

    score() {
      return this.$store.getters.selfScore;
    },

    ...mapState({
      highScore: state => state.score.high,
      status: state => state.game.status,
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
.self {
  padding-bottom: 10px;
  border-bottom: 1px solid lightgray;
}

.self .name {

}

.self .total-score {
  font-size: 2em;
  font-weight: bold;
}


.high-score {
  padding-top: 5px;
  color: gray;
}

.high-score-icon  {
  color: gold;
  margin-right: 5px;
}


#high-score-diff.no-score {
  display: none;
}
#high-score-diff.pos-score {
  color: green;
}
#high-score-diff.neg-score {
  color: orangered;
}

@media screen and (max-width: 600px) {
  #player-name {
    color: white;
    background-color: red;
    margin-right: 9px;
    padding: 1px 5px;

  }

  #player-name.name:after {
    color: transparent;
    display: none;
  }

  .box .self {
    display: flex;
    flex-flow: row nowrap;
    justify-content: flex-end;
    align-items: center;
    border: none;
    padding-bottom: 0;
  }

  .high-score {
    display: none;
  }
}
</style>