<template>
  <popup :visible="visible">
    <i class="close fas fa-times" @click="close"></i>
    <div class="popup-left">
      <div class="chat">
        <chat-inner></chat-inner>
      </div>
    </div>
    <div class="popup-main">
      <h2 class="blue">
        {{ title }}
      </h2>
      <h4 class="high-score-notif" id="new-highscore-notif" v-if="newHighScore">
        C'est votre meilleur score !
      </h4>
      <result-table :leaderboard="leaderboard"></result-table>
      <button id="relaunch-from-popup" @click="relaunch">Nouvelle partie</button>
      <div style="margin-top:15px;">
        <a  href="/">
          Retour à l'accueil
        </a>
      </div>
    </div>
  </popup>
</template>

<script>
import Popup from "../../components/popup.vue";
import resultTable from "./resultTable.vue";
import {mapState, mapGetters} from "vuex";
import constants from "../../common/constants";
import {goToHash} from "../../common/utils";
import chatInner from "../../components/chatInner.vue";

export default {
  components: {
    "popup": Popup,
    "result-table": resultTable,
    "chat-inner": chatInner,
  },
  computed: {
    latestScore: function() {
      const res = this.results.find(rec => (rec.player === this.$store.state.playerId));
      if (res) {
        return res.score;
      }
      return undefined;
    },

    title: function (){
      return this.status === constants.status.FINISHED ? "Partie terminée" : "Partie en cours..."
    },

    ...mapState({
      visible: state => state.ui.resultPopup,
      results: state => state.game.results,
      highScore: state => state.score.high,
      leaderboard: state => state.leaderboard,
      status: state => state.game.status,
    }),

    ...mapGetters([
      "newHighScore",
      "finalScore",
    ]),
  },
  methods: {
    close: function(){
      //this.$store.commit("hideResultPopup");
      goToHash(" ");
    },

    relaunch: function() {
      this.$socketEmit("launch");
    }
  },

  watch: {
    newHighScore(value) {
      if (value) {
        console.log("New high score", this.finalScore, "!");
        this.$cookie.highScore.write(this.finalScore);
      }
    }
  }
}
</script>

<style scoped>

/** POPUP LAYOUT **/

.popup-left {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  min-height: 0;
  width: 180px;
  border-right: 1px solid lightgray;
  margin-bottom: 0;
  overflow-x: hidden;
  overflow-y: auto;
}


.popup-main {
  margin-left: 200px;
}

/** ELEMENTS **/

.close {
    position: absolute;
    top: 7px;
    right: 7px;
    color: #a1a1a1;
    cursor:pointer;
  z-index: 1;

}
.close:hover {
  color: blue;
}

.high-score-notif {
  margin-top: 0;
  font-style: italic;
  color: gray;
}

#relaunch-from-popup {
  margin: 0 auto;
  margin-top: 15px;
}
</style>