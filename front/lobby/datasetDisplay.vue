<template>
  <div id="dataset-display"></div>
</template>

<script>
import mapBaseMixin from "../map/mapBaseMixin.vue";
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import {LAYERS, CREDITS, defaultView, getIcon} from "../common/map";

export default {
  name: "datasetDisplay",
  mixins: [mapBaseMixin],
  props: {
    points: {
      type: Array,
      default: [],
    },
    difficulty: Number,
  },
  data() {
    return {
      datapoints: undefined,
    }
  },
  watch: {
    points(points) {
      if (!this.datapoints) {
        this.datapoints = L.featureGroup().addTo(this.canvas);
      }
        this.datapoints.clearLayers();
        if (!points) { return }
        points.forEach(point => {
          const options = (point.rank > this.maxRank) ? {extraClasses: ["hidden"]} : {};
          const [lat, lon] = point.coords;
          const marker = this.createMarker({lat, lon},
              "",
              constants.colors.TRUE,
              options,
          )
          marker.rank = point.data.rank;
          this.datapoints.addLayer(marker);
        });
        const bounds = this.datapoints.getBounds();
        this.canvas.flyToBounds(this.datapoints.getBounds());
    },

    difficulty(diff) {
      if (this.datapoints) {
        this.datapoints.eachLayer(point => {
          if (point.rank > this.maxRank) {
            point._icon.classList.add("hidden");
          } else {
            point._icon.classList.remove("hidden");
          }
        })
      }
    }
  },
  computed: {
    maxRank () {
      return Math.max(10, this.difficulty * this.points.length);
    }
  },

  mounted() {
    this.initialize("dataset-display");
    this.datapoints = L.featureGroup().addTo(this.canvas);
  }
}
</script>

<style>
.my-custom-pin {
  transition: opacity 0.2s ease;
}
.my-custom-pin.hidden {
  opacity: 0;
}
</style>

<style scoped>
#dataset-display {
  height: 100%;
  width: 100%;
  background-color: black;
}
</style>