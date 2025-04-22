<template>
  <div class="camera-controls-container">
    <!-- 3D Cube Gizmo with Integrated Corners & Navigation -->
    <div class="cube-gizmo" title="Set View">
      <!-- Navigation Arrows -->
      <div class="nav-arrows">
        <button class="nav-arrow arrow-up" @click="rotateToAdjacent('up')" title="Rotate Up">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12 4l-8 8h16l-8-8z"/>
          </svg>
        </button>
        <button class="nav-arrow arrow-right" @click="rotateToAdjacent('right')" title="Rotate Right">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12 4l8 8-8 8v-16z"/>
          </svg>
        </button>
        <button class="nav-arrow arrow-down" @click="rotateToAdjacent('down')" title="Rotate Down">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12 20l8-8H4l8 8z"/>
          </svg>
        </button>
        <button class="nav-arrow arrow-left" @click="rotateToAdjacent('left')" title="Rotate Left">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12 4l-8 8 8 8v-16z"/>
          </svg>
        </button>
      </div>
      
      <!-- Corner Click Targets -->
      <div class="corner-click-targets">
        <div class="corner-target corner-top-right-front" @click="setView('frontTopRight')" title="Front Top Right Corner"></div>
        <div class="corner-target corner-top-left-front" @click="setView('frontTopLeft')" title="Front Top Left Corner"></div>
        <div class="corner-target corner-top-right-back" @click="setView('backTopRight')" title="Back Top Right Corner"></div>
        <div class="corner-target corner-top-left-back" @click="setView('backTopLeft')" title="Back Top Left Corner"></div>
        <div class="corner-target corner-bottom-right-front" @click="setView('frontBottomRight')" title="Front Bottom Right Corner"></div>
        <div class="corner-target corner-bottom-left-front" @click="setView('frontBottomLeft')" title="Front Bottom Left Corner"></div>
        <div class="corner-target corner-bottom-right-back" @click="setView('backBottomRight')" title="Back Bottom Right Corner"></div>
        <div class="corner-target corner-bottom-left-back" @click="setView('backBottomLeft')" title="Back Bottom Left Corner"></div>
      </div>
      
      <!-- Reset button -->
      <button class="reset-button" @click="resetCamera()" title="Reset View">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14">
          <path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
        </svg>
      </button>
      
      <!-- Cube faces -->
      <div class="cube" :class="currentView">
        <div class="face front" @click="setView('front')" title="Front View (+Z)">
          <span class="axis-label">Z</span>
        </div>
        <div class="face back" @click="setView('back')" title="Back View (-Z)">
          <span class="axis-label">-Z</span>
        </div>
        <div class="face right" @click="setView('right')" title="Right View (+X)">
          <span class="axis-label">X</span>
        </div>
        <div class="face left" @click="setView('left')" title="Left View (-X)">
          <span class="axis-label">-X</span>
        </div>
        <div class="face top" @click="setView('top')" title="Top View (+Y)">
          <span class="axis-label">Y</span>
        </div>
        <div class="face bottom" @click="setView('bottom')" title="Bottom View (-Y)">
          <span class="axis-label">-Y</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CameraControls',
  emits: ['setView', 'resetCamera'], // Declare emitted events
  
  data() {
    return {
      currentView: 'default', // Track current view to apply correct rotation
      // Map of adjacent faces for each current face
      adjacentFaces: {
        front: { up: 'top', right: 'right', down: 'bottom', left: 'left' },
        back: { up: 'top', right: 'left', down: 'bottom', left: 'right' },
        right: { up: 'top', right: 'back', down: 'bottom', left: 'front' },
        left: { up: 'top', right: 'front', down: 'bottom', left: 'back' },
        top: { up: 'back', right: 'right', down: 'front', left: 'left' },
        bottom: { up: 'front', right: 'right', down: 'back', left: 'left' },
        // Remove corner adjacency - navigation arrows only go between the 6 main faces
        default: { up: 'top', right: 'right', down: 'bottom', left: 'left' }
      }
    };
  },
  
  methods: {
    setView(viewType) {
      console.log('Setting view to:', viewType);
      this.currentView = viewType; // Update the current view
      
      // Emit event to parent component
      this.$emit('setView', viewType);
    },
    
    rotateToAdjacent(direction) {
      // Get the adjacent face in the specified direction based on current view
      // If current view is a corner, default to rotating from the 'front' view as a baseline
      const baseView = ['front', 'back', 'left', 'right', 'top', 'bottom', 'default'].includes(this.currentView) ? this.currentView : 'default';
      const nextView = this.adjacentFaces[baseView][direction];
      
      if (nextView) {
        this.setView(nextView);
      }
    },
    
    resetCamera() {
      console.log('Resetting camera');
      this.currentView = 'default';
      this.$emit('resetCamera');
    }
  }
};
</script>

