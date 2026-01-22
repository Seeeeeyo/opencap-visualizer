<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="500" content-class="markers-dialog">
    <v-card class="markers-dialog-card">
      <v-card-title class="headline">Import Motion Capture Markers</v-card-title>
      <v-card-text>
        <div class="text-body-1 mb-4">
          Select a .trc file to visualize motion capture markers as spheres in the 3D scene.
          Markers will be positioned according to the data in the file.
        </div>

        <v-alert v-if="animations.length === 0 && smplSequences.length === 0" type="info" text dense class="mb-4">
          No animations loaded. A standalone marker visualization will be created.
        </v-alert>

        <v-alert v-if="animations.length > 0 && markersDatasets[selectedAnimationForMarkers]" type="warning" text dense class="mb-4">
          This animation already has markers loaded. Loading new markers will replace the existing ones.
        </v-alert>

        <v-alert v-if="Object.keys(markersDatasets).length > 0 && animations.length > 0" type="info" text dense class="mb-4">
          Currently loaded markers for: {{ loadedMarkersText }}
        </v-alert>

        <div v-if="animations.length > 0" class="mb-4">
          <v-select
            :value="selectedAnimationForMarkers"
            @input="$emit('update:selectedAnimationForMarkers', $event)"
            :items="animationOptions"
            item-text="text"
            item-value="value"
            label="Associate with Animation"
            outlined
            dense
          ></v-select>
        </div>

        <v-file-input
          :value="markersFile"
          @input="$emit('update:markersFile', $event)"
          label="Markers File (.trc)"
          accept=".trc"
          prepend-icon="mdi-record-circle-outline"
          outlined
          show-size
          clearable
          @change="$emit('handle-markers-file-select', $event)"
        ></v-file-input>

        <div v-if="markersFile" class="mt-4">
          <div class="text-subtitle-2 mb-2">Marker Visualization Settings</div>

          <v-row>
            <v-col cols="6">
              <v-text-field
                :value="markerSize"
                @input="$emit('update:markerSize', parseFloat($event) || markerSize)"
                label="Marker Size"
                type="number"
                step="1"
                min="1"
                max="20"
                dense
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <div class="text-subtitle-2 mb-2">Marker Color</div>
              <v-menu offset-y :close-on-content-click="false">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: markerColor }" block outlined>
                    <v-icon left>mdi-palette</v-icon>
                    Color
                  </v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex align-center">
                    <v-color-picker
                      :value="markerDisplayColor"
                      :modes="['hex', 'rgba']"
                      show-swatches
                      :swatches="Array.isArray(availableColors) ? availableColors : []"
                      @input="(color) => $emit('update-marker-color', { color, index: selectedAnimationForMarkers || 0 })"
                      class="flex-grow-1"
                    ></v-color-picker>
                    <v-btn icon small @click="$emit('open-eyedropper', { target: 'marker', index: selectedAnimationForMarkers || 0 })" title="Pick color from screen" class="ml-2">
                      <v-icon>mdi-eyedropper-variant</v-icon>
                    </v-btn>
                  </div>
                </v-card>
              </v-menu>
            </v-col>
          </v-row>

          <v-switch
            :input-value="showMarkers"
            @change="$emit('update:showMarkers', $event)"
            label="Show Markers"
            color="success"
          ></v-switch>
        </div>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey darken-1" text @click="$emit('close-dialog')">
          Cancel
        </v-btn>
        <v-btn
          color="success"
          text
          @click="$emit('load-markers')"
          :disabled="!markersFile || loadingMarkers"
          :loading="loadingMarkers"
        >
          Load Markers
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'MarkersDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    },
    animations: {
      type: Array,
      default: () => []
    },
    smplSequences: {
      type: Array,
      default: () => []
    },
    markersDatasets: {
      type: Object,
      default: () => ({})
    },
    selectedAnimationForMarkers: {
      type: Number,
      default: 0
    },
    animationOptions: {
      type: Array,
      default: () => []
    },
    markersFile: {
      type: Object,
      default: null
    },
    markerSize: {
      type: Number,
      default: 5
    },
    showMarkers: {
      type: Boolean,
      default: true
    },
    loadingMarkers: {
      type: Boolean,
      default: false
    },
    availableColors: {
      type: Array,
      default: () => []
    },
    markerColor: {
      type: String,
      default: '#00ff00'
    },
    markerDisplayColor: {
      type: String,
      default: '#00ff00'
    }
  },
  computed: {
    loadedMarkersText() {
      return Object.keys(this.markersDatasets)
        .map(idx => this.animations[idx]?.trialName || `Subject ${parseInt(idx) + 1}`)
        .join(', ');
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .markers-dialog {
  .v-card {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    overflow: hidden;
  }

  .v-card-title {
    background-color: #282828 !important;
    color: #FFFFFF !important;
    font-size: 1.6rem;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .v-card-text {
    color: #FFFFFF !important;
    padding: 30px;
    background-color: #1E1E1E !important;
  }

  .v-card-actions {
    background-color: #282828 !important;
    padding: 12px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .v-text-field input {
    color: #FFFFFF !important;
  }

  .v-text-field .v-label {
    color: rgba(255, 255, 255, 0.7) !important;
  }

  .v-select .v-select__selection {
    color: #FFFFFF !important;
  }

  .v-file-input .v-file-input__text {
    color: #FFFFFF !important;
  }

  .v-alert {
    &.warning {
      background-color: rgba(255, 193, 7, 0.1) !important;
      border: 1px solid rgba(255, 193, 7, 0.3) !important;
    }
    &.info {
      background-color: rgba(33, 150, 243, 0.1) !important;
      border: 1px solid rgba(33, 150, 243, 0.3) !important;
    }
  }
}

.color-preview {
  min-height: 40px !important;
  border-radius: 4px !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.color-picker {
  background: #1E1E1E !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.color-picker .v-btn {
  margin: 2px;
  padding: 0;
  min-width: 32px !important;
  width: 32px !important;
  height: 32px !important;
}
</style>
