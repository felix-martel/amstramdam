<template>
  <div class="game-item">
    <a :href="url">{{ game.name }}</a>
    <span class="game-infos">
      <span class="game-info">
        <i class="fas fa-map"></i>
        <span>
          {{ game.map }}
        </span>
      </span>

      <span class="game-info">
        <i class="fas fa-users"></i>
        <span>
          {{ game.players }}
        </span>
      </span>
    </span>
  </div>
</template>

<script>
export default {
  props: {
    game: Object,
  },
  computed: {
    url() {
      return `/game/${this.game.name}`;
    },
  }
}
</script>

<style scoped>
.game-item {
  margin: 2px 0;
}

.game-info {
  margin-left: 10px;
}

.game-info .fas {
  color: #c4c4c4;
  margin-right: 5px;
}
</style>

<style>
</style>