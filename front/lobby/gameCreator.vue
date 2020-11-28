<template>
  <div class="game-creator">
    <form id="game-creator" :action="action.url" :method="action.method">
      <div class="fieldset">
        <label for="map-selector">Carte</label>
        <map-selector :datasets="datasets" v-model="currentMap"></map-selector>
      </div>

      <div class="fieldset">
        <label for="public-checkbox"
          data-tooltip="La partie apparaîtra dans la liste des parties publiques"
        >Partie publique</label>
        <input id="public-checkbox" v-model="isPublic" name="public" type="checkbox">
      </div>
      <div class="fieldset">
        <label for="diff-level">Niveau de difficulté</label>
        <div class="slidecontainer">
          <input
              type="range" min="1" max="100" v-model="difficulty" @change="difficultyChange"
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
          <div class="fieldset">
            <label for="precision_mode">Mode Précision
              <help-tooltip :content="tooltips.precision_mode" position="top right"></help-tooltip>
            </label>
            <input type="checkbox" name="precision_mode" id="precision_mode" v-model="precisionMode">
          </div>
<!--          <div class="fieldset">-->
<!--            <label for="zoom-checkbox">Zoom autorisé</label>-->
<!--            <input id="zoom-checkbox" v-model="allowZoom" name="zoom" type="checkbox">-->
<!--          </div>-->
        </collapsible-div>
      <div class="buttons">
        <div class="left-buttons">
          <button @click="submit" id="new-game-button" type="submit">
            C'est parti
          </button>
            <slot></slot>
        </div>
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
import HelpTooltip from "../components/helpTooltip.vue";

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
    HelpTooltip,
    CollapsibleDiv,
    MapSelector,
    "v-select": vSelect,
  },

  emits: ["map-change", "difficulty-change", "launch"],

  props: {
    datasets: Array,
    //difficulty: Number,
    //map: String,
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
      map: undefined,
      difficulty: 100,
      duration: 10,
      waitDuration: 7,
      allowZoom: true,
      isPublic: true,
      showOptions: false,
      precisionMode: false,
    tooltips: {
      "precision_mode": "En mode Précision, le temps n'est pas pris en compte dans le calcul du score"
    }
    }
  },

  computed: {
    currentMap: {
      get() {
        return this.map;
      },
      set(value){
        this.$emit("map-change", value);
        this.map = value;
      }
    },

    gameParams() {
      return {
        map: this.currentMap,
        difficulty: this.difficulty,
        runs: this.nRuns,
        duration: this.duration,
        wait_time: this.waitDuration,
        zoom: this.allowZoom,
        public: this.isPublic,
        precision_mode: this.precisionMode
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