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

</style>