<template>
  <span></span>
</template>

<script>
import {CountUp} from "countup.js";

export default {
  props: {
    value: Number,
  },
  data () {
    return {
      counter: undefined,
    }
  },
  mounted() {
    this.counter = new CountUp(this.$el, this.value, {separator: ""});
    this.counter.start();
  },
  watch: {
    value: function(oldValue, newValue) {
      this.counter.update(newValue);
    }
  }
}
</script>

<style scoped>

</style>