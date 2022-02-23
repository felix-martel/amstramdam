<template>

<div class="data-builder">
          <div id="vertical-target"></div>
    <div id="horizontal-target"></div>
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
      <div class="auth-container">
        <input type="password" v-model="authKey" placeholder="Mot de passe">
      </div>
    </div>
    <table>
      <tbody>
      <tr>
        <td v-for="column in columns">{{ column }}</td>
      </tr>
      <tr ref="datarow">
        <td v-for="column in columns" class="cell-inputable">
          <input type="text"
                 :value="typeof currentData[column] === 'undefined' ? '' : currentData[column]"
                 @input="processChange($event, currentPid, column)"
                 @keydown.enter="focusOnMap"
                 :readonly="column === 'pid'"
          >
        </td>
      </tr>
      </tbody>
    </table>
    <div class="dataset-control">
      <button @click="createPoint">Nouveau</button>
      <button disabled @click="commitChanges">Enregistrer</button>
      <button @click="downloadChanges">Télécharger</button>
    </div>
  </div>
  <div id="map" :data-group="selectedGroups">

    <div id="map-element" ref="mapElement">
    </div>
  </div>
</div>

</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import mapBaseMixin from "../map/mapBaseMixin.vue";
import {GET, POST, unproxify} from "../common/utils.js";
import MapSelector from "../lobby/mapSelector.vue";
import {LAYERS, getIcon} from "../common/map.js";

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
      authKey: "",
      changes: {
        update: {},
        create: []
      },
      nChanged: 0,
      nCreated: 0,
      markers: {},
      dataframe: {},
      converter: {},
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
      },
      tiles: LAYERS.labelled,
    });

    this.loadPoints(this.baseMap);
    this.canvas.on("keydown", this.handleKeyEvent);
    this.canvas.on("keyup", (e) => {
      if (e.originalEvent.key === "n") this.createPoint();
    })
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
      const lat = data[this.latCol];
      const lon = data[this.lonCol]; // <- longitude is sometimes labeled "lon" and sometimes "lng"
      const group = data[this.groupCol] || 0;
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

    handleKeyEvent(event) {
      const key = event.originalEvent.key;
      console.log(key);
      if (key === "Escape") {
        this.interruptDragging(event);
      }
    },

    interruptDragging(event) {
      if (this.dragging) {
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

    focusOnMap() {
      this.$refs.mapElement.focus();
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
    GET(`/dataset/${newBaseMap.map_id}?auth=${this.authKey}`).then(data => {
        this.removeAllLayers();
        this.markers = {};
        this.dataframe = this.createDataFrame(data.points);
        this.columns = data.columns;
        this.converter = data.converter;
        this.nPoints = data.points.length;
        if (data.bbox) {
          this.canvas.fitBounds(data.bbox);
        }
        this.renderDataframe();
      })
    },

    commitChanges() {
      return;
      const changes = this.changes;
      changes["auth"] = this.authKey;
      POST(`/commit/${this.baseMap.map_id}`, changes);
    },

    downloadFile(blob, filename) {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    },

    downloadChanges() {
      const changes = this.changes;
      changes["output"] = "download";
      changes["auth"] = this.authKey;
      fetch(`/commit/${this.baseMap.map_id}`, {
        method: "POST",
        headers: new Headers({'Content-Type': 'application/json'}),
        body: JSON.stringify(changes)
      }).then(req => req.blob())
        .then(data => {
          const filename =  this.baseMap.map_id + '_edited.csv';
          this.downloadFile(data, filename);
        });
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
      data[this.latCol] = lat;
      data[this.lonCol] = lng;
      data["pid"]  = pid;
      data[this.labelCol] = "";
      data[this.groupCol] = this.selectedGroupsArray ? Math.min(...this.selectedGroupsArray) : 0;
      this.changes.create.push(data);
      this.dataframe[pid] = data;
      this.renderPoint(pid);
      this.currentPid = pid;

      let el = this.$refs.datarow.firstElementChild;
      if (el && el.firstElementChild) {
        const newNameInput = el.firstElementChild;
        if (newNameInput) {
          newNameInput.focus();
        }
        // el.firstElementChild.focus();
      }
    },

    getChanges() {
      console.log(unproxify(this.changes.update))
    }

  },

  computed: {
    selectedGroupsArray() {
      const groups = [];
      this.levels.forEach((s, i) => {
        if (s) groups.push(i);
      })
      return groups;
    },
    selectedGroups () {
      return this.selectedGroupsArray.join("");
    },

    lonCol () {
      return this.converter["lon"] || "lon";
    },

    labelCol() {
      return this.converter["place"] || "place";
    },

    hintCol() {
      return this.converter["hint"] || "admin";
    },

    latCol () {
      return this.converter["lat"] || "lat";
    },

    groupCol() {
      return this.converter["group"] || "group";
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

#horizontal-target {
  position: fixed;
  left: 0;
  right: 0;
  top: 50%;
  height: 1px;
  background-color: cyan;
  z-index: 2;
}
#vertical-target {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  background-color: cyan;
  z-index: 2;
}

#map {
  /*height: 100vh;*/
  /*z-index: 1;*/
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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

td.cell-inputable {
  padding-top: 3px;
}

table input {
  width: 100%;
  height: 100%;
  border: none;
  border-bottom: 1px solid lightgray;
  box-sizing: border-box;
}

table input:hover {
  border-color: blue;
}

#map-element {
  height: 100%;
  z-index: 1;
}

.controls {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 3;
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

.dataset-control button {
  margin-left: 10px;
}

.auth-container input {
  height: 100%;
  box-sizing: border-box;
  margin-left: 10px;
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