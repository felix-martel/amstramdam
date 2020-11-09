/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./front/lobby.js":
/*!************************!*\
  !*** ./front/lobby.js ***!
  \************************/
/*! namespace exports */
/*! exports [not provided] [no usage info] */
/*! runtime requirements: __webpack_require__, __webpack_require__.r, __webpack_exports__, __webpack_require__.* */
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./utils */ "./front/utils.js");
;

document.addEventListener("DOMContentLoaded", () => {
    const LAYERS = {
        default: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        alt: 'https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
        watercolor: 'http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
        terrain: 'http://c.tile.stamen.com/terrain-background/{z}/{x}/{y}.jpg',
        bw: 'http://tile.stamen.com/toner-background/{z}/{x}/{y}.png',
        bwSSL: 'https://stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png'
    };
    const defaultView = {
            center: [23.7, 7.6],
            zoom: 1
        };
    const difficultySlider = (0,_utils__WEBPACK_IMPORTED_MODULE_0__.$)("diff-level");

    function getIcon(color="red", extraClass="", opacity=0.8){
        const markerHtmlStyles = `
          background: ${color};
          width: 6px;
          height: 6px;
          display: block;
          border-radius: 3px;`;

        return L.divIcon({
            className: "my-custom-pin",
            iconAnchor: [3, 3],
            html: `<span class="icon ${extraClass}" style="${markerHtmlStyles}"></span>`
        })
    }


     var map = L.map('leaflet').setView(defaultView.center, defaultView.zoom);
     var OSM = L.tileLayer(LAYERS.bwSSL, {zoomControl:  false, });
     OSM.addTo(map);

     /* HANDLE DATA POINTS */
     var pointLayer = L.featureGroup();
    pointLayer.addTo(map);

    const gameSelector = document.getElementById("map-selector");
    function GET(theUrl, callback)
    {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
                callback(JSON.parse(xmlHttp.responseText));
        };
        xmlHttp.open("GET", theUrl, true); // true for asynchronous
        xmlHttp.send(null);
    }

    function updateView(){
        if (pointLayer){
            map.removeLayer(pointLayer);
        }
        const dataset = gameSelector.value;
        GET(`/points/${dataset}`, (data) => {
            pointLayer = L.featureGroup();
            var diff = difficultySlider.value / 100;
            var maxRank = Math.min(10, diff * data.points.length);
            data.points.forEach(point => {
                var extraClass = (point.rank > maxRank) ? "hidden" : "";
                var pointMarker = L.marker(point.coords, {icon: getIcon("blue", extraClass)});
                pointMarker.rank = point.data.rank;
                pointLayer.addLayer(pointMarker);
            });
            const bounds = pointLayer.getBounds();
            pointLayer.addTo(map);
            map.flyToBounds(bounds);

        });
    }

    gameSelector.addEventListener("change", () => {
        updateView();
    });

    function updateDifficulty(){
        if (pointLayer){
            var diff = difficultySlider.value / 100;
            var minValue = 0;
            var nLayers = pointLayer.getLayers().length;
            var maxRank = Math.max(10, diff * nLayers);

            pointLayer.eachLayer(point => {
                if (point.rank > maxRank){
                    point._icon.classList.add("hidden");
                } else {
                    point._icon.classList.remove("hidden");
                }
            })
        }
    }
    updateView();
    var gameNameInput = document.getElementById("game-name");
    var gameJoinButton = document.getElementById("join-game-button");
    gameNameInput.addEventListener("keydown", function(event){
        if (event.keyCode === 13){
            event.preventDefault();
            gameJoinButton.click();
        }
    });
    gameJoinButton.addEventListener("click", (e) => {
        e.preventDefault();
        const rawInput = gameNameInput.value;
        const gameName = rawInput.charAt(0).toUpperCase() + rawInput.slice(1).toLowerCase();
        window.location.href = `/game/${gameName}`;
    });
    difficultySlider.addEventListener("change", (e) => {
        updateDifficulty();
    });
})

/***/ }),

/***/ "./front/utils.js":
/*!************************!*\
  !*** ./front/utils.js ***!
  \************************/
