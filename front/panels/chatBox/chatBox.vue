<template>
  <div class="box" id="chat-box">
    <i id="close-chatbox" class="fas fa-times" @click="hideSelf"></i>
    <inner-chat></inner-chat>
  </div>
</template>
<script>
import chatInner from "../../components/chatInner.vue";

export default {
  components: {
    "inner-chat": chatInner,
  },
  data () {
    return {
    }
  },
  methods: {
    hideSelf () {
      this.$store.commit("hideChatBox");
    }
  }
}
</script>
<style scoped>
#chat-box {
  position: relative;
  min-height: 200px;
  overflow-x: hidden;
  overflow-y: auto;

}

#chat-box.hidden {
  display: none;
}

#close-chatbox {
    position: absolute;
    top: 7px;
    right: 7px;
    color: #a1a1a1;
    cursor:pointer;
  z-index: 1;

}
#close-chatbox:hover {
  color: blue;
}
</style>