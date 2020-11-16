<template>
  <div id="game-sharing-link">Inviter des amis: <u id="sharing-link">{{ url }}</u>
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
      this.url = window.location.href.replace("https://", "").replace("www.", "");
    },

    methods: {
      toggleAutozoom() {
        let value = this.autozoomHandler.read();
        this.autozoomHandler.write(!value);
      }
    }
  }

</script>