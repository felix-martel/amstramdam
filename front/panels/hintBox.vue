<template>
  <div class="game-info box" id="display-hint">
                <span class="run-info">
                    <span id="run-current">{{ currentRun }}</span>
                  /
                  <span id="run-total">{{ totalRuns }}</span>
                </span>
    <span id="target">
      {{ hint }}
    </span>
    <div class="progress-container">
      <div class="progress-inner">
        <div class="wrapper" id="countdown-animation-wrapper" data-anim="base wrapper">
          <div class="circle" id="countdown-animation-left" data-anim="base left"></div>
          <div class="circle" id="countdown-animation-right" data-anim="base right"></div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from "vuex";

export default {
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
    })
  },
}
</script>

<style scoped>

</style>