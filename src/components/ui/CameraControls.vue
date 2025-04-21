<template>
  <div class="camera-controls-container">
    <!-- 3D Cube Gizmo -->
    <div class="cube-gizmo" title="Set View">
      <!-- Cube faces -->
      <div class="cube">
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
  methods: {
    setView(viewType) {
      console.log('Emitting setView:', viewType);
      this.$emit('setView', viewType);
    },
    resetCamera() {
      console.log('Emitting resetCamera');
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
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  min-width: 75px;
  min-height: 75px;
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

.cube {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transform: rotateX(-25deg) rotateY(45deg);
  transition: transform 0.3s ease;
}

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

.axis-label {
  font-size: 10px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}
</style> 