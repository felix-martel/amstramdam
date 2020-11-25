<template>
  <div @wheel="scroll" :style="transformation">
    <slot>

    </slot>
  </div>
</template>

<script>
/**
 * DO NOT USE YET !
 * Maybe this should move to a directive:
 * <div v-scrollable></div>
 */
export default {
  name: "scrollable",
  data() {
    return {
      offset: 0,
      height: 0,
      parentHeight: 0,
      observer: undefined,
      parentObserver: undefined,
    }
  },

  computed: {
    maxOffset () {
      return this.height - this.parentHeight;
    },

    transformation () {
      return {
        transform: `translateY(${this.offset}px)`
      }
    }
  },

  mounted() {
    console.log(this.$el);
    const parent = this.$el.parentElement;
    const self = this.$el.firstElementChild;
    this.observer = new ResizeObserver(entries => {
      for (let entry of entries){
        this.height = entry.contentRect.size;
      }
    });
    this.observer.observe(self);
    this.parentObserver = new ResizeObserver(entries => {
      for (let entry of entries){
        this.parentHeight = entry.contentRect.size;
      }
    });
    this.parentObserver.observe(parent);
  },

  methods: {
    scroll(event) {
      const dy = - event.deltaY;
      const newOffset = offset + dy;
      if (0 <= newOffset && newOffset <= this.maxOffset){
        this.offset = newOffset;
      }
    }
  }
}
</script>

<style scoped>

</style>