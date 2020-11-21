<template>
  <span></span>
</template>

<script>
import {CountUp} from "countup.js";

export default {
  props: {
    value: Number,
    float: {
      default: false,
      type: Boolean,
    },
  },
  data () {
    return {
      counter: undefined,
    }
  },
  mounted() {
    this.counter = new CountUp(this.$el, this.value, {
      separator: "",
      decimal: ",",
      decimalPlaces: this.float ? 2 : 0,
    });
    this.counter.start();
    // this.counter.update(this.value);
  },
  watch: {
    value: function(newValue, oldValue) {
      this.counter.update(newValue);
    }
  }
}
</script>

<style scoped>

</style>