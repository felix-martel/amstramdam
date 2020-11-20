<template>
  <div class="popup-container" id="popup-container" :hidden="visible">
    <div id="mask">

    </div>
    <div id="popup" class="box">
      <slot>
      </slot>
    </div>
  </div>
</template>

<script>
export default {
name: "popup",
  props: {
    visible: Boolean,
  }
}
</script>

<style scoped>

</style>