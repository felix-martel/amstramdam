<template>
  <div class="section">
    <div class="section-controller">
      <slot name="control"></slot>
    </div>
    <div
        ref="container"
        :class="{collapsed: collapsed}"
        :style="{maxWidth: collapsed ? 0 : width}"
        class="section-collapsible">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    collapsed: Boolean
  },
  data() {
    return {
      width: 0
    }
  },

  mounted() {
    this.width = this.getIntrinsicWidth(this.$refs.container);
  },

  methods: {
    getIntrinsicWidth(el) {
      if (!el) return -1;
      el.style.maxWidth = "none";
      const width = getComputedStyle(el).width;
      // el.style.display = "inline-block";
      el.style.maxWidth = 0;
      return width;
    }
  }
}
</script>

<style scoped>
.section {
  display: flex;
  flex-flow: row nowrap;
  justify-content: flex-start;
  align-items: center;
}

.section-collapsible {
  transition: all 0.4s ease;
  overflow-x: hidden;
}

.section-collapsible.collapsed {
  opacity: 0;
}
</style>