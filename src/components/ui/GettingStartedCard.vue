<template>
  <div v-if="show" class="getting-started-section mb-4">
    <v-card dark class="pa-4" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
      <div class="d-flex align-center mb-3">
        <v-icon color="primary" class="mr-2">mdi-information-outline</v-icon>
        <h3 class="text-subtitle-1">Getting Started</h3>
      </div>

      <div class="text-caption mb-3">
        <strong>Import Methods:</strong>
      </div>

      <div class="mb-3">
        <v-btn
          color="primary"
          small
          outlined
          block
          @click="$emit('show-sample-selection')"
          class="mb-2"
        >
          <v-icon left small>mdi-play-circle</v-icon>
          Try Sample Data
        </v-btn>
        <div class="text-caption grey--text mb-3">
          Explore with pre-loaded motion capture data
        </div>

      </div>

      <v-divider class="my-3" style="opacity: 0.3;"></v-divider>

      <div class="text-caption mb-2">
        <strong>Workflow Options:</strong>
      </div>

      <div class="workflow-steps text-caption">
        <div class="step-item mb-2">
          <div class="d-flex align-center">
            <v-icon x-small color="orange" class="mr-2">mdi-numeric-1-circle</v-icon>
            <span class="font-weight-medium">OpenSim Files</span>
          </div>
          <div class="ml-5 grey--text">
            Upload .osim model + .mot motion files
          </div>
        </div>

        <div class="step-item mb-2">
          <div class="d-flex align-center">
            <v-icon x-small color="indigo" class="mr-2">mdi-numeric-2-circle</v-icon>
            <span class="font-weight-medium">Motion Data</span>
          </div>
          <div class="ml-5 grey--text">
            Load .json files or .trc marker files
          </div>
        </div>

        <div class="step-item mb-2">
          <div class="d-flex align-center">
            <v-icon x-small color="green" class="mr-2">mdi-numeric-3-circle</v-icon>
            <span class="font-weight-medium">Enhance</span>
          </div>
          <div class="ml-5 grey--text">
            Add forces (.mot), video, or 3D models
          </div>
        </div>
      </div>

      <v-divider class="my-3" style="opacity: 0.3;"></v-divider>

      <div class="text-caption mb-2">
        <strong>Tips:</strong>
      </div>
      <ul class="text-caption grey--text pl-4 mb-0">
        <li class="mb-1">Drag & drop files directly into the viewer (.json, .trc, .osim, .mot)</li>
        <li class="mb-1">Use Import button for batch uploads</li>
        <li class="mb-1">Multiple subjects can be loaded together</li>
        <li class="mb-1">.trc files can be loaded independently</li>
        <li class="mb-1">.mot force files are automatically detected and positioned at feet</li>
      </ul>
    </v-card>
  </div>
</template>

<script>
/**
 * GettingStartedCard Component
 * 
 * Displays introductory information and guidance when no files are loaded in the visualizer.
 * Shows import methods, workflow options, and helpful tips for getting started.
 * 
 * @emits show-sample-selection - Emitted when the "Try Sample Data" button is clicked
 */
export default {
  name: 'GettingStartedCard',
  props: {
    /**
     * Controls whether the getting started card should be displayed
     */
    show: {
      type: Boolean,
      required: true
    }
  }
}
</script>

<style scoped>
/* Component-specific styles can be added here if needed */
</style>
