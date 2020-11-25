<template>
  <div class="chat-message" v-if="isMessage">
    <span class="chat-author">{{ author }}</span><br/>
    <div class="chat-message-content">
      <div class="chat-message-content" v-for="msg in message.messages">{{ msg }}</div>
    </div>
  </div>
  <div class="chat-notification" v-else-if="isNotif">
    <span class="notif">{{ notification }}</span>
  </div>
</template>

<script>
import constants from "../common/constants";

export default {
name: "chatMessage",
  props: {
    message: Object,
  },
  computed: {
    author() {
      return this.getPlayerName(this.message.author);
    },

    notification() {
      if (!this.isNotif) { return ""}
      const content = this.message.content;
      switch (content.type) {
        case constants.chatItemTypes.NOTIF_LAUNCH:
          return `${this.getPlayerName(content.from)} a lancé la partie`;
        case constants.chatItemTypes.NOTIF_RELAUNCH:
          return `${this.getPlayerName(content.from)} a relancé la partie`;
        case constants.chatItemTypes.NOTIF_WINNER:
          return `${this.getPlayerName(content.player)} a remporté la partie !`;
        case constants.chatItemTypes.NOTIF_NEW_SCORE:
          return `${this.getPlayerName(content.player)} a marqué ${content.score} point` + (content.score > 1 ? "s" : "");
        case constants.chatItemTypes.NOTIF_NEW_HINT:
          return `À trouver : ${content.hint}`;
      }
    },

    isMessage () {
      return this.message.type === constants.chatItemTypes.MESSAGE;
    },

    isNotif () {
      return this.message.type === constants.chatItemTypes.NOTIFICATION;
    }
  }
}
</script>

<style scoped>
.chat-message {
    text-align: left;
    padding: 5px 10px;
}

.chat-notification {
  text-align: left;
  padding: 1px 10px;
}

.chat-author {
  font-size: 0.8em;
  color: gray;
      margin-right: 15px;
    font-style: italic;
}

.notif {
  font-size: 0.8em;
  font-style: italic;
  color: gray;
}
</style>