<style scoped>
.camera-controls-container {
  position: absolute;
  bottom: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(28, 28, 28, 0.85);
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  min-width: 90px;
  min-height: 90px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cube-gizmo {
  width: 45px;
  height: 45px;
  perspective: 450px;
  position: relative;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

/* Navigation Arrows */
.nav-arrows {
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  pointer-events: none;
  z-index: 10;
}

.nav-arrow {
  position: absolute;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(60, 60, 60, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s ease;
  pointer-events: auto;
  padding: 0;
  z-index: 15;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.nav-arrow:hover {
  background-color: rgba(80, 80, 80, 0.9);
  transform: scale(1.1);
}

/* Arrow positions adjusted to create more space from the cube */
.arrow-up {
  top: -35px;
  left: calc(50% - 12px);
}

.arrow-right {
  right: -35px;
  top: calc(50% - 12px);
}

.arrow-down {
  bottom: -35px;
  left: calc(50% - 12px);
}

.arrow-left {
  left: -35px;
  top: calc(50% - 12px);
}

/* Corner Click Targets (Invisible overlays) */
.corner-click-targets {
  position: absolute;
  inset: -5px; /* Slightly larger area around the cube */
  z-index: 12;
  pointer-events: none; /* Container doesn't capture events */
}

.corner-target {
  position: absolute;
  width: 20px;
  height: 20px;
  cursor: pointer;
  pointer-events: auto; /* Targets capture events */
  /* Optional: Uncomment to visualize targets for debugging */
  /* background-color: rgba(255, 0, 0, 0.2); */
  /* border-radius: 50%; */
}

/* Precise positioning over cube corners in default view */
.corner-top-right-front { top: 0; right: 0; }
.corner-top-left-front { top: 0; left: 0; }
.corner-top-right-back { top: 15px; right: 15px; } /* Approx */
.corner-top-left-back { top: 15px; left: 15px; } /* Approx */
.corner-bottom-right-front { bottom: 15px; right: 15px; } /* Approx */
.corner-bottom-left-front { bottom: 15px; left: 15px; } /* Approx */
.corner-bottom-right-back { bottom: 0; right: 0; }
.corner-bottom-left-back { bottom: 0; left: 0; }

/* Reset button adjusted */
.reset-button {
  position: absolute;
  top: -35px;
  right: -35px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: rgba(80, 80, 80, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s ease;
  z-index: 15;
  padding: 0;
}

.reset-button:hover {
  background-color: rgba(100, 100, 100, 0.9);
  transform: scale(1.1);
}

/* Existing cube styles */
.cube {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transform: rotateX(-25deg) rotateY(45deg);
  transition: transform 0.6s ease;
}

/* Cube Face Styles */
.face {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: bold;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  background-color: rgba(40, 40, 40, 0.9);
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(2px);
}

.face::after {
  content: '';
  position: absolute;
  inset: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  pointer-events: none;
}

.face.front { 
  transform: translateZ(22.5px); 
  background-color: rgba(52, 152, 219, 0.4);
  border-radius: 2px;
}
.face.back { 
  transform: translateZ(-22.5px) rotateY(180deg); 
  background-color: rgba(52, 152, 219, 0.2);
  border-radius: 2px;
}
.face.right { 
  transform: translateX(22.5px) rotateY(90deg); 
  background-color: rgba(231, 76, 60, 0.4);
  border-radius: 2px;
}
.face.left { 
  transform: translateX(-22.5px) rotateY(-90deg); 
  background-color: rgba(231, 76, 60, 0.2);
  border-radius: 2px;
}
.face.top { 
  transform: translateY(-22.5px) rotateX(90deg); 
  background-color: rgba(46, 204, 113, 0.4);
  border-radius: 2px;
}
.face.bottom { 
  transform: translateY(22.5px) rotateX(-90deg); 
  background-color: rgba(46, 204, 113, 0.2);
  border-radius: 2px;
}

.face:hover {
  filter: brightness(1.3);
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.1);
}

.face.front:hover { background-color: rgba(52, 152, 219, 0.6); }
.face.back:hover { background-color: rgba(52, 152, 219, 0.4); }
.face.right:hover { background-color: rgba(231, 76, 60, 0.6); }
.face.left:hover { background-color: rgba(231, 76, 60, 0.4); }
.face.top:hover { background-color: rgba(46, 204, 113, 0.6); }
.face.bottom:hover { background-color: rgba(46, 204, 113, 0.4); }

/* Cube rotation states based on the current view */
.cube.front {
  transform: rotateX(0deg) rotateY(0deg);
}

.cube.back {
  transform: rotateX(0deg) rotateY(180deg);
}

.cube.right {
  transform: rotateX(0deg) rotateY(-90deg);
}

.cube.left {
  transform: rotateX(0deg) rotateY(90deg);
}

.cube.top {
  transform: rotateX(-90deg) rotateY(0deg);
}

.cube.bottom {
  transform: rotateX(90deg) rotateY(0deg);
}

/* Corner view rotations - 45 degree angles */
.cube.frontTopRight {
  transform: rotateX(-35deg) rotateY(-35deg);
}

.cube.frontTopLeft {
  transform: rotateX(-35deg) rotateY(35deg);
}

.cube.frontBottomRight {
  transform: rotateX(35deg) rotateY(-35deg);
}

.cube.frontBottomLeft {
  transform: rotateX(35deg) rotateY(35deg);
}

.cube.backTopRight {
  transform: rotateX(-35deg) rotateY(-145deg);
}

.cube.backTopLeft {
  transform: rotateX(-35deg) rotateY(145deg);
}

.cube.backBottomRight {
  transform: rotateX(35deg) rotateY(-145deg);
}

.cube.backBottomLeft {
  transform: rotateX(35deg) rotateY(145deg);
}

.cube.default {
  transform: rotateX(-25deg) rotateY(45deg);
}

.axis-label {
  font-size: 10px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}
</style> 