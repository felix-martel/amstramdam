<template>
  <div class="game-creator">
    <h2>Nouvelle partie</h2>
    <form id="game-creator" :action="action.url" :method="action.method">
      <div class="fieldset">
        <label for="map-selector">Carte</label>
        <map-selector :datasets="datasets" v-model="currentMap"></map-selector>
      </div>

      <div class="fieldset">
        <label for="public-checkbox">Partie publique</label>
        <input id="public-checkbox" v-model="isPublic" name="public" type="checkbox">
      </div>
      <div class="fieldset">
        <label for="diff-level">Niveau de difficulté</label>
        <div class="slidecontainer">
          <input
              type="range" min="1" max="100" :value="difficulty*100" @change="difficultyChange"
              class="slider" id="diff-level" name="difficulty">
        </div>

      </div>
      <collapsible-div :collapsed="!showOptions">
          <div class="fieldset">
            <label for="n-runs-input">Manches</label>
            <input type="number" name="runs" id="n-runs-input" v-model="runs">
          </div>
          <div class="fieldset">
            <label for="duration-input">Durée d'une manche</label>
            <input type="number" name="duration" id="duration-input" v-model="duration">
          </div>
          <div class="fieldset">
            <label for="wait-input">Durée entre les manches</label>
            <input type="number" name="wait_time" id="wait-input" v-model="waitDuration">
          </div>
<!--          <div class="fieldset">-->
<!--            <label for="zoom-checkbox">Zoom autorisé</label>-->
<!--            <input id="zoom-checkbox" v-model="allowZoom" name="zoom" type="checkbox">-->
<!--          </div>-->
        </collapsible-div>
      <div class="buttons">
      <button @click="submit" id="new-game-button" type="submit">
        C'est parti
      </button>
        <a class="low-key" @click="showOptions = !showOptions">
          {{ showOptions ? "Moins d'options" : "Plus d'options" }}
        </a>
      </div>
    </form>
  </div>
</template>

<script>
import vSelect from 'vue-select'
import MapSelector from "./mapSelector.vue";
import CollapsibleDiv from "../components/collapsibleDiv.vue";

/**
 * Form can be submitted in two ways:
 * - as a regular HTML form. Through the 'action' prop, you provide the target URL ('action.url') and
 * the method ('action.method'). Example:
 * < game-creator :action="{url: '/new', method: 'post'}">...
 * Clicking the launch button will submit the form to the provided URL with the said method
 * - as a Vue event. If 'action.method' === 'emit', then a 'launch' event will be emitted to the
 * parent component, with a payload corresponding to the form content.
 */
export default {
  components: {
    CollapsibleDiv,
    MapSelector,
    "v-select": vSelect,
  },

  emits: ["map-change", "difficulty-change", "launch"],

  props: {
    datasets: Array,
    difficulty: Number,
    map: String,
    action: {
      type: Object,
      default: {
        method: "emit",
        url: ""
      }
    }
  },

  data () {
    return {
      runs: 10,
      duration: 10,
      waitDuration: 7,
      allowZoom: true,
      isPublic: true,
      showOptions: false,
    }
  },

  computed: {
    currentMap: {
      get() {
        return this.map;
      },
      set(value){
        this.$emit("map-change", value);
      }
    },

    gameParams() {
      return {
        map: this.currentMap,
        difficulty: 100*this.difficulty,
        nRuns: this.nRuns,
        duration: this.duration,
        wait_time: this.waitDuration,
        zoom: this.allowZoom,
        isPublic: this.isPublic,
      }
    }
  },

  methods: {
    updateView(map) {
      this.$emit("map-change", map);
    },

    difficultyChange(e) {
      this.$emit("difficulty-change", parseInt(e.target.value) / 100);
    },

    submit(e) {
      if (this.action.method === "emit") {
        e.preventDefault();
        this.$emit("launch", this.gameParams);
      }
    }
  }
}
</script>

<style scoped>

.buttons {
      display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;
  margin-top: 25px;
}
</style>