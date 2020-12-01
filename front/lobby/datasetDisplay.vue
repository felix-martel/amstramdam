<template>
  <div id="dataset-display" :data-size="nPoints"></div>
</template>

<script>
import mapBaseMixin from "../map/mapBaseMixin.vue";
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import {LAYERS, CREDITS, defaultView, getIcon, CREDITS_SHORT} from "../common/map";

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
      nPoints: 0,
    }
  },
  watch: {
    points(points) {
      this.removeAllLayers();
      this.datapoints = L.featureGroup().addTo(this.canvas);
      // if (!this.datapoints) {
      //   this.datapoints = L.featureGroup().addTo(this.canvas);
      // }
      // this.datapoints.clearLayers();
      if (points.length === 0) { return }
      let n = 0;
      points.forEach(point => {
        //const options = (point.rank > this.maxRank) ? {extraClasses: ["hidden"]} : {};
        const [lat, lon] = point.coords;
        if (point.rank <= this.maxRank) n++;
        const marker = this.createMarker({lat, lon},
            "",
            constants.colors.TRUE,
            {
              small: true,
              extraClasses: (point.rank > this.maxRank) ? ["hidden"] : []
            },
        )
        marker.rank = point.data.rank;
        this.datapoints.addLayer(marker);
      });
      this.nPoints = n;
      this.canvas.flyToBounds(this.datapoints.getBounds());
    },

    difficulty(diff) {
      if (this.datapoints) {
        let n = 0;
        this.datapoints.eachLayer(point => {
          if (point.rank > this.maxRank) {
            point._icon.classList.add("hidden");
          } else {
            point._icon.classList.remove("hidden");
            n ++;
          }
        });
        this.nPoints = n;
      }
    }
  },
  computed: {
    maxRank () {
      return Math.max(10, this.difficulty * this.points.length);
    }
  },

  mounted() {
    this.initialize("dataset-display", {credits: ""});
    // this.datapoints = L.featureGroup().addTo(this.canvas);
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

#dataset-display:after {
  content: attr(data-size);
  display: inline-block;
  position: absolute;
  color: red;
}
</style>