<template>
  <div class="game-creator">
    <h2>Nouvelle partie</h2>
    <form id="game-creator" action="/new" method="post">
      {# [[datasets]] #}
      <div class="fieldset">
        <label for="map-selector">Carte</label>
        <select name="map" id="map-selector">
          {% for dataGroup in datasets %}
          {% if loop.index0 == 0 %}
          {% for dataset in dataGroup.maps %}
          <option value="[[dataset.map_id]]">[[ dataset.name]]</option>
          {% endfor %}
          {% else %}
          <optgroup label="[[ dataGroup.group]]">
            {% for dataset in dataGroup.maps %}
            <option value="[[dataset.map_id]]">[[ dataset.name]]</option>
            {% endfor %}
          </optgroup>
          {% endif %}
          {% endfor %}
        </select>
      </div>
      <div class="fieldset">
        <label for="n-runs-input">Manches</label>
        <input type="number" name="runs" id="n-runs-input" value="10">
      </div>
      <div class="fieldset">
        <label for="wait-input">Durée entre les manches</label>
        <input type="number" name="wait_time" id="wait-input" value="7">
      </div>
      <div class="fieldset">
        <label for="zoom-checkbox">Zoom autorisé</label>
        <input id="zoom-checkbox" checked name="zoom" type="checkbox">
      </div>
      <div class="fieldset">
        <label for="public-checkbox">Partie publique</label>
        <input id="public-checkbox" checked name="public" type="checkbox">
      </div>
      <div class="fieldset">
        <label for="diff-level">Niveau de difficulté</label>
        <div class="slidecontainer">
          <input type="range" min="1" max="100" value="100" class="slider" id="diff-level" name="difficulty">
        </div>
      </div>
      <button type="submit" id="new-game-button">
        C'est parti
      </button>
    </form>
  </div>
</template>

<script>
export default {
  props: {
    datasets: Array,
    params: {
      map: "world",
      nRuns: 10,
      duration: 10,
      wait_time: 7,
      zoom: true,
      public: true,
      difficulty: 100,
    }
  }
}
</script>

<style scoped>

</style>