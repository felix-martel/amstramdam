<template>
<table id="final-results">
  <result-record v-for="(record, index) in leaderboard"
                 :index="index"
                 :key="record.player"
                 :record="record">
  </result-record>
</table>
</template>

<script>
import resultRecord from "./resultRecord.vue";

export default {
  components: {
    "result-record": resultRecord,
  },
  props: {
    leaderboard: Array,
  },
  mounted() {
    console.log(this.leaderboard)
  }
}
</script>

<style scoped>

</style>