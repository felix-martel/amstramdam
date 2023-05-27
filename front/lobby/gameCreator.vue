<template>
  <div class="game-creator">
    <form id="game-creator" :action="action.url" :method="action.method">
      <div class="fieldset">
        <label for="map-selector">Carte</label>
        <map-selector :datasets="datasets" v-model="currentMap"></map-selector>
      </div>


      <div class="fieldset diffset" v-if="currentMap.levels && (currentMap.levels.length > 1)">
        <label>Difficulté</label>
        <div class="slidecontainer">
<!--          <input-->
<!--              type="range" min="1" max="100" v-model="difficulty" @change="difficultyChange"-->
<!--              class="slider diff-slider" id="diff-level" name="difficulty">-->
<!--          <span class="diff-counter">{{ difficulty }}%</span>-->
          <button v-for="level in currentMap.levels"
                  @click.prevent="difficultyChange(level.index)"
                  :class="{selected: level.index === difficulty}">
            {{ level.name }}
          </button>
          <input type="range" min="0" max="2" v-model="difficulty" name="difficulty" hidden>
        </div>
      </div>
      <div class="fieldset">
        <label for="public-checkbox"
          data-tooltip="La partie apparaîtra dans la liste des parties publiques"
        >Partie publique</label>
        <input id="public-checkbox" v-model="isPublic" name="public" type="checkbox">
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
import MapSelector from "./mapSelector.vue";
import CollapsibleDiv from "../components/collapsibleDiv.vue";
import HelpTooltip from "../components/helpTooltip.vue";
import {unproxify} from "../common/utils.js";

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
      map: {},
      difficulty: 0,
      duration: 10,
      waitDuration: 7,
      allowZoom: true,
      isPublic: true,
      showOptions: false,
      precisionMode: false,
      tooltips: {
      "precision_mode": "En mode Précision, le temps n'est pas pris en compte dans le calcul du score"
    },
      defaultDiffButtons: ["Normal", "Avancé", "Difficile"],
    }
  },

  computed: {
    currentMap: {
      get() {
        return this.map;
      },
      set(value){
        // console.log(unproxify(value));
        this.$emit("map-change", value);
        this.map = value;
        this.difficultyChange(this.map.default_level || 0);
        // console.log(unproxify(this.map));
        // console.log(unproxify(this.diffLevels));
      }
    },

    gameParams() {
      return {
        map: this.currentMap.map_id,
        difficulty: this.difficulty,
        runs: this.runs,
        duration: this.duration,
        wait_time: this.waitDuration,
        zoom: this.allowZoom,
        public: this.isPublic,
        precision_mode: this.precisionMode
      }
    },

    diffLevels() {
      const maxLevel = ((typeof this.map !== "undefined")
          && (typeof this.map.available_levels !== "undefined")) ? this.map.available_levels - 1 : 3;
      return {
        min: 0,
        max: maxLevel, // this.map.available_levels-1 || 3,
        // default: this.map.default_level || 0,
      }
    },

    diffButtons() {
      const buttons = (this.map.customLevels && this.map.customLevels.length >= this.diffLevels.max) ?
          this.map.customLevels : this.defaultDiffButtons
      return buttons.slice(0, this.diffLevels.max + 1);
    }
  },

  methods: {
    updateView(map) {
      this.$emit("map-change", map);
    },

    difficultyChange(value) {
      //e.target.value
      this.difficulty = value;
      this.$emit("difficulty-change", this.difficulty);
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

.slidecontainer {
  white-space: nowrap;
}

.diff-slider {
  vertical-align: middle;
}

.diff-counter {
  display: inline-block;
  min-width: 40px;
  text-align: right;
  margin-left: 10px;
}

.fieldset.diffset {
  display: flex;
flex-flow: row nowrap;
align-items: center;
}
button.selected {
  border-color: gray;
}
</style>