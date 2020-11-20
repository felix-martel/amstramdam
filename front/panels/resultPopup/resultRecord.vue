<template>
  <tr>
    <td class="rank">{{ index+1 }}</td>
    <td class="player-name">
      {{ name }}
      <i class="fas fa-crown first-place" v-if="isWinner"></i>
    </td>
    <td class="player-score-deets">
      <i class="fas fa-ruler"></i>{{ distance }}
    </td>
    <td class="player-score-deets">
      <i class="fas fa-clock"></i>{{ delay }}
    </td>
    <td class="player-score">{{ score }}</td>
  </tr>
</template>

<script>
import constants from "../../common/constants";

export default {
  props: {
    index: Number,
    record: Object,
  },
  methods: {
    formatNumber: function(value, unit, prec=0) {
      if (value === "-") { return "-" }
      let rounded = Math.round(value * (10**prec)) / (10**prec);
      rounded = String(rounded).replace(/(?!^)(?=(?:\d{3})+(?:\.|$))/gm, ' ')
          .replace(".", ",");
      return rounded + " " + unit;
    }
  },

  computed: {
    name: function () {
      return this.getPlayerName(this.record.player);
    },

    isWinner: function() {
      return (this.$store.state.game.status === constants.status.FINISHED) && this.index === 0
    },

    distance: function () {
      return this.formatNumber(this.record.dist, "km");
    },

    score: function () {
      return this.formatNumber(this.record.score, "pts");
    },

    delay: function () {
      return this.formatNumber(this.record.delta, "s", 2);
    }
  }
}
</script>

<style scoped>

</style>