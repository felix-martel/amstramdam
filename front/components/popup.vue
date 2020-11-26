<template>
  <div class="popup-container" id="popup-container" :hidden="!visible">
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
#mask {
  background-color: black;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  opacity: 0.8;
  z-index: 1001;
}


#popup {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 800px;
  transform: translate(-50%, -50%);
  z-index: 1002;
  overflow: hidden;
  /*min-height: 400px;*/
}

@media screen and (max-width: 800px) {
  #popup {
    width: 100%;
  }
}
</style>