<template>
  <div class="main">
    <footer></footer>
    <popup>
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
          <h2>Rejoindre</h2>
          <div>
            <i>Entrez le nom d'une partie existante :</i>
          </div>
          <input type="text" id="game-name"  size="15">
          <button id="join-game-button">
            Rejoindre
          </button>

          <h4>Parties publiques</h4>
          <div class="game-list">
            {% for game in games %}
            <div class="game-item">
              <a href="/game/[[game.name]]">[[game.name | trim]]</a>
              <span class="game-infos">[[game.map]]·
                            difficulté [[100*game.difficulty|round|int]]% ·
                            [[game.players]] joueur{% if game.players > 1 %}s{% endif %}
                        </span>
            </div>
            {% endfor %}
          </div>
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

export default {
  components: {
    "footer": footer,
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