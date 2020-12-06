<template>
  <div class="game-info box" id="display-hint">
    <div class="countdown-container">
      <linear-countdown :duration="runDuration" class="countdown"
                        progress="rgba(0, 0, 0, 0.1)"
                        :background="'white'"></linear-countdown>
    </div>
    <div class="game-info">
      <runIndicator/>
      <span id="target">
        {{ hint.main }}
        <paris-subway-line v-if="currentMap === 'paris_subway'" :line="hint.extra.line"></paris-subway-line>
    </span>
    </div>

  </div>
</template>

<script>
import {mapState} from "vuex";
import RunIndicator from "./RunIndicator.vue";
import ParisSubwayLine from "./customHintDisplay/parisSubwayLine.vue";
import LinearCountdown from "../../components/linearCountdown.vue";

export default {
  components: {
    LinearCountdown,
    ParisSubwayLine,
    RunIndicator,
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
.countdown-container {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  bottom:0;
}

.game-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: relative;
}

#target {
  color: blue;
  font-size: 2em;
  font-weight: bold;
}
</style>