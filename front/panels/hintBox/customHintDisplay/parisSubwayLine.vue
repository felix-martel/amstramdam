<template>
  <span class="line-icon" :style="lineStyle" v-if="isValid">
    <span>
      {{ line }}
    </span>
  </span>
</template>

<script>
const lineColors = {
  "1": "#FFCD00",
  "2": "#003CA6",
  "3": "#837902",
  "3b": "#6EC4E8",
  "4": "#CF009E",
  "5": "#FF7E2E",
  "6": "#6ECA97",
  "7": "#FA9ABA",
  "7b": "#6ECA97",
  "8": "#E19BDF",
  "9": "#B6BD00",
  "10": "#C9910D",
  "11": "#704B1C",
  "12": "#007852",
  "13": "#6EC4E8",
  "14": "#62259D",
}

const lightTextLines = ["2", "3", "4", "11", "12", "14"];

export default {
  name: "parisSubwayLine",
  props: {
    line: String
  },
  computed: {
    isLight() {
      return lightTextLines.includes(this.line);
    },

    lineStyle () {
      return {
        backgroundColor: lineColors[this.line],
        color: this.isLight ? "white" : "black"
      }
    },

    isValid() {
      const validity = (this.line in lineColors)
      if (!validity) console.warn("Invalid subway line :", this.line);
      return validity
    }
  }
}
</script>

<style scoped>
.line-icon {
  display: inline-block;
  background-color: dimgray;
  color: black;
  height: 30px;
  width: 30px;
  position: relative;
  border-radius: 50%;
  font-family: sans-serif;
  font-weight: bold;
  font-size: 22px;
  transform: translate(7px, 3px);
  margin-right: 10px;
}
.line-icon span {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>