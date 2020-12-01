<template>
<div class="blink-wrapper" :class="{off: !blinking}" id="blink-wrapper">
      <div class="blink-item" id="left"></div>
      <div class="blink-item" id="right"></div>
      <div class="blink-item" id="top"></div>
      <div class="blink-item" id="bottom"></div>
</div>
</template>

<script>
export default {
  name: "blinkComponent",

  data() {
    return {
      duration: 100, // in milliseconds
      timestep: 500, // in milliseconds
      blinking: false,
    }
  },

  mounted() {
    window.setInterval(() => {
      this.blink();
    }, this.timestep);
  },

  methods: {
    blink() {
      this.blinking = true;
      window.setTimeout(() => {
        this.blinking = false;
      }, this.duration);
    }
  }
}
</script>

<style scoped>
.blink-wrapper {
  z-index: 1000;

}

.blink-item {
  position: fixed;
  background-color: blue;
  opacity: 1;
  transition: 0.1s ease-in-out;
  z-index: 10;
}
.off .blink-item {
  opacity: 0;
}

#top {
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
}
#left {
  top: 0;
  left: 0;
  bottom: 0;
  width: 5px;
}
#right {
  top: 0;
  bottom: 0;
  right: 0;
  width: 5px;
}
#bottom {
  bottom: 0;
  left: 0;
  right: 0;
  height: 5px;
}
</style>