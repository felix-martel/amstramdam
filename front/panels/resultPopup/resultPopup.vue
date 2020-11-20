<template>
  <popup :visible="visible">
    <i class="close fas fa-times" @click="close"></i>
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
      <h2 class="blue">
        {{ title }}
      </h2>
      <h4 class="high-score-notif" id="new-highscore-notif" v-if="newHighScore">
        C'est votre meilleur score !
      </h4>
      <result-table :leaderboard="leaderboard"></result-table>
      <button id="relaunch-from-popup">Nouvelle partie</button>
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
import {mapState} from "vuex";
import constants from "../../common/constants";
import {goToHash} from "../../common/utils";

export default {
  components: {
    "popup": Popup,
    "result-table": resultTable,
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

    newHighScore: function() {
      return (!this.highScore && this.status === constants.status.FINISHED)
          || (this.latestScore && this.latestScore > this.highScore);
    },

    ...mapState({
      visible: state => state.ui.resultPopup,
      results: state => state.game.results,
      highScore: state => state.score.high,
      leaderboard: state => state.leaderboard,
      status: state => state.game.status,
    })
  },
  methods: {
    close: function(){
      //this.$store.commit("hideResultPopup");
      goToHash(" ");
    }
  }
}
</script>

<style scoped>
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
</style>