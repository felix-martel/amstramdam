<template>
  <popup :visible="visible">
    <i class="close fas fa-times" @click="close"></i>
    <div class="popup-left" v-if="!isMobile">
      <div class="chat">
        <chat-inner></chat-inner>
      </div>
    </div>
    <div class="popup-main">
      <template v-if="gameCreatorMode">
        <h2 class="blue">
          Changer de partie
        </h2>
        <div class="creator-wrapper">
          <game-creator
            :datasets="datasets"
            :action="{'method': 'emit'}"
            @launch="createNewGame"
          >
            <button class="cancel-button" @click="closeCreator">Annuler</button>
          </game-creator>
        </div>
      </template>
      <template v-else>
        <h2 class="blue">
          {{ title }}
        </h2>
        <h4 class="high-score-notif" id="new-highscore-notif" v-if="newHighScore">
          C'est votre meilleur score !
        </h4>
        <result-table :leaderboard="leaderboard"></result-table>
        <div class="popup-buttons">
          <button @click="close">Voir la correction</button>
          <button id="relaunch-from-popup" @click="relaunch" class="main-button">Nouvelle partie</button>
          <button @click="openCreator">Changer de carte</button>
        </div>
        <div style="margin-top:15px;">
          <a  href="/" class="low-key">
            Retour à l'accueil
          </a>
        </div>
      </template>
    </div>
  </popup>
</template>

<script>
import Popup from "../../components/popup.vue";
import resultTable from "./resultTable.vue";
import {mapState, mapGetters} from "vuex";
import constants from "../../common/constants";
import {GET, goToHash} from "../../common/utils";
import chatInner from "../../components/chatInner.vue";
import GameCreator from "../../lobby/gameCreator.vue";

export default {
  components: {
    GameCreator,
    "popup": Popup,
    "result-table": resultTable,
    "chat-inner": chatInner,
  },
  data() {
    return {
      datasets: [
        {map_id: undefined, name: "Chargement..."}
      ],
    }
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
      gameCreatorMode: state => state.ui.showGameCreator,
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
  mounted() {
    GET("/datasets").then(datasets => {
      this.datasets = datasets;
    });
  },
  methods: {
    close: function(){
      //this.$store.commit("hideResultPopup");
      goToHash(" ");
    },

    relaunch: function() {
      this.$socketEmit("launch");
    },

    openCreator: function() {
      this.$store.commit("showGameCreator");
    },

    closeCreator: function() {
      this.$store.commit("hideGameCreator");
    },

    createNewGame: function (data) {
      console.log("Requesting game change", data);
      this.$socketEmit("request-game-change", data);
    },
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

  resize: horizontal;
  background-color: white;
  transition: width 0.2s ease;
}

.popup-left:hover, .popup-left:focus {
  width: 220px;
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

.popup-buttons {
  margin: 0 auto;
  margin-top: 15px;
}

.popup-buttons button{
  margin-right: 10px;
}

.creator-wrapper button {
  margin-left: 10px;
}

@media screen and (max-width: 600px) {
  #popup .popup-main {
      display: flex;
      flex-flow: column nowrap;
      justify-content: center;
      margin: 0;
  }

  #popup.popup-top {
      justify-content: start;
  }
}
</style>