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