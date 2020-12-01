<template>
<div class="data-builder">
  <div class="controls box">
    <div class="stats">
      <map-selector :datasets="datasets" v-model="baseMap"></map-selector>
      <br>
      {{ nPoints }} points
      <br>
      {{ nSelected }} sélectionnés
    </div>
    <div class="sliders">
    <div class="slidecontainer" v-for="(v, i) in thresholds">
      <span class="group-name">
        G{{ i }}
      </span>
          <input
              type="range" min="-1" :max="nPoints"
              :value="thresholds[i]"
              @input="updateThreshold($event, i)"
              class="slider diff-slider">
<!--          <span class="diff-counter">{{ thresholds[i] }}</span>-->
          <input class="diff-counter" type="number" :value="thresholds[i]"
              @input="updateThreshold($event, i)">
        </div>
    </div>
    <table>
      <tr>
        <td></td>
        <td v-for="index in indices">G{{index}}</td>
      </tr>
      <tr v-for="o in scales">
        <td>
          {{ o.name }}
        </td>
        <td v-for="index in indices">
          <button :disabled="getButton(o.scale, index).disabled"
                  :class="{'selected': (selected[0] === o.scale) && (selected[1] === index)}"
                  @click="select(o.scale, index)">
            {{ getButton(o.scale, index).label }}
          </button>
        </td>
      </tr>
    </table>
    <div>
      <a :href="fileContent" :download="filename">Télécharger</a>
    </div>
  </div>
  <div id="map" :data-group="selectedGroups">
    <div id="map-element" >
    </div>
  </div>
</div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import mapBaseMixin from "../map/mapBaseMixin.vue";
import {GET} from "../common/utils.js";
import MapSelector from "../lobby/mapSelector.vue";

export default {
  components: {MapSelector},
  mixins: [mapBaseMixin],
  data() {
    const thresholds = [
          1, 4, 15, 20, 30
      ];
    const indices = [...thresholds.keys()];
    return {
      difficulty: 100,
      thresholds: thresholds,
      indices: indices,
      baseMap: "IT",
      datapoints: undefined,
      nPoints: 0,
      scales: [
        {scale: 0, name: "Monde"},
        {scale: 1, name: "Continent"},
        {scale: 2, name: "Pays"},
      ],
      selected: [undefined, undefined],
      selectedGroups: "0123456",
      datasets: [datasets[5]],
    }
  },

  mounted() {
    this.initialize("map-element", {
      allowZoom: true,
      maxZoom: 18,
      extraCanvasParams: {
        zoomSnap: 0.1
      }
    });

    this.loadPoints(this.baseMap);
  },

  methods: {
    addPoints(points) {
      if (!points || points.length === 0) return;
      if (typeof this.datapoints === "undefined") this.datapoints = L.featureGroup().addTo(this.canvas);
      points.forEach(point => {
        const [lat, lon] = point.coords;
        const group = this.findGroup(point.data.rank);
        const marker = this.createMarker({lat, lon}, point.data.name, `g${group}`);
        marker.rank = point.data.rank;
        marker.addTo(this.canvas);
        this.datapoints.addLayer(marker);
      });
      // this.canvas.flyToBounds(this.datapoints.getBounds());
    },

    belongsTo(point, i) {
      if (i === 0) return point.rank <= this.thresholds[i];
      return (this.thresholds[i-1] < point.rank) && (point.rank <= this.thresholds[i]);
    },

    findGroup(rank, thresholds) {
      if (typeof thresholds === "undefined") thresholds = this.thresholds;
      for (let i=0; i < thresholds.length; i++){
        if (rank <= thresholds[i]) return i;
      }
      return thresholds.length;
    },

    loadPoints(newBaseMap){
    GET(`/points/${newBaseMap}?labels=true`).then(data => {
        this.removeAllLayers();
        this.datapoints = L.featureGroup().addTo(this.canvas);
        this.nPoints = data.points.length;
        this.canvas.fitBounds(data.bbox);
        this.addPoints(data.points);
      })
    },

    updateThreshold(e, i) {
      const oldThresholds = [...this.thresholds];
      this.thresholds[i] = parseInt(e.target.value);
      if (this.datapoints) {
        const oldGroup = p => `g${this.findGroup(p.rank, oldThresholds)}`;
        const newGroup = p => `g${this.findGroup(p.rank, this.thresholds)}`;
        this.datapoints.eachLayer(point => {
          point._icon.classList.remove(oldGroup(point))
          point._icon.classList.add(newGroup(point))
        });
      }
    },

    getButton(scale, index) {
      const level = index - scale;
      return {
        disabled: level < 0 || level >= 3,
        label: ["Facile", "Normal", "Difficile"][level] || "Indef.",
      } ;
    },

    select(scale, index) {
      if ((this.selected[0] === scale) && (this.selected[1] === index)) {
        this.selected = [undefined, undefined];
        this.selectedGroups = "0123456";
        return;
      }
      this.selected = [scale, index];
      this.selectedGroups = ""
      const minGid = scale;
      const maxGid = Math.min(scale+3, index);
      console.log("min/max gid", minGid, maxGid);
      for (let i=0; i <= maxGid; i++) {
        this.selectedGroups += String(i);
      }
      console.log(this.selectedGroups);
    },

  },

  computed: {
    nSelected() {
      return Math.max(...this.thresholds);
    },

    fileContent() {
      const table = [
        ["map", "points", "selected", ...this.indices],
        [this.baseMap, this.nPoints, this.nSelected, ...this.thresholds],
      ];
      const content = table.map(line => line.join(";")).join("\n");
      return "data:text/plain;charset=utf-8," + encodeURIComponent(content);
    },

    filename () {
      return `selected__${this.baseMap}.txt`
    }
  },

  watch: {
    baseMap(newBaseMap) {
      this.loadPoints(newBaseMap);
    },
  }

}
</script>

