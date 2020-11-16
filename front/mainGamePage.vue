<template>
  <div>
    <div class="blink-wrapper off" id="blink-wrapper">
        <div class="blink-item" id="left"></div>
        <div class="blink-item" id="right"></div>
        <div class="blink-item" id="top"></div>
        <div class="blink-item" id="bottom"></div>
    </div>
    <div class="main">
        <game-footer></game-footer>
        <div class="popup-container" id="popup-container" hidden>
            <div id="mask">

            </div>
            <div id="popup" class="box">
                <div class="popup-left">
                    <div class="box no-border" id="chat-box-popup">
                    <div class="inner-chat">

                        <div class="messages-wrapper">
                            <div id="chat-messages-popup" class="chat-messages">

                            </div>

                        </div>
                        <div class="input">
                            <textarea name="chat-input" id="chat-input-popup" class="chat-input" placeholder="Envoyez un message"></textarea>
                        </div>
                        </div>
                    </div>
                </div>
                <div class="popup-main">
                    <h2 class="blue">Partie terminée</h2>
                    <h4 class="high-score-notif no-score" id="new-highscore-notif">C'est votre meilleur score !</h4>
                <table id="final-results">

                </table>
                <button id="relaunch-from-popup">Nouvelle partie</button>
                <div style="margin-top:15px;">
                    <a  href="/">
                        Retour à l'accueil
                    </a>
                </div>
                </div>

            </div>
        </div>
      <div class="column" id="left-column-display">
        <score-box></score-box>
        <chat-box :hidden="!panelVisibility.chatBox"></chat-box>


        <div class="box" id="results" hidden>
          <div class="individual-results">
            <div id="answer-name" class="title"></div>
            <div class="distance"><span id="main-disp-dist">0</span> km</div>
            <div class="deets">
              <div class="score-dist"><i id="disp-dist">0</i> km = <i id="disp-score-dist">0</i> pts</div>
              <div class="score-time"><i id="disp-time">0</i>s = <i id="disp-score-time">0</i> pts</div>
            </div>

          </div>

          <div class="score">
            <span id="curr-score">0</span> pts
          </div>

          <div class="collective-results">
            <ul id="current-results">

            </ul>
          </div>
        </div>
      </div>

        <div class="right-corner" id="game-box" hidden>
            <div class="game-info box" id="display-hint">
                <span class="run-info">
                    <span id="run-current">0</span>/<span id="run-total">0</span>
                </span>
                <span id="target"></span>
                <div class="progress-container">
                    <div class="progress-inner">
                    <div class="wrapper" id="countdown-animation-wrapper" data-anim="base wrapper">
                      <div class="circle" id="countdown-animation-left" data-anim="base left"></div>
                      <div class="circle" id="countdown-animation-right" data-anim="base right"></div>
                    </div>

                    </div>
                </div>
            </div>
            <div class="box hidden" id="display-timer">
                <span class="timer-text">
                    <span id="timer-legend">Prochaine manche dans </span><span id="run-timer"></span>...</span>
            </div>
        </div>

        <div id="mapid"></div>
        <!--<audio id="beep" hidden src="[[ url_for('static',filename='bip.mp3') ]]"></audio>-->
    </div>
  </div>
</template>
<script>
//import store from "./store"
import scoreBox from "./panels/scoreBox.vue";
import chatBox from "./panels/chatBox.vue";
import gameFooter from "./ui/footer.vue";

export default {
    components: {
      'score-box': scoreBox,
      "chat-box": chatBox,
      "game-footer": gameFooter,
    },
    data () {
      return {
        demo: "demo",
        params: {},
      }
    },

  computed: {
      panelVisibility () {
        return this.$store.state.ui;
      }
  },

    created () {
      console.log("'mainGamePage' mounted.");
      console.log(this.$store.state.params);
      this.$socketOn("connect", () => {
        let pseudo; // TODO: read from cookie
        console.debug("Connecting... Current pseudo is", pseudo);
        this.$socketEmit("connection", {data: "connected", pseudo: pseudo});
      })

      this.$socketOn("log", data => console.log(data));

      this.$socketOn("init", data => {
        console.debug(`You're now connected as <${data.pseudo}> (id=${data.player})`);
        this.$store.commit("updatePseudos", data.pseudos);
        this.$store.commit("setPlayer", data.player);
      })
    },
}
</script>
<style>

</style>