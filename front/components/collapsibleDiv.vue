<template>
<div class="collapsible">
  <div ref="container" :style="{height: currentHeight}" class="collapsible-inner">
    <slot></slot>
  </div>
</div>
</template>

<script>
export default {
name: "collapsibleDiv",
  props: {
    collapsed: Boolean
  },

  data() {
    return {
      height: 0,
    }
  },

  created() {
  },

  mounted() {
    this.height = this.computeHeight();
  },

  computed: {
    currentHeight() {
      return (this.collapsed ? 0 : this.height);
    },
  },

  methods: {

    computeHeight() {
      const container = this.$refs.container;
      if (!container) {
        return "auto";
      }
      container.style.height = "auto";
      const h = getComputedStyle(container).height;
      container.style.height = 0;
      return h;
    }
  }
}
</script>

<style scoped>
.collapsible-inner {
  overflow: hidden;
  transition: 0.5s;
}
</style>