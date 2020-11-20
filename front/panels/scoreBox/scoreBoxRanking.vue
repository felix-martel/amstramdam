<template>
  <ul id="player-list">
    <li v-for="el in leaderboard">
      <span class="pname">{{ getPlayerName(el.player) }}</span>
      <span class="pscore">{{el.score}} pts</span>
    </li>
  </ul>
<!--  <table>-->
<!--    <tr v-for="el in leaderboard">-->
<!--      <td class="pname">{{ getPlayerName(el.player) }}</td>-->
<!--      <td class="pscore">{{ el.score }} pts</td>-->
<!--    </tr>-->
<!--  </table>-->
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
ul {
  width: 100%;
  margin: 10px 0;
}

li {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.pscore {
  color: gray;
}
</style>