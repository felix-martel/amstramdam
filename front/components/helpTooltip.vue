<template>
  <i class="fas fa-question-circle tooltip-icon">
    <div class="tooltip-content" :style="positioningStyle">
      {{ content }}
    </div>
  </i>
</template>

<script>
export default {
  props: {
    content: String,
    position: {
      type: String,
      default: "bottom right"
    },
    width: {
      type: Number,
      default: 150,
    }
  },
  computed: {
    positioningStyle() {
      const s = {
        width: `${this.width}px`,
      };
      const y = (this.position.split(" ")[0] === "top") ? "bottom" : "top";
      const x = (this.position.split(" ")[1] === "left") ? "right" : "left";
      s[y] = "100%";
      s[x] = "100%";
      s.transformOrigin = y + " " + x;
      return s;
    }
  }
}
</script>

<style scoped>
.tooltip-icon {
  position: relative;
  color: lightgrey;
  margin-left: 5px;
  transform: translateY(-1px);
}

.tooltip-icon:hover {
  color: gray;
}
.tooltip-content {
  position: absolute;
  /*top: 100%;*/
  /*left: 100%;*/
  background-color: rgba(0, 0, 0, 0.8);
  color: white;max-width: 300px;
  padding: 5px 10px;
  font-size: 0.8em;
  font-weight: normal;
  /*width: 200px;*/
  transform: scale(0);
  /*transform-origin: top left;*/
  opacity: 0;
  transition: all 0.1s ease-out;
}

.tooltip-icon:hover .tooltip-content {
  transform: scale(1);
  opacity: 1;
}
</style>