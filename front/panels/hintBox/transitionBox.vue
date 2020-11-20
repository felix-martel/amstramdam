<template>
  <div class="box" id="display-timer">
    <span class="timer-text">
      <span id="timer-legend">{{ message }}</span>
      <span id="run-timer">{{ countdown }}</span>...
    </span>
  </div>
</template>

<script>
import {mapState} from "vuex";

export default {
  props: {
    duration: Number
  },

  data () {
    return {
      countdown: undefined,
    }
  },

  mounted() {
    this.countdown = this.duration;
    const interval = window.setInterval(() => {
      this.countdown -= 1;
      if (this.countdown <= 0) {
        window.clearInterval(interval);
      }
    }, 1000);
  },

  computed: {
    ...mapState({
      message: state => state.ui.state.message,
    })
  }
}
</script>

<style scoped>

</style>