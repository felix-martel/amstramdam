<template>
  <div class="box" id="display-timer">
    <span class="timer-text">
      <span id="timer-legend">{{ message }}</span>
      <span id="run-timer">{{ count }}</span>...
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
      count: undefined,
    }
  },

  methods: {
    start(duration){
      this.count = duration;
      this.countdown = window.setInterval(() => {
      this.count -= 1;
      if (this.count <= 0) {
        window.clearInterval(this.countdown);
      }
    }, 1000);
    }
  },

  mounted() {
    this.start(this.duration);
  },

  watch:{
    duration(newValue){
      window.clearInterval(this.countdown);
      this.start(newValue);
    }
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