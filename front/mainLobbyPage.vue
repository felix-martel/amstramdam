<template>
  <div class="main">
    <footer-box></footer-box>
    <popup :visible="true">
      <div class="main-title">
        <h1 class="blue">
          <span id="title">am·stram·dam</span>
        </h1>
        <div><i>Localiser les villes sur la carte, le plus rapidement possible</i></div>
      </div>
      <div class="game-panel-container">

        <div class="new-game game-panel">
            <h2>Créer une partie</h2>
            <game-creator :datasets="datasets"
                          :action="formAction"
                          @map-change="getPoints"
                          @difficulty-change="setDifficulty"
                          @launch="launchGame"
            >
            </game-creator>
        </div>
        <div class="vsep padded"></div>
        <div class="existing-game game-panel">
          <h2>Rejoindre une partie</h2>
          <game-joiner></game-joiner>
        </div>
      </div>

      <div class="map-container" :class="{'loading': loading}">
        <div class="map-container-inner">
          <dataset-display :difficulty="difficulty" :points="points"></dataset-display>

        </div>
      </div>
    </popup>
  </div>
</template>

<script>
import footer from "./lobby/footer.vue";
import popup from "./components/popup.vue";
import gameCreator from "./lobby/gameCreator.vue";
import GameJoiner from "./lobby/gameJoiner/gameJoiner.vue";
import {GET} from "./common/utils.js";
import DatasetDisplay from "./lobby/datasetDisplay.vue";

export default {
  components: {
    DatasetDisplay,
    GameJoiner,
    "footer-box": footer,
    "popup": popup,
    "game-creator": gameCreator,
  },

  data() {
    return {
      datasets: datasets,
      map: "",
      points: [],
      loading: true,
      difficulty: 1,
      formAction: {
        method: "post",
        url: "/new",
      }
    }
  },

  methods: {
    getPoints(map) {
      this.loading = true;
        this.map = map;
        GET(`/points/${map}`).then(data => {
          this.points = data.points;
          this.loading = false;
        });
    },

    setDifficulty(diff) {
      this.difficulty = diff;
    },

    launchGame(params){

    }
  },


}
</script>

<style scoped>
.map-container {
  height: 220px;
  width: 100%;
  position: relative;
}

.map-container-inner {
  position: absolute;
  top: 0;
  left: -20px;
  right: -20px;
  bottom: -20px;
  background-color: black;
  /*transition: opacity 1.2s ease-in;*/
}

.loading .map-container-inner {
  /*opacity: 0.2;*/
  /*transition: opacity 1.2s ease-in;*/
}


</style>