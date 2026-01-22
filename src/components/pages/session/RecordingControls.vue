<template>
  <div class="recording-controls mb-4">
    <!-- Video Recording Section -->
    <div class="recording-section mb-6 pa-3">
      <div class="section-title mb-3">Video Recording</div>
      <!-- Record button row with settings button -->
      <div class="d-flex align-center mb-3">
        <v-btn v-if="!isRecording" color="#EF4444" dark @click="$emit('start-recording')" :disabled="isRecording" class="custom-btn" style="flex: 1;">
          <v-icon left>mdi-record</v-icon>
          Record
        </v-btn>
        <v-btn v-else color="#E53E3E" dark @click="$emit('stop-recording')" class="custom-btn pulse-recording" style="flex: 1;">
          <v-icon left>mdi-stop</v-icon>
          <span class="font-weight-bold">RECORDING</span>
          <span v-if="loopCount !== Infinity" class="caption ml-1">({{ currentLoop }}/{{ loopCount }})</span>
        </v-btn>

        <v-btn
          small
          outlined
          color="white"
          class="ml-2 settings-text-btn"
          @click="openRecordingSettings($event)"
          :disabled="isRecording"
        >
          Settings
        </v-btn>
      </div>

      <!-- Recording settings summary -->
      <div class="d-flex align-center recording-summary">
        <div class="text-caption text-center" style="flex: 1;">
          <span class="font-weight-bold">Format:</span> {{ recordingFormat === 'webm' ? 'WebM' : 'MP4' }}
        </div>
        <div class="text-caption text-center" style="flex: 1;">
          <span class="font-weight-bold">Bitrate:</span> {{ (videoBitrate / 1000000).toFixed(0) }} Mbps
        </div>
        <div class="text-caption text-center" style="flex: 1;">
          <span class="font-weight-bold">Loops:</span> {{ loopCount === Infinity ? '∞' : loopCount }}
        </div>
      </div>

      <!-- Recording settings dialog -->
      <v-dialog
        v-model="showRecordingSettings"
        max-width="500"
      >
        <v-card class="recording-settings-dialog">
          <v-card-title>Recording Settings</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-select
                  :value="loopCount"
                  @input="$emit('update:loopCount', $event)"
                  :items="[
                    {text: 'Infinite ∞', value: Infinity},
                    {text: '1 Loop', value: 1},
                    {text: '2 Loops', value: 2},
                    {text: '3 Loops', value: 3},
                    {text: '4 Loops', value: 4},
                    {text: '5 Loops', value: 5}
                  ]"
                  label="Number of Loops"
                  outlined
                  dense
                  dark
                  hide-details="auto"
                  class="mb-4"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-select
                  :value="recordingFormat"
                  @input="$emit('update:recordingFormat', $event)"
                  :items="[
                    {text: 'WebM (Recommended)', value: 'webm'},
                    {text: 'MP4 (May be limited)', value: 'mp4'}
                  ]"
                  label="Video Format"
                  outlined
                  dense
                  dark
                  hide-details="auto"
                  class="mb-4"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-select
                  :value="videoBitrate"
                  @input="$emit('update:videoBitrate', $event)"
                  :items="[
                    {text: '2 Mbps', value: 2000000},
                    {text: '5 Mbps', value: 5000000},
                    {text: '8 Mbps', value: 8000000},
                    {text: '12 Mbps', value: 12000000},
                    {text: '15 Mbps', value: 15000000},
                    {text: '20 Mbps', value: 20000000}
                  ]"
                  label="Video Bitrate"
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
                    <span class="subtitle-2">Recording Tips</span>
                  </div>
                  <ul class="pl-4 mb-0 text-caption">
                    <li class="mb-1">Maximize your browser window for best quality</li>
                    <li class="mb-1">Use WebM format for better compatibility</li>
                    <li>Higher bitrates produce larger files but better quality</li>
                  </ul>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" text @click="showRecordingSettings = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecordingControls',

  props: {
    isRecording: {
      type: Boolean,
      default: false
    },
    loopCount: {
      type: Number,
      default: Infinity
    },
    currentLoop: {
      type: Number,
      default: 1
    },
    recordingFormat: {
      type: String,
      default: 'webm'
    },
    videoBitrate: {
      type: Number,
      default: 8000000
    }
  },

  data() {
    return {
      showRecordingSettings: false
    };
  },

  methods: {
    openRecordingSettings(event) {
      event.stopPropagation();
      this.showRecordingSettings = true;
    }
  }
};
</script>

<style scoped>
.recording-section {
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

.custom-btn {
  text-transform: none;
  letter-spacing: normal;
}

.pulse-recording {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(229, 62, 62, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(229, 62, 62, 0);
  }
}
</style>
