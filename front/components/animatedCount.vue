<template>
  <span ref="animable"></span>
  <span>{{ displayedUnit }}</span>
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
    unit: {
      type: String,
      default: ""
    }
  },
  data () {
    return {
      counter: undefined,
    }
  },
  mounted() {
    this.counter = new CountUp(this.$refs.animable, this.value, {
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
  },
  computed: {
    displayedUnit(){
      return (this.unit.length > 0) ? " " + this.unit : "";
    }
  }
}
</script>

<style scoped>

</style>