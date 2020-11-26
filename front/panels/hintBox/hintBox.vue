<template>
  <div class="game-info box" id="display-hint">
    <runIndicator/>
    <span id="target">
      {{ hint }}
    </span>
    <radial-countdown :duration="runDuration"></radial-countdown>
  </div>
</template>

<script>
import {mapState} from "vuex";
import radialCountdown from "../../components/radialCountdown.vue";
import RunIndicator from "./RunIndicator.vue";

export default {
  components: {
    RunIndicator,
    'radial-countdown': radialCountdown,
  },
  computed: {
    hint () {
      let value = this.currentPlace;
      if (this.currentHint){
        value += ` (${this.currentHint})`;
      }
      return value;
    },
    ...mapState({
      currentRun: state => state.game.currentRun,
      totalRuns: state => state.game.nRuns,
      status: state => state.game.status,
      currentPlace: state => state.game.currentPlace,
      currentHint: state => state.game.currentHint,
      runDuration: state => state.ui.state.duration,
    })
  },
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
</style>