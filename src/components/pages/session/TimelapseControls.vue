<template>
  <div>
    <!-- Timelapse Controls -->
    <div class="timelapse-section mb-4 pa-3" style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
      <div class="section-title mb-3 d-flex align-center" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); cursor: pointer;" @click="showTimelapseDetails = !showTimelapseDetails">
        <span>Timelapse Mode</span>
        <v-spacer></v-spacer>
        <v-icon small>{{ showTimelapseDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
      </div>

      <v-expand-transition>
        <div v-show="showTimelapseDetails">
          <!-- Timelapse toggle with settings button -->
          <div class="d-flex align-center mb-3">
            <v-switch
              :value="timelapseMode"
              @change="onTimelapseModeChange"
              color="indigo"
              class="mr-auto mb-0 mt-0 pt-0"
              hide-details
              style="flex: 1;"
            ></v-switch>

            <v-btn
              small
              outlined
              color="white"
              class="ml-2 settings-text-btn"
              @click="openTimelapseSettings($event)"
              :disabled="!timelapseMode"
            >
              Settings
            </v-btn>
          </div>

          <!-- Timelapse settings summary -->
          <div v-if="timelapseMode" class="d-flex align-center recording-summary">
            <div class="text-caption text-center" style="flex: 1;">
              <span class="font-weight-bold">Interval:</span> {{ timelapseInterval }} frames
            </div>
            <div class="text-caption text-center" style="flex: 1;">
              <span class="font-weight-bold">Opacity:</span> {{ Math.round(timelapseOpacity * 100) }}%
            </div>
          </div>

          <!-- Quick action buttons when timelapse mode is enabled -->
          <div v-if="timelapseMode" class="d-flex justify-space-between align-center mt-2">
            <v-btn small text @click="$emit('clear-timelapse')" class="mt-1">
              Clear All
            </v-btn>
            <v-btn small text @click="showTimelapseManager = true" class="mt-1">
              Manage Models
            </v-btn>
          </div>
        </div>
      </v-expand-transition>
    </div>

    <!-- Timelapse Settings Dialog -->
    <v-dialog
      v-model="showTimelapseSettings"
      max-width="500"
    >
      <v-card class="recording-settings-dialog">
        <v-card-title>Timelapse Settings</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <div class="text-subtitle-2 mb-2">Frame Interval</div>
              <v-slider
                :value="timelapseInterval"
                @input="onIntervalInput"
                min="1"
                max="30"
                step="1"
                thumb-label
                thumb-size="24"
                hide-details
                class="mb-4"
              >
                <template v-slot:thumb-label="{ value }">
                  {{ value }}
                </template>
                <template v-slot:prepend>
                  <div class="text-caption grey--text">1</div>
                </template>
                <template v-slot:append>
                  <div class="text-caption grey--text">30</div>
                </template>
              </v-slider>
            </v-col>

            <v-col cols="12">
              <div class="text-subtitle-2 mb-2">Model Transparency</div>
              <v-slider
                :value="timelapseOpacity * 100"
                @input="onOpacityInput"
                @change="onOpacityChange"
                min="0"
                max="100"
                step="1"
                thumb-label
                thumb-size="24"
                hide-details
                class="mb-4"
              >
                <template v-slot:thumb-label="{ value }">
                  {{ Math.round(value) }}%
                </template>
                <template v-slot:prepend>
                  <div class="text-caption grey--text">0%</div>
                </template>
                <template v-slot:append>
                  <div class="text-caption grey--text">100%</div>
                </template>
              </v-slider>
            </v-col>

            <v-col cols="12">
              <div class="info-box pa-3 mt-2">
                <div class="d-flex align-center mb-2">
                  <v-icon small color="info" class="mr-2">mdi-information-outline</v-icon>
                  <span class="subtitle-2">Timelapse Tips</span>
                </div>
                <ul class="pl-4 mb-0 text-caption">
                  <li class="mb-1">Frame Interval determines how often timelapse captures are taken</li>
                  <li class="mb-1">Lower opacity values help distinguish between different timelapse frames</li>
                  <li>Use the Manage Models button to selectively delete timelapse frames</li>
                </ul>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="showTimelapseSettings = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Timelapse Manager Dialog -->
    <v-dialog v-model="showTimelapseManager" max-width="500">
      <v-card>
        <v-card-title>Manage Timelapse Models</v-card-title>
        <v-card-text>
          <div v-for="(group, animIndex) in timelapseGroups" :key="animIndex" class="mb-4">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="subtitle-1">{{ getAnimationName(animIndex) }}</div>
              <v-btn small text color="error" @click="$emit('delete-timelapse-group', animIndex)">
                Delete All
              </v-btn>
            </div>
            <v-list dense>
              <v-list-item v-for="frame in group" :key="frame" class="mb-1">
                <v-list-item-content>
                  <v-list-item-title>
                    Frame {{ frame }}
                    <span class="text-caption grey--text ml-2">
                      (Mesh ID: {{ getMeshIdForFrame(animIndex, frame) }})
                    </span>
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-action>
                  <v-btn small icon color="error" @click="$emit('delete-timelapse-frame', animIndex, frame)">
                    <v-icon small>mdi-delete</v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </div>
          <div v-if="Object.keys(timelapseGroups).length === 0" class="text-center grey--text">
            No timelapse models created yet
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showTimelapseManager = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'TimelapseControls',

  props: {
    timelapseMode: {
      type: Boolean,
      default: false
    },
    timelapseInterval: {
      type: Number,
      default: 5
    },
    timelapseOpacity: {
      type: Number,
      default: 0.5
    },
    timelapseGroups: {
      type: Object,
      default: () => ({})
    },
    animations: {
      type: Array,
      default: () => []
    },
    getMeshIdForFrame: {
      type: Function,
      default: () => ''
    }
  },

  data() {
    return {
      showTimelapseDetails: false,
      showTimelapseSettings: false,
      showTimelapseManager: false
    };
  },

  methods: {
    onTimelapseModeChange(value) {
      this.$emit('update:timelapseMode', value);
      this.$emit('toggle-timelapse-mode');
    },

    onIntervalInput(value) {
      this.$emit('update:timelapseInterval', value);
      this.$emit('update-timelapse');
    },

    onOpacityInput(value) {
      this.$emit('update:timelapseOpacity', value / 100);
    },

    onOpacityChange() {
      this.$emit('update-timelapse-opacity');
    },

    openTimelapseSettings(event) {
      event.stopPropagation();
      this.showTimelapseSettings = true;
    },

    getAnimationName(animIndex) {
      const anim = this.animations[animIndex];
      return anim?.trialName || `Subject ${parseInt(animIndex) + 1}`;
    }
  }
};
</script>

<style scoped>
.timelapse-section {
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

.settings-text-btn {
  text-transform: none;
  letter-spacing: normal;
}

.recording-summary {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 8px;
}

.recording-settings-dialog {
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
</style>