<style scoped>
.data-builder {
  position: absolute;
  top: -8px;
  bottom:0;
  left: 0;
  right:0;
}

#map {
  /*position: absolute;*/
  /*top: 0px;*/
  /*bottom:0;*/
  /*left: 0;*/
  /*right:0;*/
  height: 100vh;
  z-index: 1;
}

#map-element {
  height: 100vh;
  z-index: 1;
}
.controls {
  position: fixed;
  top: 10px;
  left: 10px;
  /*width: 250px;*/
  z-index: 2;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
}

.sliders {
  margin: 0 15px;
}

.slidecontainer {
  white-space: nowrap;
}

.diff-counter {
  width: 40px;
}

button.selected {
  border-color: black;

}

</style>
<style>

.ams-icon {
  transition: background-color 0.2s ease-out;
}

.ams-icon.g0,
.ams-icon.g1,
.ams-icon.g2,
.ams-icon.g3,
.ams-icon.g4,
.ams-icon.g5 {
  opacity: 0;
}

#map[data-group*="0"] .ams-icon.g0 {
  opacity: 1;
  background-color: #fd0d0d;
}

#map[data-group*="1"] .ams-icon.g1 {
  opacity: 1;
  background-color: red;
}

#map[data-group*="2"] .ams-icon.g2 {
  opacity: 1;
  background-color: #d90101;
}

#map[data-group*="3"] .ams-icon.g3 {
  opacity: 1;
  background-color: #a70000;
}

#map[data-group*="4"] .ams-icon.g4 {
  opacity: 1;
  background-color: #8b0000;
}

#map[data-group*="5"] .ams-icon.g5 {
  opacity: 0.6;
  background-color: gray;
}

/*.world-0 .ams-icon:not(.g1) {*/
/*  display: none;*/
/*}*/

/*.world-1 .ams-icon:not(g1):not(g2) {*/
/*  display: none;*/
/*}*/

/*.continent-1 .ams-icon:not(g1):not()*/
</style>