<template>
  <div class="speed-control">
    <v-menu offset-y :close-on-content-click="true">
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          small
          text
          v-bind="attrs"
          v-on="on"
          class="speed-button"
        >
          <v-icon small left>mdi-speedometer</v-icon>
          {{ getCurrentSpeedLabel() }}
        </v-btn>
      </template>
      <v-list dense class="speed-list">
        <v-list-item
          v-for="(s, index) in speeds"
          :key="index"
          @click="$emit('input', s.value)"
          :class="{ 'v-list-item--active': s.value === value }"
        >
          <v-list-item-title>{{ s.name }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>  
</template>

<script>
export default {
  name: 'SpeedControl',
  props: {
    value: {
      type: Number,
      default: 1
    }
  },
  data () {
    return {
      speeds: [
        { name: '0.1x', value: 0.1 },
        { name: '0.25x', value: 0.25 },
        { name: '0.5x', value: 0.5 },
        { name: '0.75x', value: 0.75 },
        { name: '1x', value: 1 },
        { name: '1.25x', value: 1.25 },
        { name: '1.5x', value: 1.5 },
        { name: '1.75x', value: 1.75 },
        { name: '2x', value: 2 }
      ]
    }
  },
  methods: {
    getCurrentSpeedLabel() {
      const speed = this.speeds.find(s => s.value === this.value)
      return speed ? speed.name : '1x'
    }
  }
}
</script>

<style lang="scss">
.speed-control {
  display: inline-block;
  
  .speed-button {
    min-width: 80px;
    
    &.v-btn--active {
      background-color: rgba(255, 255, 255, 0.1);
    }
  }
  
  .speed-list {
    background-color: #1E1E1E;
    
    .v-list-item--active {
      background-color: rgba(255, 255, 255, 0.1);
    }
  }
}
</style>
