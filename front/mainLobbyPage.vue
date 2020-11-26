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
            <game-creator :datasets="datasets"></game-creator>
        </div>
        <div class="vsep padded"></div>
        <div class="existing-game game-panel">
          <game-joiner></game-joiner>
        </div>
      </div>

      <div class="map-container">
        <div id="leaflet"></div>
      </div>
    </popup>
  </div>
</template>

<script>
import footer from "./lobby/footer.vue";
import popup from "./components/popup.vue";
import gameCreator from "./lobby/gameCreator.vue";
import GameJoiner from "./lobby/gameJoiner/gameJoiner.vue";

export default {
  components: {
    GameJoiner,
    "footer-box": footer,
    "popup": popup,
    "game-creator": gameCreator,
  },

  data() {
    return {
      datasets: []
    }
  }
}
</script>

<style scoped>

</style>