<template>
  <div class="countdown-outer" :style="outerStyle">
    <div class="countdown-inner" :class="{'running': !ended}" :style="innerStyle">

    </div>
  </div>
</template>

<script>
export default {
  props: {
    duration: Number,
    background: {
      type: String,
      default: "blue"
    },
    progress: {
      type: String,
      default: "darkblue"
    }
  },
  data () {
    return {
      ended: true,
      closeToEnd: false,
      interval: undefined,
      warningInterval: undefined,
    }
  },

  computed: {
    outerStyle() {
      return {backgroundColor: this.background}
    },

    innerStyle () {
      return {backgroundColor: this.progress,
        transition: `all ${this.duration}s linear`
      // transitionProperty: "all",
      // transitionTimingFunction: "linear"
      }
    }
  },

  mounted() {
    window.setTimeout(() => {
      this.ended = false;
    }, 50);
  },

  watch: {
    duration(newDuration){
      this.end();
      this.start(newDuration);
    }
  },

  methods: {
    start(){
      this.ended = false;
    },

    end(){
      this.ended = true;
    }
  },
}
</script>

<style scoped>
.countdown-outer {
  box-sizing: border-box;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.countdown-inner {
  height: 100%;
  width: 100%;
  transform: translateX(-100%);
  transition: transform 1s linear;
}

.countdown-inner.running {
  transform: translate(0);
}

@keyframes progress {
  from {
      transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

</style>