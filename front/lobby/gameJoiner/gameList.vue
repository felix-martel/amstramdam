<template>
<div class="game-list">
  <game-list-item v-for="game in games" :game="game"></game-list-item>
</div>
</template>

<script>
import GameListItem from "./gameListItem.vue";

export default {
  components: {GameListItem},
  props: {
    games: Array,
  }
}
</script>

<style scoped>
.game-list {
  max-height: 200px;
  overflow-y: auto;

}
</style>