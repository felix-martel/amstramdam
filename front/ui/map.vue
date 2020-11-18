<template>
  <div id="mapid"></div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import {LAYERS, CREDITS, getIcon} from "../common/map";
import {mapState} from "vuex";

export default {
  data() {
    return {
      canvas: undefined,
      map: undefined,
      groundTruth: undefined,
    }
  },

  mounted() {
    console.log("Map created");
    this.canvas = L.map("mapid", {
         scrollWheelZoom: true, //this.params.allow_zoom || this.isMobile,
         doubleClickZoom: true, //this.params.allow_zoom || this.isMobile,
    });
    this.canvas.fitBounds(this.params.bbox);
    const normalZoom = this.canvas.getZoom();
    const maxZoom = this.isMobile ? 18 : (normalZoom + 1);
    this.canvas.setMaxZoom(maxZoom);
    this.map = L.tileLayer(LAYERS.bwSSL, {
      zoomControl: false,
      attribution: CREDITS,
      // minZoom: currGame.zoom,
    });
    this.map.addTo(this.canvas);
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
      if (!this.isRunning || this.hasAnswered) { return ;}
      const coords = e.latlng;
      const data = {
        lon: coords.lng,
        lat: coords.lat,
        player: this.playerId,
      };
      this.addMarker(data.lat, data.lon, this.getPlayerName(this.playerId), constants.colors.SELF);
      this.$socketEmit("guess", data);
      this.$store.commit("answerSubmitted");
    },
    drawCircle({lat, lon, radius, color, onEnd}) {
      // 1: initialize circle
      const circle = L.circle([lat, lon], {
        color: color,
        radius: 0.01
      });
      circle.addTo(this.canvas);

      // 2: animate circle
      const timestep = 5;
      // convert kilometers to meters
      const finalRadius = radius * 1000;
      const step = finalRadius / timestep;
      const interval = setInterval(() => {
        let currentRadius = circle.getRadius();
        if (currentRadius < finalRadius){
          circle.setRadius(currentRadius * step);
        } else {
          clearInterval(interval);
          if (onEnd) {
            onEnd();
          }
        }
      }, timestep);

      return circle;
    },
    drawCirclePromise(lat, lon, radius, color) {
      return new Promise(resolve => {
        // 1: initialize circle
        const circle = L.circle([lat, lon], {
          color: color,
          radius: 0.01
        });
        circle.addTo(this.canvas);

        // 2: animate circle
        const timestep = 5;
        // convert kilometers to meters
        const finalRadius = radius * 1000;
        const step = finalRadius / timestep;
        const interval = setInterval(() => {
          let currentRadius = circle.getRadius();
          if (currentRadius < finalRadius){
            circle.setRadius(currentRadius + step);
          } else {
            clearInterval(interval);
            resolve(circle);
          }
        }, timestep);
      });
    },
    addMarker(lat, lon, label, color=constants.color.BASE){
      const marker = L.marker([lat, lon], {icon: getIcon(color, label)});
      marker.addTo(this.canvas);
      return marker
    },
    displayResults(answer, results){
      const trueAnswer = this.addMarker(answer.lat, answer.lon, answer.name, constants.colors.TRUE);
      const answers = L.featureGroup([trueAnswer]).addTo(this.canvas);
      // const circles = data.results.map(rec => {
      //   return new Promise(resolve => {
      //     const color = (rec.player === this.$store.state.playerId) ? constants.colors.SELF : constants.colors.BASE;
      //     this.drawCirclePromise(answer.lon, answer.lat, rec.dist, color)
      //         .then(circle => {
      //           const marker = this.addMarker(rec.guess.lat, rec.guess.lon, this.getPlayerName(rec.player), color);
      //           answers.addLayer(marker);
      //           resolve();
      //         });
      //     })
      //   });
      const circles = results.map(rec => {
        const color = (rec.player === this.$store.state.playerId) ? constants.colors.SELF : constants.colors.BASE;
        return this.drawCirclePromise(answer.lat, answer.lon, rec.dist, color)
            .then(circle => {
              const marker = this.addMarker(rec.guess.lat, rec.guess.lon, this.getPlayerName(rec.player), color);
              answers.addLayer(marker);
            });
      })
      Promise.all(circles).then(() => {
        this.autoZoomOnResults(answers, results);
      })
    },
    autoZoomOnResults(answers, results) {
      console.log("Autozoom", this.autozoomActivated);
      if (!this.autozoomActivated || (results.length === 0)) { return }
      const refState = this.getMapState();
      //this.canvas.setMaxZoom(18);
      const bounds = answers.getBounds().pad(0.5);
      this.canvas.flyToBounds(bounds, {
        duration: constants.animations.map.duration, maxZoom: 18});
      window.setTimeout(() => {
        this.setMapState(refState);
      }, 1000 * (this.params.wait_time - 2 * constants.animations.map.duration - constants.animations.map.deltaPad))
    },
    getMapState(){
      return {
          center: this.canvas.getCenter(),
          zoom: this.canvas.getZoom(),
          maxZoom: this.canvas.getMaxZoom(),
        };
    },
    setMapState({center, zoom, maxZoom}){
      this.canvas.flyTo(center, zoom, {duration: constants.animations.map.duration});
      //this.canvas.setMaxZoom(maxZoom);
    },
    clearMap(){
      this.canvas.eachLayer(layer => {
        if (layer !== this.map) {
          this.canvas.removeLayer(layer);
        }
      })
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

    "score": function ({answer, dist}) {
      this.addMarker(answer.lat, answer.lon, answer.name, constants.colors.TRUE);
      this.drawCirclePromise(answer.lat, answer.lon, dist, constants.colors.SELF);
    }
  }
}
</script>