<template>
<footer id="game-sharing-link" style="z-index: 1002;">
  <span >Amstramdam {{ version }}</span>
  <a href="https://github.com/felix-martel/amstramdam"  target="_blank">À propos</a>
  <a href="https://github.com/felix-martel/amstramdam/issues" target="_blank">Signaler un bug</a>
  <span>Demandez l'original : </span>
  <a href="https://www.jeux-geographiques.com/"  target="_blank">Jeux-Géographiques.com</a>
    </footer>
</template>

<script>
export default {
  name: "footer.vue",
  props: {
    version: String,
    isStaging: Boolean,
  }
}
</script>

<style scoped>
footer {
  position: fixed;
  bottom: 0;
  left: 0;
  background: blue;
  color: white;
  z-index: 1000;
  padding: 2px 10px;
  font-size: 0.9em;
  display: flex;
  flex-flow: row nowrap;
  justify-content: flex-start;
  align-items: center;
}

footer a, footer a:visited, footer a:hover, footer span {
  color: white;
  margin-right: 10px;
}
</style>