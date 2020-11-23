<template>
  <ul id="player-list">
    <transition-group name="leaderboard-change" tag="ul">
      <li v-for="el in leaderboard" :key="el.player">
        <span class="pname">{{ getPlayerName(el.player) }}</span>
        <span class="pscore">{{ el.score }} pts</span>
      </li>
    </transition-group>
  </ul>
</template>

<script>
import AnimatedCount from "../../components/animatedCount.vue";
export default {
  name: "scoreBoxRanking",
  components: {AnimatedCount},
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
    list-style: none;
    padding: 0;
  }

  li {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
  }

  .pscore {
    color: gray;
    text-align: right;
    font-style: italic;
    white-space: nowrap;
  }

  .pname {
    text-align: left;
    margin-right: 10px;
  }

  .leaderboard-change-move {
    transition: transform 1s;
  }
</style>