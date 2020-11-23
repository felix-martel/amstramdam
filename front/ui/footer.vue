<template>
  <div class="footer" id="game-sharing-link">
    <span class="sharing">
      Inviter des amis: <u class="sharing-link">{{ url }}</u>
    </span>
    <span class="option-bar">
        <input type="checkbox" name="autozoom" v-model="autozoomHandler.state" id="autozoom-check">
        <label for="autozoom-check">Autozoom</label>
    </span>
  </div>
</template>
<script>
  import {CookieHandler, BooleanCookieHandler, BooleanSettingHandler} from "../common/cookie";

  export default {
    data () {
      return {
        autozoomHandler: new BooleanSettingHandler("autozoom", this.$store),
        url: ""
      }
    },

    computed: {
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
      }
    }
  }

</script>

<style scoped>
  .footer {
    position: fixed;
    bottom: 0;
    left: 0;
    background: blue;
    color: white;
    z-index: 1000;
    padding: 2px 10px;
    font-size: 0.9em;
  }

  .footer .sharing-link {
    color: white;
    margin-right: 15px;
    font-size: 1.1em;
    font-weight: bold;
  }


</style>