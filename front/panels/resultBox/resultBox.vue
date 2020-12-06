<template>
  <div class="box" id="results">
    <div class="individual-results">
      <div id="answer-name" class="title"></div>
      <div class="distance">
<!--        <span id="main-disp-dist">{{ lastRun.distance }}</span> km-->
        <count :value="lastRunDistance.distance" :unit="lastRunDistance.unit" :float="lastRunDistance.float"></count>
      </div>
      <div class="deets">
        <div class="score-dist">
          <count :value="lastRunDistance.distance" :unit="lastRunDistance.unit" :float="lastRunDistance.float"></count> =
          <count :value="lastRun.sdistance"></count> pts
        </div>
        <div class="score-time" v-if="!precisionMode">
          <count :value="lastRun.delay" :float="true"></count> s =
          <count :value="lastRun.sdelay"></count> pts
        </div>
      </div>
    </div>

    <div class="score">
      <count :prefix="isMobile ? '+ ' : ''" :value="lastRun.score"></count> pts
    </div>

    <div class="collective-results">
      <ul id="current-results">
        <li v-for="guess in guesses">
          <span class="pname">{{ getPlayerName(guess.name) }}</span>
          <span class="pscore">{{ asDistance(guess.distance) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>
<script>
import {mapState} from "vuex";
import animatedCount from "../../components/animatedCount.vue";
import {formatDistance} from "../../common/format.js";

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
      useMeters: state => state.game.small,
      precisionMode: state => state.params.precision_mode,
    }),

    lastRunDistance() {
      return formatDistance(this.lastRun.distance, this.useMeters);
    }
  },

  methods: {
    asDistance(d) {
      return formatDistance(d, this.useMeters).toString();
    }
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

ul {
    width: 100%;
    margin: 0;
    margin-top: 10px;
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

  li:last-of-type {
    margin-bottom: 0;
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


@media screen and (max-width: 600px) {
  .score {
    border: none;
    margin: 0;
    padding: 0;
  }

  ul {
    margin: 0;
    margin-top: 5px;
    display: inline-block;
    width: auto;
  }

  li {
    display: none;
    background-color: blue;
    color: white;
    padding: 1px 5px;
    margin-bottom: 1px;
  }

  li:nth-last-of-type(1),
  li:nth-last-of-type(2),
  li:nth-last-of-type(3) {
    display: block;
    width: auto;
  }

  .pscore {
    color: white;
  }

  #results {
    background-color: transparent;
    color: blue;
    border: none;
    text-align: right;
    padding-top:0;
  }

  /*.last-score:before {*/
  /*      content: "+";*/
  /*      display: inline-block;*/

  /*}*/
}
</style>