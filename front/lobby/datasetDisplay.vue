<template>
  <div id="dataset-display" :data-size="nPoints" :data-selected="difficulty"></div>
</template>

<script>
import mapBaseMixin from "../map/mapBaseMixin.vue";
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";

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
        const extraClasses = [];
        if (point.data.rank <= this.maxRank) {
          n++;
        } else {
          extraClasses.push("hidden");
        }
        if (typeof point.data.group !== "undefined") extraClasses.push(`icon-group-${point.data.group}`);
        const marker = this.createMarker({lat, lon},
            "",
            constants.colors.TRUE,
            {
              small: true,
              extraClasses: extraClasses, // (point.rank > this.maxRank) ? ["hidden"] : []
            },
        )
        marker.rank = point.data.rank;
        this.datapoints.addLayer(marker);
      });
      this.nPoints = n;
      this.canvas.flyToBounds(this.datapoints.getBounds());
    },
  },
  computed: {
    maxRank () {
      return Math.max(10, this.difficulty * this.points.length);
    }
  },

  mounted() {
    this.initialize("dataset-display", {credits: ""});
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
.icon-group-0 {
  opacity: 1;
}

.icon-group-1, .icon-group-2 {
  opacity: 0;
}

div[data-selected="1"] .icon-group-1,
div[data-selected="2"] .icon-group-1{
  opacity: 1;
}

div[data-selected="2"] .icon-group-2 {
  opacity: 1;
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