<template>
  <div class="scene-section mb-4 pa-3" style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
    <div class="section-title mb-3 d-flex align-center" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); cursor: pointer;" @click="showSceneSettingsDetails = !showSceneSettingsDetails">
      <span>Scene Settings</span>
      <v-spacer></v-spacer>
      <v-icon small>{{ showSceneSettingsDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
    </div>

    <!-- Scene settings row -->
    <v-expand-transition>
      <div v-show="showSceneSettingsDetails" class="scene-settings">
      <!-- Background setting -->
      <div class="d-flex align-center mb-3">
        <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Background:</div>
        <v-menu offset-y :close-on-content-click="false">
          <template v-slot:activator="{ on, attrs }">
            <v-btn small v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: backgroundColor }"></v-btn>
          </template>
          <v-card class="color-picker pa-2">
            <div class="d-flex align-center">
              <v-color-picker
                :value="backgroundColor"
                :modes="['hex', 'rgba']"
                show-swatches
                :swatches="Array.isArray(backgroundColors) ? backgroundColors : []"
                @input="onBackgroundColorInput"
                class="flex-grow-1"
              ></v-color-picker>
              <v-btn icon small @click="$emit('open-eyedropper', 'backgroundColor')" title="Pick color from screen" class="ml-2">
                <v-icon>mdi-eyedropper-variant</v-icon>
              </v-btn>
            </div>
          </v-card>
        </v-menu>
      </div>

      <!-- Ground setting -->
      <div class="d-flex align-center mb-3">
        <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Ground:</div>
        <v-menu offset-y :close-on-content-click="false">
          <template v-slot:activator="{ on, attrs }">
            <v-btn small v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: showGround ? groundColor : 'transparent', border: !showGround ? '1px dashed rgba(255,255,255,0.5)' : '1px solid rgba(255,255,255,0.3)' }"></v-btn>
          </template>
          <v-card class="color-picker pa-2">
            <div class="d-flex align-center">
              <v-color-picker
                :value="groundColor"
                :modes="['hex', 'rgba']"
                show-swatches
                :swatches="Array.isArray(groundColors) ? groundColors : []"
                @input="onGroundColorInput"
                :disabled="!showGround"
                class="flex-grow-1"
              ></v-color-picker>
              <v-btn icon small @click="$emit('open-eyedropper', 'groundColor')" title="Pick color from screen" class="ml-2" :disabled="!showGround">
                <v-icon>mdi-eyedropper-variant</v-icon>
              </v-btn>
            </div>
            <v-divider class="my-2"></v-divider>
            <div class="ground-controls pa-2">
              <v-btn small text block @click="$emit('toggle-ground-visibility')" class="mb-2">
                <v-icon left small>{{ showGround ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                {{ showGround ? 'Hide Ground' : 'Show Ground' }}
              </v-btn>
              <v-btn small text block @click="$emit('toggle-ground-texture')" :disabled="!showGround" class="mb-2">
                <v-icon left small>{{ useGroundTexture ? 'mdi-texture-box' : 'mdi-checkbox-blank-outline' }}</v-icon>
                {{ useGroundTexture ? 'Remove Texture' : 'Use Texture' }}
              </v-btn>
              <v-btn small text block @click="$emit('toggle-checkerboard')" :disabled="!showGround || !useGroundTexture">
                <v-icon left small>{{ useCheckerboard ? 'mdi-grid' : 'mdi-view-grid' }}</v-icon>
                {{ useCheckerboard ? 'Use Grid' : 'Use Checkerboard' }}
              </v-btn>
              <div class="mt-3">
                <div class="text-caption mb-2">
                  Transparency: {{ Math.round((1 - groundOpacity) * 100) }}%
                </div>
                <v-slider
                  :value="(1 - groundOpacity) * 100"
                  @input="value => $emit('update-ground-opacity', 1 - value / 100)"
                  :min="0"
                  :max="100"
                  step="1"
                  hide-details
                  :disabled="!showGround"
                  dense
                  class="mt-0"
                ></v-slider>
              </div>
              <div class="mt-3">
                <div class="text-caption mb-2">
                  Height Position: {{ groundPositionY.toFixed(2) }}m
                </div>
                <v-slider
                  :value="groundPositionY"
                  @input="onGroundPositionInput"
                  :min="-5"
                  :max="5"
                  step="0.01"
                  hide-details
                  :disabled="!showGround"
                  dense
                  class="mt-0"
                ></v-slider>
              </div>
            </div>
          </v-card>
        </v-menu>
      </div>

      <!-- Axes setting -->
      <div class="d-flex align-center mb-3">
        <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Axes:</div>
        <v-btn icon small @click="$emit('toggle-axes')" title="Toggle Axes Visibility">
          <v-icon small :color="showAxes ? 'white' : 'grey'">{{ showAxes ? 'mdi-axis-arrow' : 'mdi-axis-arrow-lock' }}</v-icon>
        </v-btn>
      </div>

      <!-- Camera setting -->
      <div class="d-flex align-center mb-3">
        <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Camera:</div>
        <v-btn icon small @click="$emit('toggle-camera-controls')" title="Toggle Camera Controls Visibility">
          <v-icon small :color="showCameraControls ? 'white' : 'grey'">{{ 'mdi-cube-scan' }}</v-icon>
        </v-btn>
      </div>

      <!-- Lights setting -->
      <div class="d-flex align-center">
        <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Lights:</div>
        <v-btn icon small @click="$emit('toggle-lights')" title="Toggle Lighting (disable for uniform color)">
          <v-icon small :color="enableLights ? 'white' : 'grey'">{{ enableLights ? 'mdi-lightbulb-on' : 'mdi-lightbulb-off' }}</v-icon>
        </v-btn>
      </div>
      </div>
    </v-expand-transition>
  </div>
</template>

<script>
export default {
  name: 'SceneControls',
  props: {
    backgroundColor: {
      type: String,
      default: '#1a1a2e'
    },
    backgroundColors: {
      type: Array,
      default: () => []
    },
    groundColor: {
      type: String,
      default: '#808080'
    },
    groundColors: {
      type: Array,
      default: () => []
    },
    showGround: {
      type: Boolean,
      default: true
    },
    groundOpacity: {
      type: Number,
      default: 1
    },
    groundPositionY: {
      type: Number,
      default: 0
    },
    useGroundTexture: {
      type: Boolean,
      default: false
    },
    useCheckerboard: {
      type: Boolean,
      default: false
    },
    showAxes: {
      type: Boolean,
      default: true
    },
    showCameraControls: {
      type: Boolean,
      default: true
    },
    enableLights: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      showSceneSettingsDetails: false
    }
  },
  methods: {
    onBackgroundColorInput(value) {
      this.$emit('update:backgroundColor', value)
    },
    onGroundColorInput(value) {
      this.$emit('update:groundColor', value)
    },
    onGroundPositionInput(value) {
      this.$emit('update:groundPositionY', value)
      this.$emit('update-ground-position', value)
    }
  }
}
</script>

<style scoped>
.scene-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.color-preview {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.color-picker {
  max-width: 320px;
}

.ground-controls {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}
</style>
