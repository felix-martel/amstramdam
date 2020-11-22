<template>
<div class="progress-container">
      <div class="progress-inner">
        <div class="wrapper"
             id="countdown-animation-wrapper"
             :class="{'warning': closeToEnd}"
             :style="{animationDelay: halfDurationString}"
             :data-anim="ended ? '' : 'base wrapper'">
          <div class="circle"
               id="countdown-animation-left"
               :style="{animationDuration: durationString}"
               :data-anim="ended ? '' : 'base left'"></div>
          <div class="circle"
               id="countdown-animation-right"
               :style="{animationDuration: halfDurationString}"
               :data-anim="ended ? '' : 'base right'"></div>
        </div>
      </div>
    </div>
</template>

<script>
export default {
  props: {
    duration: Number
  },
  data () {
    return {
      ended: false,
      closeToEnd: false,
      interval: undefined,
      warningInterval: undefined,
    }
  },

  mounted() {
    this.start(this.duration);
  },

  watch: {
    duration(newDuration){
      this.end();
      this.start(newDuration);
    }
  },
  computed: {
    durationString() {
      return String(this.duration) + "s";
    },

    halfDurationString() {
      return String(this.duration / 2) + "s";
    }
  },

  methods: {
    start(duration){
      this.ended = false;
      this.closeToEnd = false;
      if (typeof this.interval !== "undefined") {clearInterval(this.interval)}
      this.interval = setInterval(() => {
        this.end();
      }, duration*1000)
      this.warningInterval = setInterval(() => {
        this.closeToEnd = true;
      }, (duration - 3) * 1000);
    },

    end(){
      this.ended = true;
      if (typeof this.interval !== "undefined") {
        clearInterval(this.interval)
        this.interval = undefined;
      }
      if (typeof this.warningInterval !== "undefined") {
        clearInterval(this.warningInterval)
        this.warningInterval = undefined;
      }
    }
  },
}
</script>

<style scoped>

.progress-container {
  display: inline-flex;
  position: relative;
  padding: 0 10px;
  height: 20px;
  width: 20px;

}

.progress-inner {
  height: 18px;
  width: 18px;

}

.wrapper {
  width: 18px;
  height: 18px;
  position: absolute;
    margin:-2px;
    transform: translateY(3px);
  clip: rect(0px, 18px, 18px, 9px); /* Hide half of the progress bar */
}
/* Set the sizes of the elements that make up the progress bar */
.circle {
  width: 12px;
  height: 12px;
  border: 3px solid blue;
  border-radius: 9px;
  position: absolute;
  clip: rect(0px, 9px, 18px, 0px);
}

.warning .circle {
  border-color: red;
  transition: border-color 2s;
}
/* Using the data attributes for the animation selectors. */
/* Base settings for all animated elements */
div[data-anim~=base] {
  animation-iteration-count: 1;  /* Only run once */
  animation-fill-mode: forwards; /* Hold the last keyframe */
  animation-timing-function:linear; /* Linear animation */
}

.wrapper[data-anim~=wrapper] {
  animation-duration: 0.01s; /* Complete keyframes asap */
  animation-delay: 3s; /* Wait half of the animation */
  animation-name: close-wrapper; /* Keyframes name */
}

.circle[data-anim~=left] {
  animation-duration: 6s; /* Full animation time */
  animation-name: left-spin;
}

.circle[data-anim~=right] {
  animation-duration: 3s; /* Half animation time */
  animation-name: right-spin;
}
/* Rotate the right side of the progress bar from 0 to 180 degrees */
@keyframes right-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(180deg);
  }
}
/* Rotate the left side of the progress bar from 0 to 360 degrees */
@keyframes left-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
/* Set the wrapper clip to auto, effectively removing the clip */
@keyframes close-wrapper {
  to {
    clip: rect(auto, auto, auto, auto);
  }
}
</style>