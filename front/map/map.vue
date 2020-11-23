<template>
  <div id="mapid"></div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import {mapState} from "vuex";
import mapBaseMixin from "./mapBaseMixin.vue";
export default {
  data() {
    return {
      answers: undefined,
      refWorld: 0,
      groundTruth: undefined,
      ownGuess: undefined,
    }
  },

  mixins: [
      mapBaseMixin
  ],

  mounted() {
    console.log("Map created");
    this.initialize("mapid", {
      allowZoom: this.params.allow_zoom || this.isMobile,
      bounds: this.params.bbox,
      maxZoom: canvas => (this.isMobile ? 18 : (canvas.getZoom() + 1))
    });
    this.canvas.on("click", this.submitGuess);
  },

  computed: {
    isMobile () {
      return this.$store.getters.isMobile;
    },

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

    ...mapState({
      params: state => state.params,
      gameLaunched: state => state.game.launched,
      hasAnswered: state => state.game.hasAnswered,
      playerId: state => state.playerId,
      gameStatus: state => state.game.status,
    })
  },

  methods: {
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
      console.log("Added own guess");
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
      console.log("Added ground truth");
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

</style>
<style>

.my-custom-pin {
  opacity: 1;
  transition: 0.2s ease-in opacity;
}
.my-custom-pin.hidden {
  opacity: 0;
}

.icon {
  position: relative;
}

.icon-label {
  position: absolute;
  /*top: -10px;
  left: 20px;*/
  white-space: nowrap;
}
</style>