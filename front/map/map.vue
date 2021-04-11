<template>
  <div id="map-wrapper" :class="[mapClass, shaded ? 'shaded': '']">
    <div id="mapid"></div>
  </div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import {mapState} from "vuex";
import mapBaseMixin from "./mapBaseMixin.vue";
import {summary2, generateFakeSummary} from "../common/debug.js";
import {CREDITS, CREDITS_SHORT, getIcon} from "../common/map.js";

export default {
  data() {
    return {
      answers: undefined,
      refWorld: 0,
      groundTruth: undefined,
      ownGuess: undefined,
      shaded: false,
      precorrectionState: undefined,
    }
  },

  mixins: [
      mapBaseMixin
  ],

  mounted() {
    this.initialize("mapid", {
      allowZoom: true, // this.params.allow_zoom || this.isMobile,
      bounds: this.params.bbox,
      maxZoom: canvas => (this.isMobile ? 18 : (canvas.getZoom() + 1)),
      credits: this.isNarrow ? CREDITS_SHORT : CREDITS,
    });
    this.canvas.on("mousedown", this.ctrlClickMap);
    this.canvas.on("click", this.submitGuess);
  },

  computed: {
    // isMobile () {
    //   return this.$store.getters.isMobile;
    // },

    isRunning () {
      return this.gameStatus === constants.status.RUNNING;
    },

    autozoomActivated () {
      return this.$store.getters.autozoom;
    },

    hasGroundTruth () {
      return typeof this.groundTruth !== "undefined";
    },

    hasOwnGuess () {
      return typeof  this.ownGuess !== "undefined";
    },

    mapClass () {
      console.log(this.tileType);
      return this.tileType;
    },

    ...mapState({
      params: state => state.params,
      gameLaunched: state => state.game.launched,
      hasAnswered: state => state.game.hasAnswered,
      playerId: state => state.playerId,
      gameStatus: state => state.game.status,
    })
  },

  methods: {
    startCorrectionMode(summary) {
      this.precorrectionState = this.getMapState();
      // Allow unrestricted zoom during correction
      this.enableZoom();
      this.canvas.setMaxZoom(18);
      this.displayGameSummary(summary);
    },

    endCorrection() {
      // Come back to the state prior to correction (incl. zoom)
      if (typeof this.precorrectionState !== "undefined") {
        this.setMapState(this.precorrectionState, constants.animations.map.duration);
      }
      this.precorrectionState = undefined;
    },

    displayGameSummary({places, records}){
      this.clearMap();
      for (let i=0; i<records.length;i++){
        let rec = records[i];//.concat(this.generateFakeRunSummary(places[i]));
        this.displayRunSummary(rec, places[i])
      }
    },

    displayRunSummary(records, {lon, lat, location}){
      /*
      I still have to settle how to display the game summary. The summary view has
      basically two views:
      - default view (every run is displayed)
      - focus on one run (typically, when hovering on ground truth)
      There are four kinds of items:
      - marker + label for each run's ground truth (1 per run)
      - marker (+ optional label) for each guess (1 per run and per player)
      - lines from ground truth to guesses (1 per run and per player)
      - circles from ground truth to guesse (1 per run and per player)
      TODO: when this is settled, remove extra lines and clean the code
       */
      const trueCoords = L.latLng(lat, lon);
      const truth = L.marker([lat, lon], {
        zIndexOffset: 20,
        icon: getIcon(constants.colors.TRUE, location, {extraClasses: ["summary-icon", "truth-icon"]})});
      //const run = L.featureGroup().addTo(this.canvas);
      //run.addLayer(truth);
      const runCircles = L.featureGroup().addTo(this.canvas);
      const runIcons = L.featureGroup(); //.addTo(this.canvas);
      const runLines = L.featureGroup().addTo(this.canvas);
      const runLightIcons = L.featureGroup().addTo(this.canvas);
      const run = L.featureGroup([
          truth,
          // runLightIcons,
          // runIcons,
          // runLines
      ]).addTo(this.canvas);
      const styles = {
        line: {
          activated: false,
          on: {
            opacity: 1,
            color: "purple",
            //weight: 1,
          },
          off: {
            opacity: 0.2,
            color: "black",
          }
        },
        circle: {
          activated: true,
          on: {
            fillOpacity: 0.2,
            stroke: true,
            weight: 2,
            opacity: 1.,
          },
          off: {
            fillOpacity: 0,
            //stroke: false,
            opacity: 0.5,
            weight: 1,
          }
        }
      }
      records.forEach(record => {
        const isSelf = (record.player === "Player_1") || (record.player === this.playerId);
        const color = (isSelf ? constants.colors.SELF : constants.colors.BASE);
        const marker = this.createMarker(record.guess, isSelf ? "Vous" : "", color);
        const lightMarker = this.createMarker(record.guess, "", "black", {extraClasses: ["light"]});
        const guessCoords = L.latLng(record.guess.lat, record.guess.lon);

        const line = L.polyline(
            [trueCoords, guessCoords],
            {
              //color: "black", //constants.colors.BASE,
              ...styles.line.off,
            });
        const circle = L.circle(trueCoords, {
          radius: trueCoords.distanceTo(guessCoords),
          color: color,
          ...styles.circle.off,
        });
        if (styles.line.activated) {
          runLines.addLayer(line);
        }
        runIcons.addLayer(marker);
        if (styles.circle.activated && isSelf) {
          runCircles.addLayer(circle);
        }
        runLightIcons.addLayer(lightMarker);
        //run.addLayer(line);
      });
      //run.addTo(this.canvas);
      run.on("mouseover", () => {
        this.shaded = true;
        runCircles.setStyle(styles.circle.on);
        runLines.setStyle(styles.line.on);
        runIcons.addTo(this.canvas);
      });
      run.on("mouseout", () => {
        this.shaded = false;
        runCircles.setStyle(styles.circle.off);
        runLines.setStyle(styles.line.off);
        runIcons.remove();
      })
    },

    ctrlClickMap(e){
      if (e.originalEvent.ctrlKey) {
        this.submitGuess(e);
        e.originalEvent.preventDefault();
      }
    },

    submitGuess(e) {
      const coords = e.latlng;
      const data = {
        lon: coords.lng,
        lat: coords.lat,
        player: this.playerId,
      };
      if (!this.isRunning || this.hasAnswered) {
        return ;
      }
      this.addOwnMarker(data);
      this.$socketEmit("guess", data);
      this.$store.commit("answerSubmitted");
    },

    addMarker(lat, lon, label, color=constants.color.BASE){
      if (typeof this.answers === "undefined"){
        this.answers = L.featureGroup().addTo(this.canvas);
      }
      const marker = this.createMarker({lat, lon}, label, color);
      this.answers.addLayer(marker);
      return marker
    },

    addOwnMarker(lonlat){
      this.ownGuess = lonlat;
      const marker = this.createMarker(this.ownGuess,
          this.getPlayerName(this.playerId), constants.colors.SELF);
      if (typeof this.answers === "undefined"){
        this.answers = L.featureGroup().addTo(this.canvas);
      }
      this.answers.addLayer(marker);
    },

    addTrueMarker({lon, lat, name}) {
      this.groundTruth = {lon, lat}
      if (this.hasOwnGuess){
        this.groundTruth = this.moveToSameWorld(this.groundTruth, this.ownGuess);
      }
      const marker = this.createMarker(this.groundTruth, name, constants.colors.TRUE);
      if (typeof this.answers === "undefined"){
        this.answers = L.featureGroup().addTo(this.canvas);
      }
      this.answers.addLayer(marker);
    },

    displayResults(answer, results){
      if (!this.hasGroundTruth) {
        this.addTrueMarker(answer);
      }
      const circles = results.map(rec => {
        const isSelf = (rec.player === this.$store.state.playerId)
        if (isSelf && this.hasOwnGuess) {
          return Promise.resolve();
        }
        const color = isSelf ? constants.colors.SELF : constants.colors.BASE;
        return this.drawAnimatedCircle(this.groundTruth, rec.dist, color)
            .then(circle => {
              const marker = this.createMarker(this.moveToSameWorld(rec.guess, this.groundTruth),
                  this.getPlayerName(rec.player), color);
              //if (isSelf) {this.hasOwnGuess = true;}
              this.answers.addLayer(marker);
            });
      });
      Promise.all(circles).then(() => {
        this.autoZoomOnResults(this.answers, results);
      })
    },

    autoZoomOnResults(answers, results) {
      if (!this.autozoomActivated || (results.length === 0)) { return }
      // Store current map view
      const refState = this.getMapState();
      // Disable zoom events (which allows us to unset max zoom)
      this.disableZoom();
      this.canvas.setMaxZoom(18);
      const bounds = answers.getBounds().pad(0.5);
      this.canvas.flyToBounds(bounds, {
        duration: constants.animations.map.duration});
      window.setTimeout(() => {
        this.setMapState(refState, constants.animations.map.duration);

      }, 1000 * (this.params.wait_time - 2 * constants.animations.map.duration - constants.animations.map.deltaPad))
    },

    clearMap(){
      this.removeAllLayers();
      this.groundTruth = undefined;
      this.ownGuess = undefined;
      this.answers = undefined;
    }
  },

  events: {
    "run-end": function (data) {
      this.clearMap();
      this.displayResults(data.answer, data.results);
    },

    "run-start": function() {
      this.clearMap();
    },

    "status-update": function({status, payload}) {
      if (status === constants.status.CORRECTION){
        this.displayResults(payload.answer, payload.results);
      } else if (status === constants.status.RUNNING || status === constants.status.LAUNCHING) {
          this.clearMap();
          if (status === constants.status.LAUNCHING) this.endCorrection();
      } else if (status === constants.status.FINISHED){
        //this.displayGameSummary(payload.full);
        this.startCorrectionMode(payload.full);
      }
    },

    "score": function ({answer, dist}) {
      this.addTrueMarker(answer);
      this.drawAnimatedCircle(this.groundTruth, dist, constants.colors.SELF);
    }
  }
}
</script>

<style scoped>
  #mapid {
    height: 100%;
    background-color: black;
  cursor: crosshair;
}

  #map-wrapper {
    height: 100%;
  }

</style>
<style>

.shaded .truth-icon:not(:hover) {
  /*opacity: 0!important;*/
  background-color: rgba(0, 0, 0, 0.2) !important;
}

.shaded .truth-icon .icon-label {
  /*background-color: rgba(0, 0, 0, 0.2) !important;*/
  opacity: 0 !important;
}

.truth-icon .icon-label:hover {
  background-color: blue !important;
  opacity: 1 !important;
}

.terrain .leaflet-tile {
  filter: grayscale(100%) brightness(50%) contrast(250%);
}
</style>