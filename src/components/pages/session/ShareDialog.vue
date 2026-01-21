<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="600" content-class="share-dialog">
    <v-card class="share-dialog-card">
      <v-card-title class="headline white--text">Share Visualization</v-card-title>
      <v-card-text class="white--text pt-8">
        <div class="mb-4">
          <p class="text-body-2 mb-3">Share your visualization with others using a direct link:</p>

          <!-- Share Options Tabs -->
          <v-tabs v-model="shareMethod" background-color="transparent" color="primary" class="mb-4 mt-8">
            <v-tab key="url">Share URL</v-tab>
            <v-tab key="file">Share File</v-tab>
          </v-tabs>

          <v-tabs-items v-model="shareMethod">
            <!-- URL Sharing -->
            <v-tab-item key="url">
              <v-text-field
                :value="shareUrl"
                label="Share URL"
                readonly
                outlined
                dense
                class="mb-3 mt-6"
                append-icon="mdi-content-copy"
                @click:append="$emit('copy-to-clipboard', shareUrl)"
                hide-details
                :loading="loadingInitialShare"
                :placeholder="loadingInitialShare ? 'Generating share URL...' : ''"
                :append-icon-disabled="loadingInitialShare || !shareUrl"
              />

              <div class="d-flex flex-wrap gap-2 mb-3">
                <v-btn small color="green" @click="$emit('open-in-new-tab', shareUrl)" :disabled="loadingInitialShare || !shareUrl">
                  <v-icon left small>mdi-open-in-new</v-icon>
                  Open in New Tab
                </v-btn>
              </div>

            </v-tab-item>

            <!-- File Sharing -->
            <v-tab-item key="file">
              <p class="text-body-2 mb-3">Download a share file that others can import:</p>

              <v-text-field
                :value="shareFileName"
                @input="$emit('update:shareFileName', $event)"
                label="File name"
                outlined
                dense
                suffix=".json"
                class="mb-3"
                hide-details
              />

              <div class="d-flex flex-wrap gap-2 mb-3">
                <v-btn small color="success" @click="$emit('download-share-file')">
                  <v-icon left small>mdi-download</v-icon>
                  Download Share File
                </v-btn>
              </div>

              <v-alert
                type="info"
                dense
                text
                class="mb-3"
              >
                <v-icon left small>mdi-information</v-icon>
                Recipients can import this file using the "Import" button.
              </v-alert>
            </v-tab-item>
          </v-tabs-items>

          <!-- Share Settings -->
          <v-expansion-panels flat>
            <v-expansion-panel>
              <v-expansion-panel-header class="text-body-2">
                <v-icon left small>mdi-cog</v-icon>
                Advanced Settings
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-checkbox
                  :input-value="shareSettings.includeCamera"
                  @change="updateShareSetting('includeCamera', $event)"
                  label="Include camera position"
                  dense
                  hide-details
                  class="mb-2"
                />
                <v-checkbox
                  :input-value="shareSettings.includeColors"
                  @change="updateShareSetting('includeColors', $event)"
                  label="Include custom colors"
                  dense
                  hide-details
                  class="mb-2"
                />
                <v-checkbox
                  :input-value="shareSettings.includeCurrentFrame"
                  @change="updateShareSetting('includeCurrentFrame', $event)"
                  label="Start at current frame"
                  dense
                  hide-details
                  class="mb-3"
                />
                <v-btn small outlined @click="$emit('generate-share-url')" :loading="generatingShareUrl">
                  <v-icon left small>mdi-refresh</v-icon>
                  Update Share URL
                </v-btn>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="$emit('input', false)">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'ShareDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    },
    shareUrl: {
      type: String,
      default: ''
    },
    shareFileName: {
      type: String,
      default: ''
    },
    shareSettings: {
      type: Object,
      default: () => ({
        includeCamera: true,
        includeColors: true,
        includeCurrentFrame: false
      })
    },
    loadingInitialShare: {
      type: Boolean,
      default: false
    },
    generatingShareUrl: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      shareMethod: 0
    };
  },
  methods: {
    updateShareSetting(key, value) {
      this.$emit('update:shareSettings', {
        ...this.shareSettings,
        [key]: value
      });
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .share-dialog {
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

  .v-expansion-panels {
    background-color: transparent !important;
  }

  .v-expansion-panel {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #FFFFFF !important;
  }

  .v-expansion-panel-header {
    color: #FFFFFF !important;
  }

  .v-expansion-panel-content {
    background-color: rgba(255, 255, 255, 0.02) !important;
  }

  .v-btn {
    color: #FFFFFF !important;
  }

  .v-alert {
    background-color: rgba(255, 193, 7, 0.1) !important;
    border: 1px solid rgba(255, 193, 7, 0.3) !important;
    color: #FFC107 !important;
  }

  .v-tabs {
    background-color: transparent !important;
  }

  .v-tab {
    color: rgba(255, 255, 255, 0.7) !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
    margin-right: 8px !important;
    border-radius: 4px !important;
  }

  .v-tab--active {
    color: #FFFFFF !important;
    background-color: rgba(33, 150, 243, 0.3) !important;
  }

  .v-tabs-slider {
    display: none !important;
  }

  .v-tabs-items {
    background-color: transparent !important;
  }

  .v-tab-item {
    background-color: transparent !important;
  }
}
</style>
