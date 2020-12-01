<template>
  <input type="checkbox" name="autozoom" checked id="autozoom-check">
  <label for="autozoom">Autozoom</label>
</template>
<script>
import {BooleanCookieHandler} from "../common/cookie";

export default {
  props: ["name", "label", "defaultValue"],

  data () {
    return {
      handler: new BooleanCookieHandler("amstramdam-" + this.name, this.defaultValue),
    }
  },

  created () {

  }
}
</script>