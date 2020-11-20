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