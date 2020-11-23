<template>
  <div class="box" id="results">
    <div class="individual-results">
      <div id="answer-name" class="title"></div>
      <div class="distance">
<!--        <span id="main-disp-dist">{{ lastRun.distance }}</span> km-->
        <count :value="lastRun.distance"></count> km
      </div>
      <div class="deets">
        <div class="score-dist">
          <count :value="lastRun.distance"></count> km =
          <count :value="lastRun.sdistance"></count> pts
        </div>
        <div class="score-time">
          <count :value="lastRun.delay" float="true"></count> s =
          <count :value="lastRun.sdelay"></count> pts
        </div>
      </div>
    </div>

    <div class="score">
      <count :value="lastRun.score"></count> pts
    </div>

    <div class="collective-results">
      <ul id="current-results">
        <li v-for="guess in guesses">
          <span class="pname">{{ getPlayerName(guess.name) }}</span>
          <span class="pscore">{{ guess.distance }}km</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import {mapState} from "vuex";
import animatedCount from "../../components/animatedCount.vue";

export default {
  components: {
    "count": animatedCount,
  },
  created() {
  },
  computed: {
    ...mapState({
      totalScore: state => state.score.total,
      lastRun: state => state.lastRun,
      guesses: state => state.guesses,
    })
  }
}
</script>
<style scoped>
.title {
  font-size: 1.1em;
}

.distance {
  font-size: 2em;
  font-weight: bold;
}

.deets {
  margin-top: 10px;
}

.score {
  margin-top: 10px;
  font-size: 2em;
  font-weight: bold;
  padding-bottom: 10px;
  border-bottom: 1px solid lightgray;
}

.collective-results ul {
  list-style: none;
  padding: 0;
}

.collective-results .pname {
  margin-right: 10px;
}

.collective-results .pscore {
  font-style: italic;
}
</style>