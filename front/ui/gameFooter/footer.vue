<template>
  <div class="footer" id="game-sharing-link">
    <div class="current-game">
      <i class="fas fa-map"></i>
      <b>{{ currentGame }}</b>
      <a class="change-game" @click="openChangePopup" v-if="canEdit">(changer)</a>
    </div>
    <game-sharing-link></game-sharing-link>
    <footer-options></footer-options>
  </div>
</template>
<script>
  import {CookieHandler, BooleanCookieHandler, BooleanSettingHandler} from "../../common/cookie.js";
  import gameSharingLink from "./gameSharingLink.vue";
  import FooterOptions from "./footerOptions.vue";
  import constants from "../../common/constants.js";
  export default {
    components: {
      FooterOptions,
      "game-sharing-link": gameSharingLink,
    },
    data () {
      return {
        autozoomHandler: new BooleanSettingHandler("autozoom", this.$store),
        url: ""
      }
    },

    computed: {
      currentGame() {
        return this.$store.state.game.displayName;
      },
      currentRun() {
        return this.$store.state.game.currentRun;
      },
      totalRuns() {
        return this.$store.state.game.nRuns;
      },
      canEdit() {
        return this.$store.state.game.status === constants.status.FINISHED
      }
    },

    created() {
      this.url = window.location.href
          .replace("https://", "")
          .replace("www.", "")
          .replace(window.location.hash, "");
    },

    methods: {
      toggleAutozoom() {
        let value = this.autozoomHandler.read();
        this.autozoomHandler.write(!value);
      },

      openChangePopup() {
        if (this.canEdit){
            this.$store.commit("showGameCreator");
            this.$store.commit("displayResultPopup");
        }
      }
    }
  }

</script>

<style scoped>
.current-game {
  margin-right: 10px;
}

.change-game {
  margin-left: 5px;
  color: white !important;
  text-decoration: underline;
  font-size: 0.9em;
  cursor:pointer;
}

.current-game .fas {
  margin-right: 8px;
}
  .footer {
    position: fixed;
    bottom: 0;
    left: 0;
    background: blue;
    color: white;
    z-index: 1000;
    padding: 2px 10px;
    font-size: 0.9em;
    display: flex;
  flex-flow: row nowrap;
  justify-content: flex-start;
  align-items: center;
  }

  .footer .sharing-link {
    color: white;
    margin-right: 15px;
    font-size: 1.1em;
    font-weight: bold;
  }


</style>