/*! namespace exports */
/*! export $ [provided] [no usage info] [missing usage info prevents renaming] */
/*! other exports [not provided] [no usage info] */
/*! runtime requirements: __webpack_require__.r, __webpack_exports__, __webpack_require__.d, __webpack_require__.* */
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "$": () => /* binding */ $
/* harmony export */ });
function $(identifier){
    return document.getElementById(identifier);
}


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		if(__webpack_module_cache__[moduleId]) {
/******/ 			return __webpack_module_cache__[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop)
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	// startup
/******/ 	// Load entry module
/******/ 	__webpack_require__("./front/lobby.js");
/******/ 	// This entry module used 'exports' so it can't be inlined
/******/ })()
;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9hbXN0cmFtZGFtLy4vZnJvbnQvbG9iYnkuanMiLCJ3ZWJwYWNrOi8vYW1zdHJhbWRhbS8uL2Zyb250L3V0aWxzLmpzIiwid2VicGFjazovL2Ftc3RyYW1kYW0vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vYW1zdHJhbWRhbS93ZWJwYWNrL3J1bnRpbWUvZGVmaW5lIHByb3BlcnR5IGdldHRlcnMiLCJ3ZWJwYWNrOi8vYW1zdHJhbWRhbS93ZWJwYWNrL3J1bnRpbWUvaGFzT3duUHJvcGVydHkgc2hvcnRoYW5kIiwid2VicGFjazovL2Ftc3RyYW1kYW0vd2VicGFjay9ydW50aW1lL21ha2UgbmFtZXNwYWNlIG9iamVjdCIsIndlYnBhY2s6Ly9hbXN0cmFtZGFtL3dlYnBhY2svc3RhcnR1cCJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7Ozs7QUFBQSxDQUEwQjs7QUFFMUI7QUFDQTtBQUNBLDJCQUEyQixFQUFFLDRCQUE0QixFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUU7QUFDbkUsdURBQXVELEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRTtBQUNqRSwwREFBMEQsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFO0FBQ3BFLCtEQUErRCxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUU7QUFDekUsc0RBQXNELEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRTtBQUNoRSx3RUFBd0UsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFO0FBQ2xGO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSw2QkFBNkIseUNBQUM7O0FBRTlCO0FBQ0E7QUFDQSx3QkFBd0I7QUFDeEI7QUFDQTtBQUNBO0FBQ0EsNkJBQTZCOztBQUU3QjtBQUNBO0FBQ0E7QUFDQSx1Q0FBdUMsV0FBVyxXQUFXLGlCQUFpQjtBQUM5RSxTQUFTO0FBQ1Q7OztBQUdBO0FBQ0EsMENBQTBDLHNCQUFzQjtBQUNoRTs7QUFFQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLDBDQUEwQztBQUMxQztBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSx1QkFBdUIsUUFBUTtBQUMvQjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsMERBQTBELGtDQUFrQztBQUM1RjtBQUNBO0FBQ0EsYUFBYTtBQUNiO0FBQ0E7QUFDQTs7QUFFQSxTQUFTO0FBQ1Q7O0FBRUE7QUFDQTtBQUNBLEtBQUs7O0FBRUw7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBLGlCQUFpQjtBQUNqQjtBQUNBO0FBQ0EsYUFBYTtBQUNiO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsS0FBSztBQUNMO0FBQ0E7QUFDQTtBQUNBO0FBQ0Esd0NBQXdDLFNBQVM7QUFDakQsS0FBSztBQUNMO0FBQ0E7QUFDQSxLQUFLO0FBQ0wsQ0FBQyxDOzs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNqSE07QUFDUDtBQUNBOzs7Ozs7O1VDRkE7VUFDQTs7VUFFQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7O1VBRUE7VUFDQTs7VUFFQTtVQUNBO1VBQ0E7Ozs7O1dDckJBO1dBQ0E7V0FDQTtXQUNBO1dBQ0Esd0NBQXdDLHlDQUF5QztXQUNqRjtXQUNBO1dBQ0EsRTs7Ozs7V0NQQSxzRjs7Ozs7V0NBQTtXQUNBO1dBQ0E7V0FDQSxzREFBc0Qsa0JBQWtCO1dBQ3hFO1dBQ0EsK0NBQStDLGNBQWM7V0FDN0QsRTs7OztVQ05BO1VBQ0E7VUFDQTtVQUNBIiwiZmlsZSI6ImxvYmJ5LmpzIiwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHskfSBmcm9tIFwiLi91dGlsc1wiO1xuXG5kb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKFwiRE9NQ29udGVudExvYWRlZFwiLCAoKSA9PiB7XG4gICAgY29uc3QgTEFZRVJTID0ge1xuICAgICAgICBkZWZhdWx0OiAnaHR0cHM6Ly97c30udGlsZS5vcGVuc3RyZWV0bWFwLmZyL2hvdC97en0ve3h9L3t5fS5wbmcnLFxuICAgICAgICBhbHQ6ICdodHRwczovL3RpbGVzLndtZmxhYnMub3JnL29zbS1uby1sYWJlbHMve3p9L3t4fS97eX0ucG5nJyxcbiAgICAgICAgd2F0ZXJjb2xvcjogJ2h0dHA6Ly9jLnRpbGUuc3RhbWVuLmNvbS93YXRlcmNvbG9yL3t6fS97eH0ve3l9LmpwZycsXG4gICAgICAgIHRlcnJhaW46ICdodHRwOi8vYy50aWxlLnN0YW1lbi5jb20vdGVycmFpbi1iYWNrZ3JvdW5kL3t6fS97eH0ve3l9LmpwZycsXG4gICAgICAgIGJ3OiAnaHR0cDovL3RpbGUuc3RhbWVuLmNvbS90b25lci1iYWNrZ3JvdW5kL3t6fS97eH0ve3l9LnBuZycsXG4gICAgICAgIGJ3U1NMOiAnaHR0cHM6Ly9zdGFtZW4tdGlsZXMuYS5zc2wuZmFzdGx5Lm5ldC90b25lci1iYWNrZ3JvdW5kL3t6fS97eH0ve3l9LnBuZydcbiAgICB9O1xuICAgIGNvbnN0IGRlZmF1bHRWaWV3ID0ge1xuICAgICAgICAgICAgY2VudGVyOiBbMjMuNywgNy42XSxcbiAgICAgICAgICAgIHpvb206IDFcbiAgICAgICAgfTtcbiAgICBjb25zdCBkaWZmaWN1bHR5U2xpZGVyID0gJChcImRpZmYtbGV2ZWxcIik7XG5cbiAgICBmdW5jdGlvbiBnZXRJY29uKGNvbG9yPVwicmVkXCIsIGV4dHJhQ2xhc3M9XCJcIiwgb3BhY2l0eT0wLjgpe1xuICAgICAgICBjb25zdCBtYXJrZXJIdG1sU3R5bGVzID0gYFxuICAgICAgICAgIGJhY2tncm91bmQ6ICR7Y29sb3J9O1xuICAgICAgICAgIHdpZHRoOiA2cHg7XG4gICAgICAgICAgaGVpZ2h0OiA2cHg7XG4gICAgICAgICAgZGlzcGxheTogYmxvY2s7XG4gICAgICAgICAgYm9yZGVyLXJhZGl1czogM3B4O2A7XG5cbiAgICAgICAgcmV0dXJuIEwuZGl2SWNvbih7XG4gICAgICAgICAgICBjbGFzc05hbWU6IFwibXktY3VzdG9tLXBpblwiLFxuICAgICAgICAgICAgaWNvbkFuY2hvcjogWzMsIDNdLFxuICAgICAgICAgICAgaHRtbDogYDxzcGFuIGNsYXNzPVwiaWNvbiAke2V4dHJhQ2xhc3N9XCIgc3R5bGU9XCIke21hcmtlckh0bWxTdHlsZXN9XCI+PC9zcGFuPmBcbiAgICAgICAgfSlcbiAgICB9XG5cblxuICAgICB2YXIgbWFwID0gTC5tYXAoJ2xlYWZsZXQnKS5zZXRWaWV3KGRlZmF1bHRWaWV3LmNlbnRlciwgZGVmYXVsdFZpZXcuem9vbSk7XG4gICAgIHZhciBPU00gPSBMLnRpbGVMYXllcihMQVlFUlMuYndTU0wsIHt6b29tQ29udHJvbDogIGZhbHNlLCB9KTtcbiAgICAgT1NNLmFkZFRvKG1hcCk7XG5cbiAgICAgLyogSEFORExFIERBVEEgUE9JTlRTICovXG4gICAgIHZhciBwb2ludExheWVyID0gTC5mZWF0dXJlR3JvdXAoKTtcbiAgICBwb2ludExheWVyLmFkZFRvKG1hcCk7XG5cbiAgICBjb25zdCBnYW1lU2VsZWN0b3IgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChcIm1hcC1zZWxlY3RvclwiKTtcbiAgICBmdW5jdGlvbiBHRVQodGhlVXJsLCBjYWxsYmFjaylcbiAgICB7XG4gICAgICAgIHZhciB4bWxIdHRwID0gbmV3IFhNTEh0dHBSZXF1ZXN0KCk7XG4gICAgICAgIHhtbEh0dHAub25yZWFkeXN0YXRlY2hhbmdlID0gZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICBpZiAoeG1sSHR0cC5yZWFkeVN0YXRlID09PSA0ICYmIHhtbEh0dHAuc3RhdHVzID09PSAyMDApXG4gICAgICAgICAgICAgICAgY2FsbGJhY2soSlNPTi5wYXJzZSh4bWxIdHRwLnJlc3BvbnNlVGV4dCkpO1xuICAgICAgICB9O1xuICAgICAgICB4bWxIdHRwLm9wZW4oXCJHRVRcIiwgdGhlVXJsLCB0cnVlKTsgLy8gdHJ1ZSBmb3IgYXN5bmNocm9ub3VzXG4gICAgICAgIHhtbEh0dHAuc2VuZChudWxsKTtcbiAgICB9XG5cbiAgICBmdW5jdGlvbiB1cGRhdGVWaWV3KCl7XG4gICAgICAgIGlmIChwb2ludExheWVyKXtcbiAgICAgICAgICAgIG1hcC5yZW1vdmVMYXllcihwb2ludExheWVyKTtcbiAgICAgICAgfVxuICAgICAgICBjb25zdCBkYXRhc2V0ID0gZ2FtZVNlbGVjdG9yLnZhbHVlO1xuICAgICAgICBHRVQoYC9wb2ludHMvJHtkYXRhc2V0fWAsIChkYXRhKSA9PiB7XG4gICAgICAgICAgICBwb2ludExheWVyID0gTC5mZWF0dXJlR3JvdXAoKTtcbiAgICAgICAgICAgIHZhciBkaWZmID0gZGlmZmljdWx0eVNsaWRlci52YWx1ZSAvIDEwMDtcbiAgICAgICAgICAgIHZhciBtYXhSYW5rID0gTWF0aC5taW4oMTAsIGRpZmYgKiBkYXRhLnBvaW50cy5sZW5ndGgpO1xuICAgICAgICAgICAgZGF0YS5wb2ludHMuZm9yRWFjaChwb2ludCA9PiB7XG4gICAgICAgICAgICAgICAgdmFyIGV4dHJhQ2xhc3MgPSAocG9pbnQucmFuayA+IG1heFJhbmspID8gXCJoaWRkZW5cIiA6IFwiXCI7XG4gICAgICAgICAgICAgICAgdmFyIHBvaW50TWFya2VyID0gTC5tYXJrZXIocG9pbnQuY29vcmRzLCB7aWNvbjogZ2V0SWNvbihcImJsdWVcIiwgZXh0cmFDbGFzcyl9KTtcbiAgICAgICAgICAgICAgICBwb2ludE1hcmtlci5yYW5rID0gcG9pbnQuZGF0YS5yYW5rO1xuICAgICAgICAgICAgICAgIHBvaW50TGF5ZXIuYWRkTGF5ZXIocG9pbnRNYXJrZXIpO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBjb25zdCBib3VuZHMgPSBwb2ludExheWVyLmdldEJvdW5kcygpO1xuICAgICAgICAgICAgcG9pbnRMYXllci5hZGRUbyhtYXApO1xuICAgICAgICAgICAgbWFwLmZseVRvQm91bmRzKGJvdW5kcyk7XG5cbiAgICAgICAgfSk7XG4gICAgfVxuXG4gICAgZ2FtZVNlbGVjdG9yLmFkZEV2ZW50TGlzdGVuZXIoXCJjaGFuZ2VcIiwgKCkgPT4ge1xuICAgICAgICB1cGRhdGVWaWV3KCk7XG4gICAgfSk7XG5cbiAgICBmdW5jdGlvbiB1cGRhdGVEaWZmaWN1bHR5KCl7XG4gICAgICAgIGlmIChwb2ludExheWVyKXtcbiAgICAgICAgICAgIHZhciBkaWZmID0gZGlmZmljdWx0eVNsaWRlci52YWx1ZSAvIDEwMDtcbiAgICAgICAgICAgIHZhciBtaW5WYWx1ZSA9IDA7XG4gICAgICAgICAgICB2YXIgbkxheWVycyA9IHBvaW50TGF5ZXIuZ2V0TGF5ZXJzKCkubGVuZ3RoO1xuICAgICAgICAgICAgdmFyIG1heFJhbmsgPSBNYXRoLm1heCgxMCwgZGlmZiAqIG5MYXllcnMpO1xuXG4gICAgICAgICAgICBwb2ludExheWVyLmVhY2hMYXllcihwb2ludCA9PiB7XG4gICAgICAgICAgICAgICAgaWYgKHBvaW50LnJhbmsgPiBtYXhSYW5rKXtcbiAgICAgICAgICAgICAgICAgICAgcG9pbnQuX2ljb24uY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKTtcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICBwb2ludC5faWNvbi5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH0pXG4gICAgICAgIH1cbiAgICB9XG4gICAgdXBkYXRlVmlldygpO1xuICAgIHZhciBnYW1lTmFtZUlucHV0ID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoXCJnYW1lLW5hbWVcIik7XG4gICAgdmFyIGdhbWVKb2luQnV0dG9uID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoXCJqb2luLWdhbWUtYnV0dG9uXCIpO1xuICAgIGdhbWVOYW1lSW5wdXQuYWRkRXZlbnRMaXN0ZW5lcihcImtleWRvd25cIiwgZnVuY3Rpb24oZXZlbnQpe1xuICAgICAgICBpZiAoZXZlbnQua2V5Q29kZSA9PT0gMTMpe1xuICAgICAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAgIGdhbWVKb2luQnV0dG9uLmNsaWNrKCk7XG4gICAgICAgIH1cbiAgICB9KTtcbiAgICBnYW1lSm9pbkJ1dHRvbi5hZGRFdmVudExpc3RlbmVyKFwiY2xpY2tcIiwgKGUpID0+IHtcbiAgICAgICAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICBjb25zdCByYXdJbnB1dCA9IGdhbWVOYW1lSW5wdXQudmFsdWU7XG4gICAgICAgIGNvbnN0IGdhbWVOYW1lID0gcmF3SW5wdXQuY2hhckF0KDApLnRvVXBwZXJDYXNlKCkgKyByYXdJbnB1dC5zbGljZSgxKS50b0xvd2VyQ2FzZSgpO1xuICAgICAgICB3aW5kb3cubG9jYXRpb24uaHJlZiA9IGAvZ2FtZS8ke2dhbWVOYW1lfWA7XG4gICAgfSk7XG4gICAgZGlmZmljdWx0eVNsaWRlci5hZGRFdmVudExpc3RlbmVyKFwiY2hhbmdlXCIsIChlKSA9PiB7XG4gICAgICAgIHVwZGF0ZURpZmZpY3VsdHkoKTtcbiAgICB9KTtcbn0pIiwiZXhwb3J0IGZ1bmN0aW9uICQoaWRlbnRpZmllcil7XG4gICAgcmV0dXJuIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKGlkZW50aWZpZXIpO1xufVxuIiwiLy8gVGhlIG1vZHVsZSBjYWNoZVxudmFyIF9fd2VicGFja19tb2R1bGVfY2FjaGVfXyA9IHt9O1xuXG4vLyBUaGUgcmVxdWlyZSBmdW5jdGlvblxuZnVuY3Rpb24gX193ZWJwYWNrX3JlcXVpcmVfXyhtb2R1bGVJZCkge1xuXHQvLyBDaGVjayBpZiBtb2R1bGUgaXMgaW4gY2FjaGVcblx0aWYoX193ZWJwYWNrX21vZHVsZV9jYWNoZV9fW21vZHVsZUlkXSkge1xuXHRcdHJldHVybiBfX3dlYnBhY2tfbW9kdWxlX2NhY2hlX19bbW9kdWxlSWRdLmV4cG9ydHM7XG5cdH1cblx0Ly8gQ3JlYXRlIGEgbmV3IG1vZHVsZSAoYW5kIHB1dCBpdCBpbnRvIHRoZSBjYWNoZSlcblx0dmFyIG1vZHVsZSA9IF9fd2VicGFja19tb2R1bGVfY2FjaGVfX1ttb2R1bGVJZF0gPSB7XG5cdFx0Ly8gbm8gbW9kdWxlLmlkIG5lZWRlZFxuXHRcdC8vIG5vIG1vZHVsZS5sb2FkZWQgbmVlZGVkXG5cdFx0ZXhwb3J0czoge31cblx0fTtcblxuXHQvLyBFeGVjdXRlIHRoZSBtb2R1bGUgZnVuY3Rpb25cblx0X193ZWJwYWNrX21vZHVsZXNfX1ttb2R1bGVJZF0obW9kdWxlLCBtb2R1bGUuZXhwb3J0cywgX193ZWJwYWNrX3JlcXVpcmVfXyk7XG5cblx0Ly8gUmV0dXJuIHRoZSBleHBvcnRzIG9mIHRoZSBtb2R1bGVcblx0cmV0dXJuIG1vZHVsZS5leHBvcnRzO1xufVxuXG4iLCIvLyBkZWZpbmUgZ2V0dGVyIGZ1bmN0aW9ucyBmb3IgaGFybW9ueSBleHBvcnRzXG5fX3dlYnBhY2tfcmVxdWlyZV9fLmQgPSAoZXhwb3J0cywgZGVmaW5pdGlvbikgPT4ge1xuXHRmb3IodmFyIGtleSBpbiBkZWZpbml0aW9uKSB7XG5cdFx0aWYoX193ZWJwYWNrX3JlcXVpcmVfXy5vKGRlZmluaXRpb24sIGtleSkgJiYgIV9fd2VicGFja19yZXF1aXJlX18ubyhleHBvcnRzLCBrZXkpKSB7XG5cdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywga2V5LCB7IGVudW1lcmFibGU6IHRydWUsIGdldDogZGVmaW5pdGlvbltrZXldIH0pO1xuXHRcdH1cblx0fVxufTsiLCJfX3dlYnBhY2tfcmVxdWlyZV9fLm8gPSAob2JqLCBwcm9wKSA9PiBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwob2JqLCBwcm9wKSIsIi8vIGRlZmluZSBfX2VzTW9kdWxlIG9uIGV4cG9ydHNcbl9fd2VicGFja19yZXF1aXJlX18uciA9IChleHBvcnRzKSA9PiB7XG5cdGlmKHR5cGVvZiBTeW1ib2wgIT09ICd1bmRlZmluZWQnICYmIFN5bWJvbC50b1N0cmluZ1RhZykge1xuXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBTeW1ib2wudG9TdHJpbmdUYWcsIHsgdmFsdWU6ICdNb2R1bGUnIH0pO1xuXHR9XG5cdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCAnX19lc01vZHVsZScsIHsgdmFsdWU6IHRydWUgfSk7XG59OyIsIi8vIHN0YXJ0dXBcbi8vIExvYWQgZW50cnkgbW9kdWxlXG5fX3dlYnBhY2tfcmVxdWlyZV9fKFwiLi9mcm9udC9sb2JieS5qc1wiKTtcbi8vIFRoaXMgZW50cnkgbW9kdWxlIHVzZWQgJ2V4cG9ydHMnIHNvIGl0IGNhbid0IGJlIGlubGluZWRcbiJdLCJzb3VyY2VSb290IjoiIn0=