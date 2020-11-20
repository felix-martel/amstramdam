<template>
  <div>
    <hint-box v-if="hinting"></hint-box>
    <transition-box :duration="duration" v-else-if="transitioning"></transition-box>
  </div>
</template>

<script>
import hintBox from "./hintBox.vue";
import transitionBox from "./transitionBox.vue";
import {mapState} from "vuex";


export default {
  components: {
    "hint-box": hintBox,
    "transitionBox": transitionBox
  },

  computed: {
    ...mapState({
      transitioning: state => state.ui.state.transition,
      hinting: state => state.ui.state.hint,
      duration: state => state.ui.state.duration,
    })
  }
}
</script>

<style scoped>

</style>