<template>
  <div class="chat-message">
    <span class="chat-author">{{ author }}</span><br/>
    <span class="chat-message-content">{{ content }}</span>
  </div>
</template>

<script>
export default {
name: "chatMessage",
  props: {
    authorId: String,
    content: String
  },
  computed: {
    author() {
      return this.getPlayerName(this.authorId);
    }
  }
}
</script>

<style scoped>
.chat-author {
  font-size: 0.8em;
  color: gray;
}
</style>