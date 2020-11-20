<template>
  <div class="inner-chat">
    <div class="messages-wrapper">
      <div id="chat-messages" class="chat-messages">

        <chat-message v-for="msg in messages"
                      :author-id="msg.author"
                      :content="msg.message"></chat-message>
      </div>

    </div>
    <div class="input">
        <textarea name="chat-input"
                  id="chat-input"
                  class="chat-input"
                  @keyup.enter="sendMessage"
                  placeholder="Envoyez un message" v-model="message"></textarea>
    </div>
  </div>
</template>


<script>
import chatMessage from "./chatMessage.vue";

export default {
  components: {
    "chat-message": chatMessage
  },
  data () {
    return {
      message: "",
    }
  },
  computed: {
    messages () {
      return this.$store.state.chat.messages
    }
  },
  mounted () {
    this.$socketOn("chat:new", this.processNewMessage);
  },
  methods: {
    processNewMessage (data) {
      if (data.author !== this.$store.state.playerId){
        this.$store.commit("addMessage", data);
      }
    },

    sendMessage() {
      const payload = {
        message: this.message,
        author: this.$store.state.playerId
      };
      this.$store.commit("addMessage", payload);
      this.$socketEmit("chat:send", this.message);
      this.message = "";
    }
  }
}
</script>

<style scoped>
textarea {
  font-size: 0.9em;
}
</style>