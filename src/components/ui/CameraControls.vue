<template>
  <div class="camera-controls-container">
    <!-- Reset Button -->
    <button @click="resetCamera" class="control-button reset-button">Reset</button>

    <!-- Axis Gizmo -->
    <div class="axis-gizmo">
      <!-- Center (Placeholder/No action) -->
      <div class="gizmo-center"></div>
      <!-- Axis Clickable Areas -->
      <div class="gizmo-axis gizmo-pos-y" @click="setView('top')" title="Top View (+Y)"></div>
      <div class="gizmo-axis gizmo-neg-y" @click="setView('bottom')" title="Bottom View (-Y)"></div>
      <div class="gizmo-axis gizmo-pos-x" @click="setView('right')" title="Right View (+X)"></div>
      <div class="gizmo-axis gizmo-neg-x" @click="setView('left')" title="Left View (-X)"></div>
      <div class="gizmo-axis gizmo-pos-z" @click="setView('front')" title="Front View (+Z)"></div>
      <div class="gizmo-axis gizmo-neg-z" @click="setView('back')" title="Back View (-Z)"></div>
    </div>

    <!-- Isometric Button -->
    <button @click="setView('isometric')" class="control-button iso-button">Isometric</button>
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
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  background-color: rgba(40, 40, 40, 0.8);
  padding: 8px;
  border-radius: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.control-button {
  background-color: #444;
  color: #eee;
  border: none;
  padding: 8px 16px;
  margin: 0 5px;
  border-radius: 15px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.control-button:hover {
  background-color: #555;
}

.axis-gizmo {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin: 0 10px;
  position: relative;
  cursor: pointer;
  background-color: #555; /* Darker background for the gizmo */
}

.gizmo-center {
  position: absolute;
  width: 20px;
  height: 20px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #333; /* Even darker center */
  border-radius: 50%;
  pointer-events: none; /* Center doesn't need clicks */
}

.gizmo-axis {
  position: absolute;
  width: 16px; /* Size of the clickable end cap */
  height: 16px;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.gizmo-axis:hover {
  filter: brightness(1.3);
}

/* Position and color the axis indicators */
.gizmo-pos-y {
  top: 1px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #4CAF50; /* Green for +Y (Top) */
}

.gizmo-neg-y {
  bottom: 1px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #8BC34A; /* Lighter Green for -Y (Bottom) */
}

.gizmo-pos-x {
  right: 1px;
  top: 50%;
  transform: translateY(-50%);
  background-color: #F44336; /* Red for +X (Right) */
}

.gizmo-neg-x {
  left: 1px;
  top: 50%;
  transform: translateY(-50%);
  background-color: #FF7043; /* Lighter Red for -X (Left) */
}

.gizmo-pos-z {
  top: 50%;
  left: 50%;
  transform: translate(calc(-50% + 8px), calc(-50% + 8px)); /* Offset diagonally */
  background-color: #2196F3; /* Blue for +Z (Front) */
  z-index: 1; /* Ensure it's clickable over others */
}

.gizmo-neg-z {
  top: 50%;
  left: 50%;
  transform: translate(calc(-50% - 8px), calc(-50% - 8px)); /* Offset diagonally opposite */
  background-color: #64B5F6; /* Lighter Blue for -Z (Back) */
}

</style> 