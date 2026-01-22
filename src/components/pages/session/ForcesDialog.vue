<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="500" content-class="forces-dialog">
    <v-card class="forces-dialog-card">
      <v-card-title class="headline">Import Ground Reaction Forces</v-card-title>
      <v-card-text>
        <div class="text-body-1 mb-4">
          Select a .mot forces file to visualize ground reaction forces at the subject's feet.
          Forces will be automatically positioned at the foot segments of the selected animation.
          <br><br>
          <strong>Supported formats:</strong>
          <ul class="mt-2">
            <li>• Standard OpenSim format: <code>R_ground_force_vx</code>, <code>L_ground_force_vx</code></li>
            <li>• Alternative format: <code>ground_force_right_vx</code>, <code>ground_force_left_vx</code></li>
            <li>• Files with "force" in the filename are automatically detected</li>
          </ul>
        </div>

        <v-alert v-if="animations.length === 0 && smplSequences.length === 0" type="warning" text dense class="mb-4">
          Please load an animation first before importing forces.
        </v-alert>

        <v-alert v-if="forcesDatasets[selectedAnimationForForces]" type="warning" text dense class="mb-4">
          This animation already has forces loaded. Loading new forces will replace the existing ones.
        </v-alert>

        <v-alert v-if="Object.keys(forcesDatasets).length > 0" type="info" text dense class="mb-4">
          Currently loaded forces for: {{ loadedForcesText }}
        </v-alert>

        <div v-if="animations.length > 0" class="mb-4">
          <v-select
            :value="selectedAnimationForForces"
            @input="$emit('update:selectedAnimationForForces', $event)"
            :items="animationOptions"
            item-text="text"
            item-value="value"
            label="Associate with Animation"
            outlined
            dense
          ></v-select>
        </div>

        <v-file-input
          :value="forcesFile"
          @input="$emit('update:forcesFile', $event)"
          label="Forces File (.mot)"
          accept=".mot"
          prepend-icon="mdi-vector-line"
          outlined
          show-size
          clearable
          :disabled="animations.length === 0"
          @change="$emit('handle-forces-file-select', $event)"
        ></v-file-input>

        <div v-if="forcesFile" class="mt-4">
          <div class="text-subtitle-2 mb-2">Force Visualization Settings</div>

          <v-row>
            <v-col cols="6">
              <v-text-field
                :value="forceScale"
                @input="$emit('update:forceScale', parseFloat($event) || forceScale)"
                label="Force Scale"
                type="number"
                step="0.001"
                min="0.001"
                max="0.01"
                dense
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <div class="text-subtitle-2 mb-2">Arrow Color</div>
              <v-menu offset-y :close-on-content-click="false">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: forceColor }" block outlined>
                    <v-icon left>mdi-palette</v-icon>
                    Color
                  </v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex align-center">
                    <v-color-picker
                      :value="forceDisplayColor"
                      :modes="['hex', 'rgba']"
                      show-swatches
                      :swatches="Array.isArray(availableColors) ? availableColors : []"
                      @input="(color) => $emit('update-force-color', { color, index: selectedAnimationForForces || 0 })"
                      class="flex-grow-1"
                    ></v-color-picker>
                    <v-btn icon small @click="$emit('open-eyedropper', { target: 'force', index: selectedAnimationForForces || 0 })" title="Pick color from screen" class="ml-2">
                      <v-icon>mdi-eyedropper-variant</v-icon>
                    </v-btn>
                  </div>
                </v-card>
              </v-menu>
            </v-col>
          </v-row>

          <v-switch
            :input-value="showForces"
            @change="$emit('update:showForces', $event)"
            label="Show Forces"
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
          @click="$emit('load-forces')"
          :disabled="!forcesFile || loadingForces"
          :loading="loadingForces"
        >
          Load Forces
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'ForcesDialog',
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
    forcesDatasets: {
      type: Object,
      default: () => ({})
    },
    selectedAnimationForForces: {
      type: Number,
      default: 0
    },
    animationOptions: {
      type: Array,
      default: () => []
    },
    forcesFile: {
      type: Object,
      default: null
    },
    forceScale: {
      type: Number,
      default: 0.001
    },
    showForces: {
      type: Boolean,
      default: true
    },
    loadingForces: {
      type: Boolean,
      default: false
    },
    availableColors: {
      type: Array,
      default: () => []
    },
    forceColor: {
      type: String,
      default: '#ff0000'
    },
    forceDisplayColor: {
      type: String,
      default: '#ff0000'
    }
  },
  computed: {
    loadedForcesText() {
      return Object.keys(this.forcesDatasets)
        .map(idx => this.animations[idx]?.trialName || `Subject ${parseInt(idx) + 1}`)
        .join(', ');
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .forces-dialog {
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

  code {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    color: #4FC3F7;
  }

  ul {
    list-style: none;
    padding-left: 0;
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
