<template>
  <div class="box" id="results">
    <div class="individual-results">
      <div id="answer-name" class="title"></div>
      <div class="distance">
        <span id="main-disp-dist">{{ lastRun.distance }}</span> km
      </div>
      <div class="deets">
        <div class="score-dist">
          <i id="disp-dist">{{ lastRun.distance }}</i> km =
          <i id="disp-score-dist">{{ lastRun.sdistance}}</i> pts
        </div>
        <div class="score-time">
          <i id="disp-time">{{ lastRun.delay }}</i>s =
          <i id="disp-score-time">{{ lastRun.sdelay}}</i> pts
        </div>
      </div>
    </div>

    <div class="score">
      <span id="curr-score">{{ lastRun.score }}</span> pts
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

export default {
  computed: {
    ...mapState({
      totalScore: state => state.score.total,
      lastRun: state => state.lastRun,
      guesses: state => state.guesses,
    })
  }
}
</script>