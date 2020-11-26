<template>
<span class="run-info" :class="{'light': light}">
        <span id="run-current">{{ currentRun }}</span>
      /
      <span id="run-total">{{ totalRuns }}</span>
    </span>
</template>
<script>
import {mapState} from "vuex";
export default {
  name: 'runIndicator',
  props: {
    light: {
      type: Boolean,
      default: true,
    }
  },
  computed: {
    ...mapState({
      currentRun: state => state.game.currentRun,
      totalRuns: state => state.game.nRuns,
    })
  },
};

</script>
<style scoped>

.run-info {
  margin-right: 10px;
}

.run-info.light {
  font-size: 0.9em;
  color: gray;
}

</style>