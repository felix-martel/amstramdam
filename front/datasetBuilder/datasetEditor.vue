<template>
<div class="data-builder">
  <div class="controls box">
    <div class="stats">
      <map-selector :datasets="datasets" v-model="baseMap"></map-selector>
      <div class="slidecontainer" v-for="(selected, level) in levels">
        <button
            class="group-selector"
            :class="{'selected': selected}"
            @click="levels[level] = !levels[level]"
        >G{{ level}}</button>
      </div>
    </div>
    <table>
      <tbody>
      <tr>
        <td v-for="column in columns">{{ column }}</td>
      </tr>
      <tr>
        <td v-for="column in columns">
          <input type="text" :value="currentData[column] || ''" :readonly="column === 'pid'"
                 @input="processChange($event, currentPid, column)">
        </td>
      </tr>
      </tbody>
    </table>
    <div>
      <button @click="getChanges">Voir les changements</button>
      <button @click="createPoint">Nouveau</button>
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
import {GET, unproxify} from "../common/utils.js";
import MapSelector from "../lobby/mapSelector.vue";
import {getIcon} from "../common/map.js";

export default {
  components: {MapSelector},
  mixins: [mapBaseMixin],
  data() {
    const levels = [true, false, false, false, false];
    return {
      levels: levels,
      columns: [],
      currentPoint: {},
      baseMap: {},
      nPoints: 0,
      datasets: datasets,
      changes: {
        update: {},
        create: {}
      },
      nChanged: 0,
      nCreated: 0,
      markers: {},
      dataframe: {},
      focusedMarker: {data: {}},
      currentPid: undefined,
      dragging: false,
      initCoords: undefined
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
    this.canvas.on("keydown", this.interruptDragging);
  },

  methods: {
    emptyMarker() {
      return {data: {}}
    },

    renderPoint(pid) {
      if (!(pid in this.dataframe) ){
        console.log("Unknown pid", pid);
        return;
      }
      const data = this.dataframe[pid];
      const lat = data.lat;
      const lon = data[this.lonCol]; // <- longitude is sometimes labeled "lon" and sometimes "lng"
      const group = data.group || 0;
      const classname = `g${group}`;
      const name = data[this.labelCol]; // data.place || data.city;

      const marker = L.marker([lat, lon], {draggable: true, icon: getIcon(classname, name)});
      marker.pid = pid;
      this.markers[pid] = marker;
      marker.on("click", this.clickMarker);
      marker.on("dragstart", this.startDragging);
      marker.on("dragend", this.endDragging);

      marker.addTo(this.canvas);
      return marker;
    },

    startDragging(event) {
      console.log(`Interrupt dragging P[${event.target.pid}]`);
      this.currentPid = event.target.pid;
      this.dragging = true;
      //
      // this.focusedMarker = event.target;
      // const {lat, lng} = this.focusedMarker.getLatLng();
      // this.initCoords = {lat, lon: lng};
      // this.dragging = true;
    },

    interruptDragging(event) {
      console.log(event);
      console.log(this.dragging);
      if (event.originalEvent.key === "Escape" && this.dragging) {
        console.log(`Interrupt dragging P[${this.currentPid}]`);
        const marker = this.markers[this.currentPid];
        const data = this.dataframe[this.currentPid];
        marker.dragging.disable();
        marker.setLatLng([data.lat, data[this.lonCol]]);
        marker.dragging.enable();
      }
    },

    endDragging(event) {
      console.log(`Interrupt dragging P[${event.target.pid}]`);
      const {lat, lng} = this.markers[this.currentPid].getLatLng();
      this.dragging = false;
      this.setValue(lat, this.currentPid, "lat"); // <- false bc marker is already up-to-date
      this.setValue(lng, this.currentPid, this.lonCol); // <- false bc marker is already up-to-date
    },

    clickMarker(event) {
      console.log("Clicked", event.target.pid);
      this.currentPid = event.target.pid;
    },

    renderDataframe() {
      for (let pid in this.dataframe){
        this.renderPoint(pid);
      }
    },

    createDataFrame(points) {
      if (!points) return {};
      const dataframe = {};
      points.forEach(point => {
        dataframe[point.pid] = point;
      });
      return dataframe;
    },

    loadPoints(newBaseMap){
    GET(`/edit/${newBaseMap.map_id}`).then(data => {
        this.removeAllLayers();
        this.markers = {};
        this.dataframe = this.createDataFrame(data.points);
        this.columns = data.columns;
        this.nPoints = data.points.length;
        if (data.bbox) {
          this.canvas.fitBounds(data.bbox);
        }
        this.renderDataframe();
      })
    },

    processChange(event, pid, column) {
      const value = event.target.value.trim();
      this.setValue(value, pid, column);
    },

    setValue(value, pid, column) {
      this.dataframe[pid][column] = value;

      if (pid in this.changes.update) {
        this.changes.update[pid][column] = value;
      } else {
        this.changes.update[pid] = {[column]: value};
        this.nChanged ++;
      }
      this.updateMarker(pid);
      console.log(`P[${pid}].${column} updated to ${value}`);
    },

    updateMarker(pid) {
      if (pid in this.markers) {
        this.canvas.removeLayer(this.markers[pid])
        this.markers[pid] = undefined;
        this.renderPoint(pid);
      }
    },

    createPoint() {
      let pid = Math.max(...Object.keys(this.dataframe)) + 1;
      console.log(`Creating point with pid=${pid}`);
      const {lat, lng} = this.canvas.getCenter();
      const data = {};
      this.columns.forEach(col => {
        data[col] = "";
      });
      data["lat"] = lat;
      data[this.lonCol] = lng;
      data["pid"]  = pid;
      data[this.labelCol] = "Nouveau point";
      this.dataframe[pid] = data;
      this.renderPoint(pid);
      this.currentPid = pid;
    },

    getChanges() {
      console.log(unproxify(this.changes.update))
    }

  },

  computed: {
    selectedGroups () {
      let groups = "";
      this.levels.forEach((s, i) => {
        if (s) groups += String(i);
      })
      return groups;
    },

    lonCol () {
      if (this.columns.includes("lng")) return "lng";
      return "lon";
    },

    labelCol() {
      return "place";
    },

    currentData () {
      if (typeof this.currentPid === "undefined" || !(this.currentPid in this.dataframe)) {
        return {}
      } else {
        return this.dataframe[this.currentPid];
      }
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
  height: 100vh;
  z-index: 1;
}

table, td {
  border: 1px solid lightgrey;
  border-collapse: collapse;
}
table {
  margin: 15px 0;
}
td {
  padding: 5px;
  max-width: 100px;
  overflow: hidden;
  font-size: 0.9em;
}

#map-element {
  height: 100vh;
  z-index: 1;
}

.controls {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 2;
}

.stats {
  display: flex;
  flex-flow: row nowrap;
}

.slidecontainer {
  margin-left: 10px;
  display: flex;
  flex-flow: row nowrap;
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
  display: none;
}

#map[data-group*="0"] .ams-icon.g0 {
  opacity: 1;
  display: block;
  background-color: #fd0d0d;
}

#map[data-group*="1"] .ams-icon.g1 {
  opacity: 1;
  display: block;
  background-color: red;
}

#map[data-group*="2"] .ams-icon.g2 {
  opacity: 1;
  display: block;
  background-color: #d90101;
}

#map[data-group*="3"] .ams-icon.g3 {
  opacity: 1;
  display: block;
  background-color: #a70000;
}

#map[data-group*="4"] .ams-icon.g4 {
  opacity: 1;
  display: block;
  background-color: #8b0000;
}

#map[data-group*="5"] .ams-icon.g5 {
  opacity: 0.6;
  display: block;
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