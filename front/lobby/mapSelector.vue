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
      const mid = e.target.value;
      this.$emit("update:modelValue", this.valueMapper[mid] || mid);
    }
  },

  created() {
    this.$emit("update:modelValue", this.defaultMap);
  },

  computed: {
    defaultMap () {
      return this.datasets[0].maps[0]
    },

    valueMapper() {
      const o = {};
      this.datasets.forEach(group => {
        group.maps.forEach(dataset => {
          o[dataset.map_id] = dataset;
        })
      })
      return o;
    }
  },
}
</script>

<style scoped>

</style>