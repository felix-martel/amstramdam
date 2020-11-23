<template>
  <div class="chat-message">
    <span class="chat-author">{{ author }}</span><br/>
    <div class="chat-message-content">
      <div class="chat-message-content" v-for="msg in messages">{{ msg }}</div>
    </div>
  </div>
</template>

<script>
export default {
name: "chatMessage",
  props: {
    authorId: String,
    messages: String
  },
  computed: {
    author() {
      return this.getPlayerName(this.authorId);
    }
  }
}
</script>

<style scoped>
.chat-message {
    text-align: left;
    padding: 5px 10px;
}

.chat-author {
  font-size: 0.8em;
  color: gray;
      margin-right: 15px;
    font-style: italic;
}
</style>