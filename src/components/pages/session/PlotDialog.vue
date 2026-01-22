<template>
  <v-dialog
    :value="value"
    @input="$emit('input', $event)"
    max-width="1200"
    persistent
    content-class="plotting-dialog"
    :overlay="false"
  >
    <v-card
      class="plotting-dialog-card"
      :style="{
        position: 'fixed',
        top: plottingDialogPosition.y + 'px',
        left: plottingDialogPosition.x + 'px',
        width: plottingDialogSize.width + 'px',
        height: plottingDialogSize.height + 'px',
        maxWidth: 'none',
        maxHeight: 'none',
        zIndex: 1000,
        resize: 'both',
        overflow: 'hidden'
      }"
    >
      <!-- Header with drag handle -->
      <v-card-title
        class="plotting-header d-flex align-center pa-3"
        style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); cursor: move; user-select: none;"
        @mousedown="$emit('start-drag', $event)"
        @touchstart="$emit('start-drag', $event)"
      >
        <v-icon color="white" class="mr-3">mdi-chart-line</v-icon>
        <span class="white--text font-weight-bold text-h6">Real-time Data Plots</span>
        <v-spacer></v-spacer>

        <!-- Plot Controls -->
        <v-btn icon small @click="$emit('toggle-plot-updates')" class="mr-2">
          <v-icon color="white">{{ plotUpdatesEnabled ? 'mdi-pause' : 'mdi-play' }}</v-icon>
        </v-btn>

        <v-btn icon small @click="$emit('export-plot')" class="mr-2">
          <v-icon color="white">mdi-download</v-icon>
        </v-btn>

        <v-btn icon small @click="$emit('input', false)">
          <v-icon color="white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- Plot Content -->
      <v-card-text class="pa-0" style="height: calc(100% - 64px); overflow: hidden;">
        <div class="d-flex" style="height: 100%;">
          <!-- Left Panel - Plot Controls -->
          <div class="plot-controls-panel pa-3" style="width: 280px; background: rgba(0, 0, 0, 0.05); border-right: 1px solid rgba(0, 0, 0, 0.1); overflow-y: auto;">
            <div class="text-subtitle-2 mb-3 font-weight-bold">Plot Configuration</div>

            <!-- Plot Type Selection -->
            <div class="mb-4">
              <div class="text-caption font-weight-bold mb-2">Plot Type:</div>
              <v-select
                :value="selectedPlotType"
                @input="$emit('update:selectedPlotType', $event)"
                :items="plotTypes"
                item-text="label"
                item-value="value"
                outlined
                dense
              ></v-select>
            </div>

            <!-- Variable Selection -->
            <div class="mb-4" v-if="availableVariables.length > 0">
              <div class="text-caption font-weight-bold mb-2">Variables:</div>
              <v-select
                :value="selectedVariables"
                @input="$emit('update:selectedVariables', $event)"
                :items="availableVariables"
                item-text="label"
                item-value="value"
                outlined
                dense
                multiple
                chips
                small-chips
              ></v-select>
            </div>

            <!-- Marker Selection for marker-related plots -->
            <div class="mb-4" v-if="selectedPlotType === 'marker_position' || selectedPlotType === 'marker_distance'">
              <div class="text-caption font-weight-bold mb-2">Markers:</div>
              <v-select
                :value="selectedMarkers"
                @input="$emit('update:selectedMarkers', $event)"
                :items="availableMarkers"
                item-text="label"
                item-value="value"
                outlined
                dense
                multiple
                chips
                small-chips
              ></v-select>
            </div>

            <!-- Animation Selection -->
            <div class="mb-4" v-if="animations.length > 1">
              <div class="text-caption font-weight-bold mb-2">Animation:</div>
              <v-select
                :value="selectedPlotAnimation"
                @input="$emit('update:selectedPlotAnimation', $event)"
                :items="animationOptions"
                item-text="text"
                item-value="value"
                outlined
                dense
              ></v-select>
            </div>

            <!-- Plot Appearance -->
            <div class="mb-4">
              <div class="text-caption font-weight-bold mb-2">Appearance:</div>
              <v-checkbox
                :input-value="plotSettings.showGrid"
                @change="updatePlotSetting('showGrid', $event)"
                label="Show Grid"
                dense
                hide-details
                class="mb-1"
              ></v-checkbox>
              <v-checkbox
                :input-value="plotSettings.showLegend"
                @change="updatePlotSetting('showLegend', $event)"
                label="Show Legend"
                dense
                hide-details
                class="mb-1"
              ></v-checkbox>
              <v-checkbox
                :input-value="plotSettings.showCurrentTime"
                @change="updatePlotSetting('showCurrentTime', $event)"
                label="Show Current Time"
                dense
                hide-details
              ></v-checkbox>
            </div>

            <!-- Time Range -->
            <div class="mb-4">
              <div class="text-caption font-weight-bold mb-2">Time Range (s):</div>
              <v-range-slider
                :value="plotTimeRange"
                @input="$emit('update:plotTimeRange', $event)"
                :min="0"
                :max="maxTime"
                :step="0.1"
                dense
                hide-details
                class="mb-2"
              ></v-range-slider>
              <div class="text-caption text-center">
                {{ plotTimeRange[0].toFixed(1) }}s - {{ plotTimeRange[1].toFixed(1) }}s
              </div>
            </div>
          </div>

          <!-- Right Panel - Plot Display -->
          <div class="plot-display-panel" style="flex: 1; position: relative;">
            <div v-if="!selectedPlotType || selectedVariables.length === 0" class="d-flex align-center justify-center" style="height: 100%;">
              <div class="text-center text--disabled">
                <v-icon size="64" color="grey">mdi-chart-line</v-icon>
                <div class="text-h6 mt-2">Select plot type and variables to begin</div>
              </div>
            </div>

            <!-- Chart Container -->
            <div v-else style="width: 100%; height: 100%; position: relative;">
              <canvas ref="plotChart" style="width: 100%; height: 100%;"></canvas>
            </div>
          </div>
        </div>
      </v-card-text>

      <!-- Resize Handle -->
      <div
        class="resize-handle"
        style="position: absolute; bottom: 0; right: 0; width: 20px; height: 20px; cursor: nw-resize; background: linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.3) 50%);"
        @mousedown="$emit('start-resize', $event)"
        @touchstart="$emit('start-resize', $event)"
      ></div>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'PlotDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    },
    plottingDialogPosition: {
      type: Object,
      default: () => ({ x: 100, y: 100 })
    },
    plottingDialogSize: {
      type: Object,
      default: () => ({ width: 900, height: 600 })
    },
    plotUpdatesEnabled: {
      type: Boolean,
      default: true
    },
    selectedPlotType: {
      type: String,
      default: ''
    },
    plotTypes: {
      type: Array,
      default: () => []
    },
    selectedVariables: {
      type: Array,
      default: () => []
    },
    availableVariables: {
      type: Array,
      default: () => []
    },
    selectedMarkers: {
      type: Array,
      default: () => []
    },
    availableMarkers: {
      type: Array,
      default: () => []
    },
    animations: {
      type: Array,
      default: () => []
    },
    animationOptions: {
      type: Array,
      default: () => []
    },
    selectedPlotAnimation: {
      type: Number,
      default: 0
    },
    plotSettings: {
      type: Object,
      default: () => ({ showGrid: true, showLegend: true, showCurrentTime: true })
    },
    plotTimeRange: {
      type: Array,
      default: () => [0, 1]
    },
    maxTime: {
      type: Number,
      default: 1
    }
  },
  methods: {
    updatePlotSetting(key, value) {
      const newSettings = { ...this.plotSettings, [key]: value };
      this.$emit('update:plotSettings', newSettings);
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .plotting-dialog {
  overflow: visible !important;

  .v-card {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    overflow: hidden;
  }

  .v-card-title {
    color: #FFFFFF !important;
  }

  .v-card-text {
    color: #FFFFFF !important;
    background-color: #1E1E1E !important;
  }
}

.plotting-dialog-card {
  background-color: #1E1E1E !important;
  color: #FFFFFF !important;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.plotting-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.plot-controls-panel {
  background: rgba(0, 0, 0, 0.3) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.1) !important;

  .text-subtitle-2,
  .text-caption {
    color: #FFFFFF !important;
  }

  ::v-deep .v-input {
    .v-label {
      color: rgba(255, 255, 255, 0.7) !important;
    }

    .v-select__selection {
      color: #FFFFFF !important;
    }

    input {
      color: #FFFFFF !important;
    }
  }

  ::v-deep .v-checkbox {
    .v-label {
      color: rgba(255, 255, 255, 0.9) !important;
    }
  }
}

.plot-display-panel {
  background: #2A2A2A;
}

.resize-handle {
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
}
</style>
