<template>
<div>

    <div>
      <i>Entrez le nom d'une partie existante :</i>
    </div>
    <input v-model="targetGame"
           @keydown.enter="goToGame"
           type="text" id="game-name" size="15">
    <button id="join-game-button" @click="goToGame">
      Rejoindre
    </button>

    <h4>Parties publiques
      <i class="fas fa-sync-alt refresh-button"
                             @click="retrievePublicGames"></i>
    </h4>
    <game-list :games="games"></game-list>
</div>
</template>

<script>
import GameList from "./gameList.vue";
import {GET} from "../../common/utils";
export default {
  name: "gameJoiner",
  data() {
    return {
      games: [],
      retries: 0,
      interval: undefined,
      targetGame: "",
      duration: 2, // in seconds
    }
  },
  components: {GameList},
  created() {
    this.retrievePublicGames();
    this.waitThenUpdate();
  },

  methods: {
    retrievePublicGames () {
      GET("/games").then(results => {
        this.games = results;
      });
    },

    goToGame(e){
      e.preventDefault();
      const gameName = this.targetGame.charAt(0).toUpperCase() + this.targetGame.slice(1).toLowerCase();
      window.location.href = `/game/${gameName}`;
    },

    waitThenUpdate() {
      window.setTimeout(() => {
        this.retrievePublicGames();
        this.retries += 1;
        if (this.retries > 5) {
          this.duration = 30;
        }
        this.waitThenUpdate();
      }, this.duration*1000);
    },
  }
}
</script>

<style scoped>
#join-game-button {
  margin-left: 10px;
}

.refresh-button {
  margin-left: 10px;
  color: lightgray;
  transition: transform 0.8s ease, color 0.2s ease;
}

.refresh-button:hover {
  color: blue;
}

.refresh-button:active {
  transform: rotate(-360deg);
  transition: none;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

</style>