<template>
  <footer-collapsible-section :collapsed="collapsed">
    <template v-slot:control>
      <span @click="toggle" class="control">
        Options
      </span>
    </template>
    <template v-slot:content>
      <span class="option-bar">
        <input
            v-model="autozoomHandler.state"
            type="checkbox"
            name="autozoom"
            id="autozoom-check">
        <label for="autozoom-check">Autozoom</label>
    </span>
    </template>
  </footer-collapsible-section>
</template>

<script>
import FooterCollapsibleSection from "./footerCollapsibleSection.vue";
import {BooleanSettingHandler} from "../../common/cookie.js";

export default {
name: "footerOptions",
  components: {FooterCollapsibleSection},
  data() {
    return {
      collapsed: true,
      autozoomHandler: new BooleanSettingHandler("autozoom", this.$store),

    }
  },

  methods: {
    toggle() {
      this.collapsed = !this.collapsed;
    },
      toggleAutozoom() {
        let value = this.autozoomHandler.read();
        this.autozoomHandler.write(!value);
      }
  }
}
</script>

<style scoped>
.control {
  cursor: pointer;
}
.option-bar {
  white-space: nowrap;
}
</style>