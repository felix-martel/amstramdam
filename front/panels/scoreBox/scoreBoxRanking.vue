<template>
  <ul id="player-list">
    <li v-for="el in leaderboard">
      <span class="pname">{{ getPlayerName(el.player) }}</span>
      <span class="pscore">{{el.score}} pts</span>
    </li>
  </ul>
</template>

<script>
export default {
  name: "scoreBoxRanking",
  computed: {
    leaderboard () {
      return this.$store.state.leaderboard;
    }
  }
}
</script>

<style scoped>

</style>