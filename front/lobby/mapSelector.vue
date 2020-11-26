<template>
  <select name="map" id="map-selector" @change="updateSelected">
    <option
        v-for="dataset in datasets[0].maps"
        :value="dataset.map_id"
        :selected="modelValue === dataset.map_id"
    >
      {{ dataset.name }}
    </option>
    <optgroup
        v-for="datagroup in datasets.slice(1)"
        :label="datagroup.group"
    >
      <option v-for="dataset in datagroup.maps"
              :value="dataset.map_id"
        :selected="modelValue === dataset.map_id"
      >
        {{ dataset.name}}
      </option>
    </optgroup>
  </select>
</template>

<script>
export default {
  props: {
    datasets: Array,
    modelValue: String,
  },
  emits: ["select", "update:modelValue"],
  methods: {
    updateSelected(e) {
      this.$emit("update:modelValue", e.target.value);
    }
  },

  created() {
    this.$emit("update:modelValue", this.defaultMap.map_id);
  },

  computed: {
    defaultMap () {
      return this.datasets[0].maps[0]
    }
  },
}
</script>

<style scoped>

</style>