<template>
  <div class="capture-controls">
    <!-- Image Capture Section -->
    <div class="capture-section pa-3">
      <div class="section-title mb-3">Image Capture</div>
      <!-- Capture button row with settings button -->
      <div class="d-flex align-center mb-3">
        <v-btn
          color="#6B7280"
          dark
          @click="$emit('capture-screenshot')"
          class="custom-btn"
          style="flex: 1;"
        >
          <v-icon left>mdi-camera</v-icon>
          Capture Image
        </v-btn>

        <v-btn
          small
          outlined
          color="white"
          class="ml-2 settings-text-btn"
          @click="openCaptureSettings($event)"
        >
          Settings
        </v-btn>
      </div>

      <!-- Capture settings summary -->
      <div class="d-flex align-center capture-summary">
        <div class="text-caption text-center" style="flex: 1;">
          <span class="font-weight-bold">Background:</span>
          {{ captureMode === 'both' ? 'Both Types' :
             captureMode === 'normal' ? 'Normal' : 'Transparent' }}
        </div>
      </div>

      <!-- Image capture settings dialog -->
      <v-dialog
        v-model="showCaptureSettings"
        max-width="500"
      >
        <v-card class="capture-settings-dialog">
          <v-card-title>Image Capture Settings</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-select
                  :value="captureMode"
                  @input="$emit('update:captureMode', $event)"
                  :items="[
                    {text: 'Both Types', value: 'both'},
                    {text: 'Normal', value: 'normal'},
                    {text: 'Transparent', value: 'transparent'}
                  ]"
                  label="Background Type"
                  outlined
                  dense
                  dark
                  hide-details="auto"
                  class="mb-4"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <div class="info-box pa-3 mt-2">
                  <div class="d-flex align-center mb-2">
                    <v-icon small color="info" class="mr-2">mdi-information-outline</v-icon>
                    <span class="subtitle-2">Capture Tips</span>
                  </div>
                  <ul class="pl-4 mb-0 text-caption">
                    <li class="mb-1"><b>Both Types:</b> Saves both normal and transparent versions</li>
                    <li class="mb-1"><b>Normal:</b> Standard PNG with background</li>
                    <li><b>Transparent:</b> PNG with transparent background (useful for overlays)</li>
                  </ul>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" text @click="showCaptureSettings = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CaptureControls',

  props: {
    captureMode: {
      type: String,
      default: 'both',
      validator: value => ['both', 'normal', 'transparent'].includes(value)
    }
  },

  data() {
    return {
      showCaptureSettings: false
    };
  },

  methods: {
    openCaptureSettings(event) {
      event.stopPropagation();
      this.showCaptureSettings = true;
    }
  }
};
</script>

<style scoped>
.capture-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.settings-text-btn {
  text-transform: none;
  letter-spacing: normal;
}

.capture-summary {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 8px;
}

.capture-settings-dialog {
  background: #1e1e1e;
}

.info-box {
  background: rgba(33, 150, 243, 0.1);
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-radius: 8px;
}

.info-box ul {
  list-style-type: disc;
}

.custom-btn {
  text-transform: none;
  letter-spacing: normal;
}
</style>
