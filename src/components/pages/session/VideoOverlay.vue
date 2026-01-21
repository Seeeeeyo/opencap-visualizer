<template>
  <div
    id="video-overlay"
    v-show="!videoPlaneSettings.visible"
    :style="{
      position: 'fixed',
      top: videoPosition.y + 'px',
      left: videoPosition.x + 'px',
      width: videoSize.width + 'px',
      background: '#000',
      border: '2px solid #fff',
      borderRadius: '8px',
      zIndex: 99999,
      boxShadow: '0 4px 20px rgba(0,0,0,0.8)',
      overflow: 'hidden',
      cursor: isDragging ? 'grabbing' : 'default'
    }"
  >
    <div
      :style="{
        display: 'flex',
        justifyContent: 'space-between',
        padding: '4px',
        background: 'rgba(0, 0, 0, 0.8)',
        cursor: 'grab'
      }"
      @mousedown="$emit('start-drag', $event)"
      @touchstart="$emit('start-drag', $event)"
    >
      <div style="display: flex; align-items: center;">
        <v-icon x-small dark class="mr-1">mdi-drag</v-icon>
        <span class="caption white--text">Drag to move</span>
      </div>
      <div style="display: flex; align-items: center;">
        <v-btn icon x-small dark class="mr-1" @click.stop="$emit('toggle-video-overlay')">
          <v-icon :color="videoOverlayMode ? 'cyan lighten-2' : 'grey lighten-1'">
            {{ videoOverlayMode ? 'mdi-vector-polyline' : 'mdi-vector-polyline-remove' }}
          </v-icon>
        </v-btn>
        <v-btn icon x-small dark @click="$emit('toggle-video-preview')" class="mr-1">
          <v-icon>{{ videoMinimized ? 'mdi-arrow-expand' : 'mdi-arrow-collapse' }}</v-icon>
        </v-btn>
        <v-btn icon x-small dark @click="$emit('close-video')">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </div>
    <div :style="{ position: 'relative' }">
      <video
        ref="videoPreview"
        :style="{ width: '100%', height: 'auto', minHeight: videoMinimized ? '120px' : '200px' }"
        @loadedmetadata="$emit('video-loadedmetadata', $event)"
        @timeupdate="$emit('video-timeupdate', $event)"
        :loop="isLooping"
        controls
      >
        <source :src="videoUrl" :type="videoFile.type">
        Your browser does not support the video tag.
      </video>
      <canvas
        v-show="videoOverlayMode"
        ref="videoProjectionCanvas"
        :style="{
          position: 'absolute',
          top: '0',
          left: '0',
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          opacity: videoOverlayOpacity
        }"
      ></canvas>
    </div>

    <!-- Resize handle -->
    <div
      :style="{
        position: 'absolute',
        bottom: '0',
        right: '0',
        width: '20px',
        height: '20px',
        cursor: 'nwse-resize',
        background: 'linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.5) 50%)'
      }"
      @mousedown="$emit('start-resize', $event)"
      @touchstart="$emit('start-resize', $event)"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'VideoOverlay',
  props: {
    videoFile: {
      type: Object,
      required: true
    },
    videoUrl: {
      type: String,
      required: true
    },
    videoPosition: {
      type: Object,
      required: true,
      validator: (v) => typeof v.x === 'number' && typeof v.y === 'number'
    },
    videoSize: {
      type: Object,
      required: true,
      validator: (v) => typeof v.width === 'number'
    },
    videoPlaneSettings: {
      type: Object,
      required: true,
      validator: (v) => typeof v.visible === 'boolean'
    },
    isDragging: {
      type: Boolean,
      default: false
    },
    isResizing: {
      type: Boolean,
      default: false
    },
    videoMinimized: {
      type: Boolean,
      default: false
    },
    videoOverlayMode: {
      type: Boolean,
      default: false
    },
    videoOverlayOpacity: {
      type: Number,
      default: 1
    },
    isLooping: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    // Expose refs to parent component
    getVideoPreview() {
      return this.$refs.videoPreview;
    },
    getVideoProjectionCanvas() {
      return this.$refs.videoProjectionCanvas;
    }
  }
};
</script>
