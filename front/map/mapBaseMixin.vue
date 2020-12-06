<template>

</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import constants from "../common/constants";
import {LAYERS, CREDITS, defaultView, defaultBounds, getIcon} from "../common/map";
export default {
  data() {
    return {
      canvas: undefined,
      map: undefined,
    }
  },

  created() {

  },

  methods: {
    /**
     * Initialize a Leaflet component with:
     * - `this.canvas`: a `L.map` object
     * - `this.map`: a `L.tileLayer` layer, added to `this.canvas`
     *
     * @param identifier - the DOM <div> element where the map will be instantiated (can be provided
     * as a DOM ID or as a HTML element.
     * @param {Boolean} [allowZoom=true] - allow scrollWheelZoom and doubleClickZoom
     * @param [bounds] - which bounds the map must be fitted to
     * @param {String} [credits] - map attributions
     * @param [maxZoom=18] - maximum zoom. Can be a number, a function taking the canvas as argument and
     * returning the maximum zoom.
     * @param [tiles] - which tiling service to use. Must be a URL template (see Leaflet doc)
     * @param [extraCanvasParams] - optional parameter object that will be passed to `L.map`
     * @param [extraTileParams] - optional parameter object that will be passed to `L.tileLayer`
     */
    initialize(identifier, {
      allowZoom = true,
      bounds = defaultBounds,
      credits = CREDITS,
      maxZoom = 18,
      tiles = LAYERS.bwSSL,
      extraCanvasParams = {},
      extraTileParams = {},
    } = {}) {
      this.canvas = L.map(identifier, {
        scrollWheelZoom: allowZoom,
        doubleClickZoom: allowZoom,
        zoomControl: false,
        boxZoom: false,
        bounceAtZoomLimits: false,
        //worldCopyJump: true,
        ...extraCanvasParams
      });
      this.canvas.fitBounds(bounds);
      if (typeof maxZoom === "number"){
        this.canvas.setMaxZoom(maxZoom);
      }
      else if (typeof maxZoom === "function"){
        this.canvas.setMaxZoom(maxZoom(this.canvas));
      }
      else if (typeof maxZoom === "undefined"){
        this.canvas.setMaxZoom(18);
      }
      this.map = L.tileLayer(tiles, {
        zoomControl: false,
        attribution: credits,
        ...extraTileParams
      });
      this.map.addTo(this.canvas);
    },


    createMarker({lat, lon}, label, color=constants.colors.BASE, options){
      // TODO: cleaner interface OR remove entirely
      return L.marker([lat, lon], {icon: getIcon(color, label, options)});
    },

    drawAnimatedCircle({lat, lon}, radius, color, timestep=5) {
      return new Promise(resolve => {
        // 1: initialize circle
        const circle = L.circle([lat, lon], {
          color: color,
          radius: 0.01
        });
        circle.addTo(this.canvas);

        // 2: animate circle
        //const timestep = 5;
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

    disableZoom(){
      // This assume the `initialize` method has already been called
      this.canvas.scrollWheelZoom.disable();
      this.canvas.doubleClickZoom.disable();
    },

    enableZoom() {
      // This assume the `initialize` method has already been called
      this.canvas.scrollWheelZoom.enable();
      this.canvas.doubleClickZoom.enable();
    },


    getMapState(){
      return {
          center: this.canvas.getCenter(),
          zoom: this.canvas.getZoom(),
          maxZoom: this.canvas.getMaxZoom(),
          zoomAllowed: this.canvas.scrollWheelZoom.enabled(),
        };
    },

    setMapState({center, zoom, maxZoom, zoomAllowed}, duration){
      if (typeof duration === "undefined"){
        this.canvas.setView(center, zoom);
        if (maxZoom) {this.canvas.setMaxZoom(maxZoom);}
        if (zoomAllowed) {this.enableZoom();}
      } else {
        this.canvas.flyTo(center, zoom, {duration: duration});
        // Wait for the end of the flight...
        window.setTimeout(() => {
          // ...then re-enable zoom and set max zoom
          if (maxZoom) {this.canvas.setMaxZoom(maxZoom);}
          if (zoomAllowed) {this.enableZoom();}
        }, duration*1000);
      }
    },

    removeAllLayers(){
      this.canvas.eachLayer(layer => {
        if (layer !== this.map) {
          this.canvas.removeLayer(layer);
        }
      });
    },

    /**
     * The world number of a point (lon, lat) is the integer k such that
     * 360*k - 180 <= lon <= 360*k + 180
     * In the default view, k=0. If you pan to the right, you'll see a second copy of the world,
     * which corresponds to k=1, then a third (k=2), and so on. If you pan to the right, you'll
     * have k=-1, -2, ...
     *
     * @returns {number} - the point's world copy id
     */
    getWorldId({lon, lat}) {
      return Math.floor((lon + 180) / 360);
    },

    /**
     * Move a point to a given copy of the world (see `getWorldId` above)
     *
     * @returns {Object} - a {lon, lat} object
     */
    moveToWorld({lon, lat}, worldId) {
      return {
        lat: lat,
        lon: lon + (worldId - this.getWorldId({lon, lat})) * 360
      }
    },

    /**
     * Given a reference point B, move a point A such that the geographic distance between A and B
     * matches the map distance between them. Consider the following example:
     * const A = {lon: -179, lat: 0}
     * const B = {lon: 179, lat: 0}
     * These two points are close to each other (2° away, which is approx. 200km). Yet, when displayed
     * on a map, they will litteraly be a world away: A at the western/left edge of the map, B at
     * the eastern/right. But if you compute:
     * const C = moveToSameWorld(A, B)
     * {lon: 181, lat: 0}
     * and you display B and C, they'll close both geographically and on the map.
     *
     * @param point - the point that should be moved ('A' above)
     * @param reference - the reference point ('B' above)
     * @returns {{lon: *, lat: *}}
     */
    moveToSameWorld(point, reference){
      // Step 1: put everyone into the same copy of the world;
      const world = this.getWorldId(reference);
      const moved = this.moveToWorld(point, world);
      // Step 2: moved to nearest
      if (moved.lon > reference.lon + 180) {
        moved.lon -= 360;
      } else if (moved.lon < reference.lon - 180) {
        moved.lon += 360;
      }
      return moved;
    }
  }
}
</script>

<style scoped>

</style>