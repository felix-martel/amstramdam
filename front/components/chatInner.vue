<template>
  <div class="inner-chat">
    <div class="messages-wrapper">
        <div id="chat-messages" class="chat-messages">

        <chat-message v-for="msg in messages"
                      :message="msg"
                      :author-id="msg.author"
                      :messages="msg.messages"></chat-message>
      </div>


    </div>
    <div class="input">
        <textarea name="chat-input"
                  id="chat-input"
                  ref="chatInput"
                  class="chat-input"
                  @keyup.enter="sendMessage"
                  @keyup.esc="$emit('close')"
                  placeholder="Envoyez un message" v-model="message"></textarea>
    </div>
  </div>
</template>


<script>
import chatMessage from "./chatMessage.vue";
import scrollable from "./scrollable.vue";
export default {
  components: {
    "chat-message": chatMessage,
    "scrollable": scrollable,
  },
  emit: ["close"],
  data () {
    return {
      message: "",
      currentScroll: 0,
    }
  },
  computed: {
    messages () {
      return this.$store.state.chat.messages
    }
  },
  mounted () {
    //this.$socketOn("chat:new", this.processNewMessage);
    this.$refs.chatInput.focus();
  },
  methods: {
    processNewMessage (data) {
      // if (data.author !== this.$store.state.playerId){
      //   this.$store.commit("addMessage", data);
      // }
    },

    sendMessage() {
      const payload = {
        message: this.message,
        author: this.$store.state.playerId
      };
      this.$store.commit("addMessage", payload);
      this.$socketEmit("chat:send", this.message);
      this.message = "";
    },

    scroll () {

    }
  }
}
</script>

<style scoped>
textarea {
  font-size: 0.9em;
}

.inner-chat {
    position: absolute;
    bottom: 0;
    right: 0;
    left: 0;
  top: 0;
  overflow:hidden;
}

.chat-messages {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0px;
  box-sizing: border-box;
}

.inner-chat .input {
  position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
  height: 50px;
}


.chat-input {
    resize: none;
    border: none;
    border-top: 1px solid lightgray;
    width: 100%;
    height:100%;
    box-sizing: border-box;
    padding: 5px;
}
.chat-input:focus {
  outline: none;
}
.chat-input:hover {
  /*border-color: gray;*/
}

.messages-wrapper {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 50px;
  box-sizing: border-box;
  overflow: auto;
}
</style>