<template>
<div class="collapsible">
  <div>
    <a class="low-key" @click="toggle">{{ collapsed ? show : hide }}</a>
  </div>
  <div ref="container" :style="{height: currentHeight}" class="collapsible-inner">
    <slot></slot>
  </div>
</div>
</template>

<script>
export default {
name: "collapsibleDiv",
  props: {
    show: {
      type: String,
      default: "Voir plus",
    },
    hide: {
      type: String,
      default: "Voir moins",
    },
    initial: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      collapsed: undefined,
      height: 0,
    }
  },

  created() {
    this.collapsed = this.initial;
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
    collapse() {
      this.collapsed = true;
    },

    uncollapse() {
      this.collapsed = false;
    },

    toggle() {
      this.collapsed = !this.collapsed;
    },

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