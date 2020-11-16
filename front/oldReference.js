import {CountUp} from "countup.js";
import Countdown from "./ui/countdown";
import AmstramdamApp from "./mainGamePage.vue";

import { createApp } from 'vue'
import io from "socket.io-client";
//import store from './store';
import initStore from './store';
import 'leaflet/dist/leaflet.css';
import L from "leaflet";
import SocketIOPlugin from "./socket";

//import {$} from "./common/utils";



document.addEventListener("DOMContentLoaded", () => {
    const socket = io({
        rejectUnauthorized: false, // !params.debug,
    });
    const app = createApp(AmstramdamApp)
    const istore = initStore(params);
    app.use(istore);
    app.use(SocketIOPlugin, socket);

    app.mount('#amstramdam');

    console.log(istore);

    const $ = document.getElementById;
    //$("sharing-link").innerHTML = window.location.href.replace("https://", "").replace("www.", "");
    const blinkContainer = document.getElementById("blink-wrapper");
    //const audioBeep = $("beep");
    var hintContainer = $("target");
    var playerName = $("player-name");
    var playerList = $("player-list");
    var scorer = $("total-score");
    var gameLauncher = $("launch");
    var gameRelauncher = $("relaunch-from-popup");
    var gameBox = $("game-box");
    var gameHint = $("display-hint");
    var gameWaitDisplayer = $("display-timer");
    var gameLaunched = false;
    var runLaunched = false;
    var hasAnswered = false;
    var clickable = false;
    var PLAYER;
    var PLAYERS = [];
    var PSEUDOS = {};
    var LEADERBOARD = [];
    var nRuns;
    var currRun = 0;
    var autozoomCheckbox = $("autozoom-check");
    var newMessageWhileHidden = false;
    var invertModeButton = $("colinvert-check");
    var highScore;
    var deltaHighScore;
    var gameName;
    const runCountdown = new Countdown("countdown-animation", params.duration);

    autozoomCheckbox.checked = readAutozoom();
    invertModeButton.checked = readInverted();
    if (invertModeButton.checked){
        $("mapid").classList.add("inverted");
    }
    if (!readChatVisibility()){
        $("chat-box").classList.add("hidden");
    }
    function chatIsHidden(){
        return $("chat-box").classList.contains("hidden");
    }

    updatePlayerList();
    function blink(audio= true){
        const duration = 100; // In millisec
        blinkContainer.classList.remove("off");
        // if (audio) {audioBeep.play();}
        window.setTimeout(() => {
            blinkContainer.classList.add("off");
        }, duration);
    }
    function getIcon(color="red", name="", labelOnly=false, random=false){
        const iconColor = labelOnly ? "transparent" : color;
        const markerHtmlStyles = `
          background: ${iconColor};
          width: 10px;
          height: 10px;
          display: block;
          border-radius: 5px;`;
        var inner;
        if (name) {
            let x = 15;
            let y = 15;
            if (random){
                x = 2* (Math.random()-0.5);
                y = Math.sqrt(1 - Math.pow(x, 2));
                if (Math.random() > 0.5){
                    y = -y;
                }
                x = Math.round((15 + 15*Math.random())*x);
                y = Math.round((15 + 15*Math.random())*y);
            }
            const labelStyle = `
            background-color: ${color};
            color: white;
            padding: 3px;
            top: ${x}px;
            left: ${y}px;
            position: absolute;
            font-family: "Roboto", monospace;
            `;
            inner = `<span class="icon-label" style="${labelStyle}">${name}</span>`;
        }
        else {
            inner = "";
        }

        return L.divIcon({
            className: "my-custom-pin",
            iconAnchor: [5, 5],
            html: `<span class="icon" style="${markerHtmlStyles}">${inner}</span>`
        })
    }
    function getLabelIcon(color="red", name=""){

    }

    function getPlayerName(name){
        return PSEUDOS[name] || name;
    }
    function updatePseudos(pseudos){
        PSEUDOS = pseudos || {};
        updatePlayerList();
    }
    function addPseudo(player, name){
        PSEUDOS[player] = name;
        updatePlayerList();
    }

    let franceZoom = 6;
    let worldZoom = 2;
    let zoom = worldZoom;
    const LAYERS = {
        default: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        alt: 'https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
        watercolor: 'http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
        terrain: 'http://c.tile.stamen.com/terrain-background/{z}/{x}/{y}.jpg',
        bw: 'http://tile.stamen.com/toner-background/{z}/{x}/{y}.png',
        bwSSL: 'https://stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png'
    };
    var centerFrance = [46.758162, 2.812324];
    var centerWorld = [23.7, 7.6];
    const isMobile = mobileCheck();
    const game = {
        france: {
            center: centerFrance,
            zoom: franceZoom
        },
        world: {
            center: centerWorld,
            zoom: worldZoom
        },
    };


    const currGame = game; // game.world;
     var map = L.map('mapid', {
         // zoomSnap: 0,
         scrollWheelZoom: params.allow_zoom || isMobile,
         doubleClickZoom: params.allow_zoom || isMobile,
     }); //.setView(currGame.center, currGame.zoom);
    map.fitBounds(params.bbox);
     function mobileCheck() {
          let check = false;
          (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
          return check;
        };

     const maxZoom = isMobile ? 6 : currGame.zoom+2;

     var OSM = L.tileLayer(LAYERS.bwSSL, {
	    //maxZoom: currGame.zoom, //maxZoom,
        minZoom: currGame.zoom,
         zoomControl:  false, //false,

	 //attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>'
     attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a> and  <a href="https://simplemaps.com/data/world-cities">World Cities Database</a> under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>',
     });
    OSM.addTo(map);
    //var spider = new OverlappingMarkerSpiderfier(map);
    var correctionCircle;

     function updatePlayerList(){
         playerList.innerHTML = "";
         LEADERBOARD.forEach(el => {
             if (el.player === PLAYER){
                 scorer.innerHTML = el.score;
                 displayDiffWithHighScore(el.score);
                 playerList.innerHTML += `<li><i><span class="pname">${getPlayerName(el.player)}*</span><span class="pscore">${el.score} pts</span></i></li>`
             }
             else {
                playerList.innerHTML += `<li><span class="pname">${getPlayerName(el.player)}</span><span class="pscore">${el.score} pts</span></li>`
             }
         });
     }
     function fullShowResults(results){
         let table = "";
         results.forEach((el, i) => {
             var crown = (i === 0) ? " <i class='fas fa-crown first-place'></i>" : "";
             table += `<tr>
                    <td class="rank">${i+1}</td>
                    <td class="player-name">${getPlayerName(el.player)}${crown}</td>
                    <td class="player-score-deets"><i class="fas fa-ruler"></i>${Math.round(el.dist)}km</td>
                    <td class="player-score-deets"><i class="fas fa-clock"></i>${Math.round(100*el.delta)/100}s</td>
                    <td class="player-score">${el.score}pts</td>
                </tr>`
         });
       $("final-results").innerHTML = table;
       $("popup-container").hidden = false;
     }
     function hideResults(){
        $("new-highscore-notif").classList.add("no-score");
       $("popup-container").hidden = true;
     }
     function displayGameBox(hint, currRun, totalRun){
        gameBox.hidden = true;
        gameHint.classList.remove("hidden");
         gameWaitDisplayer.classList.add("hidden");
        $("run-current").innerHTML = currRun + 1;
        $("run-total").innerHTML = totalRun;
        target.innerHTML = hint;
        gameBox.hidden = false;
     }
     function hideGameBox(){
         gameBox.hidden = true;
     }
     const TEXTS = {
         beforeNewRun: "Prochaine manche dans ",
         beforeGameEnd: "Partie finie, palmarès dans ",
         beforeGameStart: "Début de partie dans "
     }
     function startWaitTimer({
                                 duration= params.wait_time,
                                 label= TEXTS.beforeNewRun
     } = {}){
         gameHint.classList.add("hidden");
         gameWaitDisplayer.classList.remove("hidden");
         gameBox.hidden = false;

         //var duration = params.wait_time;
         $("timer-legend").innerHTML = label;
         $("run-timer").innerHTML = duration;
         var waitInterval = window.setInterval(() => {
             duration = duration - 1;
             if (duration >= 0) {
                 $("run-timer").innerHTML = duration;
             }
             else {
                 window.clearInterval(waitInterval);
             }
         }, 1000); // Update every second

     }

        function addGuessEntry(name, distance){
            // $("results").hidden = false;
            showRunResults();
            var resultContainer = $("current-results");
            distance = Math.round(distance);
            resultContainer.innerHTML += `<li><span class="pname">${getPlayerName(name)}</span><span class="pscore">${distance}km</span></li>`;
        }
        function clearGuessEntries(){
            $("current-results").innerHTML = "";
        }
    function makeAnimatedCircle(lat, lon, radius, color, onEnd){
         var newRadius = radius*1000; // Kilometres to meters
         let circle = L.circle([lat, lon], {
                color: color,
                // fillColor: color,
                // fillOpacity: 0.1,
                radius: 0.01
            });
         circle.addTo(map);
         let duration = 400;
         let timestep = 5;
         let step = newRadius / timestep;
        //return;

        var interval = setInterval(function() {
           var currentRadius = circle.getRadius();
           if (currentRadius < newRadius) {
               circle.setRadius(currentRadius + step);
           } else {
               clearInterval(interval);
               if (onEnd){
                onEnd();

               }
           }
        }, timestep);

        return circle;
    }
    function showRunResults(){
         const container = $("left-column-display");
         if (!container.classList.contains("with-results")){
             container.classList.add("with-results");
         }
         $("results").hidden = false;
    }
    function hideRunResults(){
         const container = $("left-column-display");
         if (container.classList.contains("with-results")){
             container.classList.remove("with-results");
         }
         $("results").hidden = true;
    }
    const blinkDelay = 3; // In seconds: screen will blink `blinkDelay` seconds before run end
    const blinkTimestep = 500; // In milliseconds
    var blinkTimeout;
    var blinkInterval;


        // var socket = io({
        //     rejectUnauthorized: false, // !params.debug,
        // });
        socket.on('connect', function() {
            var pseudo = getPseudoFromCookie();
            console.debug("Connecting... Current pseudo is", pseudo);
            socket.emit('connection', {data: 'I\'m connected!', pseudo: pseudo});
        });
        socket.on('disconnect', function() {
            console.debug("Disconnecting...");
        });
        socket.on('redirect', function (data) {
            console.debug(`Redirecting to ${data.url}...`);
            window.location.href = data.url;
        })
        socket.on("log", function(data){
            console.debug(data);
        });
        socket.on("game-launched", (data) => {
            console.debug("Received: game launched");
            hideResults();
            clearMap();
            gameName = [data.game, data.runs, data.diff].join("_");
            highScore = getHighscore(gameName);
            deltaHighScore = highScore / data.runs;
            hideDiffWithHighScore();
            console.debug("Your score for game", gameName, "is", highScore);

            gameLaunched = true;
            gameLauncher.disabled = true;
            startWaitTimer({duration: 3, label: TEXTS.beforeGameStart});
        });
        socket.on("game-end", (data) => {
           console.debug("Game ended!");
           LEADERBOARD = data.leaderboard;
           updatePlayerList();

           var selfResults = data.full["summary"].find(rec => (rec.player === PLAYER));
           if (selfResults){
               var latestScore = selfResults.score;
               if ((latestScore && !highScore) || latestScore >= highScore){
                   console.debug("You have a new high score:", latestScore);
                   saveHighscore(gameName, latestScore);
                   highScore = latestScore;
                   displayHighscore();
                   hideDiffWithHighScore();
                   $("new-highscore-notif").classList.remove("no-score");
               }
               gameLaunched = false;
           }

           fullShowResults(data.full["summary"]);

        });
        socket.on("marker", function(data){
            var name = data.name || "";
            var color = data.color || "red";
            addMarker(data.lat, data.lon, name, color)
        });
        socket.on("run-start", (data) => {
            runLaunched = true;
            console.debug(`Run started, place to find is «${data.hint}»`);
            clearMap();
            clearGuessEntries();
            hideRunResults();
            runCountdown.start();

            hasAnswered = false;
            //$("results").hidden = true;
            displayGameBox(data.hint, data.current, data.total);
            currRun = data.current+1;
            /*gameBox.hidden = true;
            $("results").hidden = true;
            $("run-current").innerHTML = data.current+1;
            $("run-total").innerHTML = data.total;
            target.innerHTML = data.hint;
            gameBox.hidden = false;*/

            blinkTimeout = window.setTimeout(() => {
                console.debug(`${blinkDelay} seconds remaining...`);
                blinkInterval = window.setInterval(() => {
                    blink(false);
                }, blinkTimestep);
            }, 1000*(params.duration - blinkDelay));
        });
        socket.on("new-guess", (data) => {
            //console.debug(data);
            addGuessEntry(data.player, data.dist);
        });
        function displayDiffWithHighScore(currScore){

            var diffDisplayer = $("high-score-diff");
            if (highScore && currScore !== false && typeof currScore !== "undefined" && gameLaunched){
                const theoricalHighScore = currRun * deltaHighScore;
                const deltaWithHighScore = Math.round(currScore - theoricalHighScore);

                if (deltaWithHighScore >= 0){
                    diffDisplayer.innerHTML = "+" + deltaWithHighScore;
                    diffDisplayer.classList = "pos-score";
                }
                else {
                    diffDisplayer.innerHTML = deltaWithHighScore;
                    diffDisplayer.classList = "neg-score";
                }
            }
            else {
                diffDisplayer.classList = "no-score";
                diffDisplayer.innerHTML = "";
            }
        }
        function hideDiffWithHighScore(){
            var diffDisplayer = $("high-score-diff");
            diffDisplayer.classList = "no-score";
            diffDisplayer.innerHTML = "";
        }

        socket.on("score", (data) => {
            addMarker(data.answer.lat, data.answer.lon, data.answer.name, "blue");
            makeAnimatedCircle(data.answer.lat, data.answer.lon, data.dist, "red");
            scorer.innerHTML = data.total_score;
            const dist = Math.round(data.dist);
            const score = Math.round(data.score);
            displayDiffWithHighScore(data.total_score);


            $("answer-name").innerHTML = data.answer.name;
            $("main-disp-dist").innerHTML = 0; //dist; // Math.round(data.dist);
            $("disp-dist").innerHTML = 0; //dist; // Math.round(data.dist);
            $("disp-score-dist").innerHTML = 0; //Math.round(data.sd);
            $("disp-time").innerHTML = 0; //Math.round(data.delta * 100) / 100;
            $("disp-score-time").innerHTML = 0; // Math.round(data.st);
            $("curr-score").innerHTML = 0; //score; //data.score;
            $("results").hidden = false;

            const distanceCounter = new CountUp('main-disp-dist', dist, {separator: ""});
            distanceCounter.start();
            const scoreCounter = new CountUp('curr-score', score, {separator: ""});

            scoreCounter.start();

            const secDistCounter =  new CountUp("disp-dist", Math.round(data.dist));
            secDistCounter.start();
            const sdCounter =  new CountUp("disp-score-dist", Math.round(data.sd));
            sdCounter.start();
            const timeCounter =  new CountUp("disp-time", Math.round(data.delta * 100)/100);
            timeCounter.start();
            const stCounter =  new CountUp("disp-score-time", Math.round(data.st));
            stCounter.start();
        });
        socket.on("init", (data)=> {
            console.debug(`You're now connected as <${data.pseudo}> (id=${data.player})`);
            PLAYER = data.player;
            updatePseudos(data.pseudos);
            //addPseudo(PLAYER, data.pseudo);

            playerName.innerHTML = getPlayerName(PLAYER);
            playerName.contentEditable = true;

            gameName = [data.game, data.runs, data.diff].join("_");
            highScore = getHighscore(gameName);
            deltaHighScore = highScore / data.runs;
            displayHighscore();
            hideDiffWithHighScore();

            console.debug("High score for game", gameName, ":", highScore);

            gameLaunched = data.launched;
            if (gameLaunched) {
                gameLauncher.disabled = true;
            }
        });
        socket.on("new-name", (data) => {
            console.debug(`Player <${data.change.player}> has a new nickname: "${data.change.pseudo}"`);
            updatePseudos(data.pseudos);
        })
        socket.on("new-player", (data) => {
            console.debug(`Welcome ${data.pseudo} (id=${data.player})`);
            LEADERBOARD = data.leaderboard;
            updatePseudos(data.pseudos);
            updatePlayerList();
        });
        socket.on("player-left", (data) => {
            console.debug("Bye,", data.player);
            LEADERBOARD = data.leaderboard;
            updatePlayerList();
        });
        socket.on("run-end", (data) => {
            runCountdown.end();
            runLaunched = false;
            window.clearInterval(blinkInterval);
            window.clearTimeout(blinkTimeout);
            startWaitTimer({label: data.done ? TEXTS.beforeGameEnd : TEXTS.beforeNewRun});
            clearMap();
            LEADERBOARD = data.leaderboard;
            updatePlayerList();
            displayRun(data);
        });
    var comeBackToPreviousZoom;

    function displayRun(data){
        const trueLon = data.answer.lon;
        const trueLat = data.answer.lat;
        var nAnswers = data.results.length;
        var trueAnswer = addMarker(data.answer.lat, data.answer.lon, data.answer.name, "blue");
        var answers = L.featureGroup([trueAnswer]).addTo(map);
        let requests = data.results.map((rec) => {
            return new Promise((resolve) => {
                let col = (rec.player === PLAYER) ? "red" : "purple";
                makeAnimatedCircle(trueLat, trueLon, rec.dist || 10, col, () => {
                    let marker = addMarker(rec.guess.lat, rec.guess.lon, getPlayerName(rec.player), col);
                    answers.addLayer(marker);
                    resolve();
                });
            });
        });

        if (!isMobile && autozoomCheckbox.checked ){
            const originalCenter = map.getCenter();
            const originalZoom = map.getZoom();
            const originalMaxZoom = map.getMaxZoom();
            const ANIM_DURATION = 0.5;
            const DELTA_PAD = 0.5;
            Promise.all(requests).then(() => {
                if (nAnswers > 0){
                    let bounds = answers.getBounds().pad(0.5);
                    let tempZoom = OSM.maxNativeZoom || 8;
                    map.flyToBounds(bounds, {duration: ANIM_DURATION});
                }
            });
            if (nAnswers > 0){
                comeBackToPreviousZoom = window.setTimeout(() => {
                    map.flyTo(originalCenter, originalZoom, {duration: ANIM_DURATION});
                    map.setMaxZoom(originalMaxZoom);
                    //OSM.maxZoom  = originalMaxZoom;
                }, (params.wait_time-2*ANIM_DURATION - DELTA_PAD)*1000);
            }
        } else {
            if (comeBackToPreviousZoom){
                window.clearTimeout(comeBackToPreviousZoom)
            }
        }
    }
    function encodeGameName(gameName){
        return encodeURIComponent("amstram__" + gameName + "__score");
    }
    function saveHighscore(gameName, score, neverExpire=false){
        gameName = encodeGameName(gameName);
        var expires =  neverExpire ? ";max-age=31536000" : "";
        document.cookie = gameName + "=" + score + expires;
    }
    function getHighscore(gameName){
        gameName = encodeGameName(gameName);
        var cookieValue = document.cookie.split(gameName+"=");
        if (cookieValue.length < 2){
            return false
        }
        var score = parseInt(cookieValue[cookieValue.length-1].split(";")[0]);
        if (!score){
            return false
        }
        return score
    }
    function clearHighscore(gameName){
        saveHighscore(gameName, "", true);
    }
    function savePseudoToCookie(value){
        value = encodeURIComponent(value);
        var expires = ";max-age=31536000";
        document.cookie = "amstramdamUsername=" + value + expires;
    }
    function getPseudoFromCookie(){
        var cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)amstramdamUsername\s*\=\s*([^;]*).*$)|^.*$/, "$1");
        cookieValue = decodeURIComponent(cookieValue);
        return cookieValue;
    }
    function storeAutozoom(value){
        document.cookie = `amstramdamAutozoom=${+value}`;
    }
    function readAutozoom(value){
        var cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)amstramdamAutozoom\s*\=\s*([^;]*).*$)|^.*$/, "$1");
        return cookieValue !== "0";
    }
    function storeInverted(value){
        document.cookie = `amstramdamInverted=${+value}`;
    }
    function readInverted(value){
        var cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)amstramdamInverted\s*\=\s*([^;]*).*$)|^.*$/, "$1");
        return (cookieValue !== "0") && (cookieValue !== "");
    }
    function storeChatVisibility(value){
        document.cookie = `amstramdamChatVisible=${+value}`;
    }
    function readChatVisibility(value){
        var cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)amstramdamChatVisible\s*\=\s*([^;]*).*$)|^.*$/, "$1");
        return (cookieValue !== "0") && (cookieValue !== "");
    }
    playerName.addEventListener("keydown", (e) => {
        if (e.keyCode === 13){
            playerName.blur();
        }
        if (playerName.innerHTML.length >= 30){
            e.preventDefault();
        }
    });
    playerName.addEventListener("click", (e) => {
        //playerName.focus();
        e.stopPropagation();
    });
    playerName.addEventListener("focusout", (e) => {
        const newName = playerName.innerHTML;
        if (!newName){
            // Empty name
            playerName.innerHTML = PLAYER;
            return;
        }
        if (newName !== PLAYER){
            console.debug(PLAYER, "has requested a new pseudo", newName);
            socket.emit("name-change", {name: newName});
            savePseudoToCookie(newName);
        }
    });
    gameLauncher.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!gameLaunched){
            socket.emit("launch");
        }
    });
    gameRelauncher.addEventListener("click", (e) => {
        console.debug("Relaunching...");
        e.preventDefault();
        if (!gameLaunched){
            socket.emit("launch");
        }
    });
     function addMarker(lat, lon, name="", color="red", openPopup=false){
         var marker = L.marker([lat, lon], {icon: getIcon(color, name)}).addTo(map);
         //var labelMarker = L.marker([lat, lon], {icon: getIcon(color, name, true)}).addTo(map);
         //spider.addMarker(marker);
         return marker;
     }
     function addGuess(guess, answer, name, color="red", popup=true){
         //addMarker(answer.lat, answer.lon, "", "blue");
        L.polyline(
            [
                [guess.lat, guess.lon],
                [answer.lat, answer.lon]
            ]).addTo(map);
        let marker = addMarker(guess.lat, guess.lon);
        if (popup){
            marker.bindPopup(name).openPopup();
        }
     }
    function clearMap(excludeLayers=[]){
        map.eachLayer(function (layer) {
            if (layer !== OSM &&  layer !== correctionCircle ){ //!excludeLayers.includes(layer)){
                map.removeLayer(layer);
            }
        });
    }
    function onMapClick(e) {
        if (!runLaunched || hasAnswered){
            return
        }
        let coords = e.latlng;
        let data = {
                lon: coords.lng,
                lat: coords.lat,
                player: PLAYER
            };
        addMarker(coords.lat, coords.lng, getPlayerName(PLAYER));
        socket.emit("guess", data);
        hasAnswered = true;
        clickable = false;
    }
    const mainInfoBox = $("main-info-box");
        mainInfoBox.addEventListener("click", () => {
        if (mainInfoBox.classList.contains("toggled")){
            mainInfoBox.classList.remove("toggled");
        } else {
            mainInfoBox.classList.add("toggled");
        }
    });

        autozoomCheckbox.addEventListener("change", () => {
            storeAutozoom(autozoomCheckbox.checked);
        });
        invertModeButton.addEventListener("change", () => {
            storeInverted(invertModeButton.checked);
            $("mapid").classList.toggle("inverted");
        });

        /* CHAT SUPPORT */
    var chatInput = $("chat-input");
    var chatMessages = $("chat-messages");
    var chatInput2 = $("chat-input-popup");
    var chatMessages2 = $("chat-messages-popup");

    function appendMessage(message, author){
            var el = `<div class="chat-message"><span class="chat-author">${getPlayerName(author)}</span><span class="chat-message-content">${message}</span></div>`;
        chatMessages.innerHTML += el;
        chatMessages2.innerHTML += el;
    }
    chatInput.addEventListener("keyup", (e) => {
        if (e.keyCode === 13){
            var message = chatInput.value;
            socket.emit("chat:send", message);
            chatInput.value = "";
            appendMessage(message, PLAYER);
        }
    });
    chatInput2.addEventListener("keyup", (e) => {
        if (e.keyCode === 13){
            var message = chatInput2.value;
            socket.emit("chat:send", message);
            chatInput2.value = "";
            appendMessage(message, PLAYER);
        }
    });

    socket.on("chat:new", (data) => {
        if (data.author !== PLAYER){
            appendMessage(data.message, data.author);
            if (chatIsHidden()){
                $("chat-toggle-button").classList.add("unread-message");
            }
        }
    });

    $("chat-toggle-button").addEventListener("click", () => {
        var state = $("chat-box").classList;
        state.toggle("hidden");
        var visibility;
        if (chatIsHidden()){
            visibility = "0";
        } else {
            $("chat-toggle-button").classList.remove("unread-message");
            visibility = "1";
        }
        storeChatVisibility(visibility);
    });

    $("close-chatbox").addEventListener("click", () => {
        $("chat-box").classList.add("hidden");
        storeChatVisibility("0");
    });

    function displayHighscore(){
        var highScoreContainer = $("high-score-container");
        var highScoreDisplay = $("high-score");

        if (!highScore){
            highScoreContainer.classList.add("no-score");
        }
        else {
            highScoreDisplay.innerHTML = highScore;
            highScoreContainer.classList.remove("no-score");
        }
    }

    map.on('click', onMapClick);
});