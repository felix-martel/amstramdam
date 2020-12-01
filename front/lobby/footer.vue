<template>
<footer id="game-sharing-link" style="z-index: 1002;">
        <a href="https://github.com/felix-martel/amstramdam"  target="_blank">À propos</a>
        <a href="https://github.com/felix-martel/amstramdam/issues" target="_blank">Signaler un bug</a>
        <span style="color: white;">Demandez l'original : </span>
        <a href="https://www.jeux-geographiques.com/"  target="_blank">Jeux-Géographiques.com</a>
    </footer>
</template>

<script>
export default {
name: "footer.vue"
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

footer a, footer a:visited, footer a:hover {
  color: white;
  margin-right: 10px;
}
</style>