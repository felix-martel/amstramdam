<template>
  <div class="game-info box" id="display-hint">
    <runIndicator/>
    <span id="target">
<!--      {{ customHint.station }}-->
<!--      <span class="line-icon" :class="`line-${customHint.line}`"><span>{{ customHint.line }}</span></span>-->
        {{ hint.main }}
        <paris-subway-line v-if="currentMap === 'paris_subway'" :line="hint.extra.line"></paris-subway-line>
    </span>
    <radial-countdown :duration="runDuration"></radial-countdown>
  </div>
</template>

<script>
import {mapState} from "vuex";
import radialCountdown from "../../components/radialCountdown.vue";
import RunIndicator from "./RunIndicator.vue";
import ParisSubwayLine from "./customHintDisplay/parisSubwayLine.vue";

export default {
  components: {
    ParisSubwayLine,
    RunIndicator,
    'radial-countdown': radialCountdown,
  },


  computed: {
    customHint () {
      let value = this.currentPlace;
      let station = value.split(" (")[0];
      let lines = value.split(" (")[1].slice(0, -1).split(", ");
      const line = lines[Math.floor(Math.random() * lines.length)];
      return {hint: station, extra: {line}};
    },

    hint () {
      const specialMethods = {
        "paris_subway": "parisSubwayHint",
      }
      const method = specialMethods[this.currentMap] || "regularHint";
      return this[method](this.currentPlace, this.currentHint);
    },
    ...mapState({
      currentRun: state => state.game.currentRun,
      totalRuns: state => state.game.nRuns,
      status: state => state.game.status,
      currentPlace: state => state.game.currentPlace,
      currentHint: state => state.game.currentHint,
      runDuration: state => state.ui.state.duration,
      currentMap: state => state.params.map,
    })
  },

  methods: {
    regularHint(place, hint) {
      let value = place;
      if (hint) value += ` (${hint})`;
      return {main: value, extra: {}};
    },

    parisSubwayHint (place, hint) {
      if (!hint) {
        const splitten = place.split(" (");
        place = splitten[0];
        hint = splitten[1].slice(0, -1);
      }
      const lines = hint.split(", ");
      const line = lines[Math.floor(Math.random() * lines.length)];
      return {main: place, extra: {
        line: line
      }};
    }
  }
}
</script>

<style scoped>
.game-info {
  display: flex;
  flex-direction: row;
  align-items: center;
}

#target {
  color: blue;
  font-size: 2em;
  font-weight: bold;
}

.line-icon {
  display: inline-block;
  /*background-color: yellow;*/
  color: black;
  height: 30px;
  width: 30px;
  position: relative;
  border-radius: 50%;
  font-family: sans-serif;
  font-weight: bold;
  font-size: 22px;
  transform: translate(7px, 3px);
}
.line-icon span {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/*.line-icon.line-1, .line-icon.line-3b, .line-icon.line-5, .line-icon.line-6, .line-icon.line-8, .line-icon.line-9, .line-icon.line-10,*/
/*.line-icon.line-13, .line-icon.line-7b, .line-icon.line-7 {*/
/*  color: black;*/
/*}*/

.line-icon.line-2, .line-icon.line-3, .line-icon.line-4, .line-icon.line-11, .line-icon.line-12, .line-icon.line-14 {
  color: white;
}

.line-icon.line-1 {
  background-color: #FFCD00;
}

.line-icon.line-2 {
  background-color: #003CA6;
}

.ligne-icon.line-3 {
  background-color: #837902;
}

.ligne-icon.line-3b {
  background-color: #6EC4E8;
}

.ligne-icon.line-4 {
  background-color: #CF009E;
}

.ligne-icon.line-5 {
  background-color: #FF7E2E;
}

.ligne-icon.line-6 {
  background-color: #6ECA97;
}

.ligne-icon.line-7 {
  background-color: #FA9ABA;
}

.ligne-icon.line-7b {
  background-color: #6ECA97;
}

.ligne-icon.line-8 {
  background-color: #E19BDF;
}

.ligne-icon.line-9 {
  background-color: #B6BD00;
}

.ligne-icon.line-10 {
  background-color: #C9910D;
}
.ligne-icon.line-11 {
  background-color: #704B1C;
}
.ligne-icon.line-12 {
  background-color: #007852;
}
.ligne-icon.line-13 {
  background-color: #6EC4E8;
}
.ligne-icon.line-14 {
  background-color: #62259D;
}


</style>