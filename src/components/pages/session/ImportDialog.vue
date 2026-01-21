<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="600" content-class="import-dialog">
    <v-card class="import-dialog-card">
      <v-card-title class="headline">Import Files </v-card-title>
      <v-card-text>
        <div class="import-grid">
          <!-- OpenSim -->
          <div class="import-item" @click="$emit('select-file-type', 'osimMotFileInput')">
            <v-icon size="32">mdi-file-document-outline</v-icon>
            <div class="import-item-title">OpenSim</div>
            <div class="import-item-subtitle">.mot + .osim</div>
          </div>

          <!-- Forces -->
          <div class="import-item" @click="$emit('open-forces-dialog')">
            <v-icon size="32">mdi-vector-line</v-icon>
            <div class="import-item-title">Forces</div>
            <div class="import-item-subtitle">.mot format</div>
          </div>

          <!-- Markers -->
          <div class="import-item" @click="$emit('open-markers-dialog')">
            <v-icon size="32">mdi-record-circle-outline</v-icon>
            <div class="import-item-title">Markers</div>
            <div class="import-item-subtitle">.trc format</div>
          </div>

          <!-- JSON Files -->
          <div class="import-item" @click="$emit('select-file-type', 'fileInput')">
            <v-icon size="32">mdi-file</v-icon>
            <div class="import-item-title">JSON Files</div>
            <div class="import-item-subtitle">OpenCap Format</div>
          </div>

          <!-- Video -->
          <div class="import-item" @click="$emit('select-file-type', 'videoFileInput')">
            <v-icon size="32">mdi-play-circle-outline</v-icon>
            <div class="import-item-title">Video</div>
            <div class="import-item-subtitle">MP4, WEBM</div>
          </div>

          <!-- 3D Model -->
          <div class="import-item" @click="$emit('select-file-type', 'objFileInput')">
            <v-icon size="32">mdi-cube-outline</v-icon>
            <div class="import-item-title">3D Model</div>
            <div class="import-item-subtitle">GLTF, STL, FBX, OBJ</div>
          </div>
        </div>

      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="$emit('input', false)">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'ImportDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
.import-dialog-card {
  background-color: #1E1E1E;
  color: #FFFFFF;
  border-radius: 12px;
  overflow: hidden;

  .v-card-title {
    background-color: #282828;
    font-size: 1.6rem;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .v-card-text {
    color: #FFFFFF;
    padding: 30px;
  }

  .v-card-actions {
    background-color: #282828;
    padding: 12px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
}

.import-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;

  .import-item {
    background-color: #282828;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    border: 1px solid rgba(255, 255, 255, 0.1);

    &:hover {
      background-color: #333333;
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }

    .v-icon {
      font-size: 36px;
      display: block;
      margin: 0 auto 12px;
    }

    .import-item-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .import-item-subtitle {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.7);
    }
  }

  .disabled {
    opacity: 0.6;
    cursor: not-allowed;

    &:hover {
      transform: none;
      background-color: #282828;
      box-shadow: none;
    }
  }
}
</style>
