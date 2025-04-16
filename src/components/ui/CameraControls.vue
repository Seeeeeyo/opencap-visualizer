<template>
  <div class="camera-controls-container">
    <!-- Reset Button -->
    <button @click="resetCamera" class="control-button reset-button" title="Reset Camera View">
      Reset
    </button>

    <!-- Axis Gizmo -->
    <div class="axis-gizmo" title="Set View">
      <!-- Center Dot -->
      <div class="gizmo-center"></div>
      <!-- Axis Lines -->
      <div class="gizmo-line line-x"></div>
      <div class="gizmo-line line-y"></div>
      <div class="gizmo-line line-z"></div>
      <!-- Axis Clickable Dots (+ Directions) -->
      <div class="gizmo-axis gizmo-pos-y" @click="setView('top')" title="Top View (+Y)"></div>
      <div class="gizmo-axis gizmo-pos-x" @click="setView('right')" title="Right View (+X)"></div>
      <div class="gizmo-axis gizmo-pos-z" @click="setView('front')" title="Front View (+Z)"></div>
      <!-- Axis Clickable Dots (- Directions - faded) -->
      <div class="gizmo-axis gizmo-neg-y faded" @click="setView('bottom')" title="Bottom View (-Y)"></div>
      <div class="gizmo-axis gizmo-neg-x faded" @click="setView('left')" title="Left View (-X)"></div>
      <div class="gizmo-axis gizmo-neg-z faded" @click="setView('back')" title="Back View (-Z)"></div>
    </div>

    <!-- Isometric Button -->
    <button @click="setView('isometric')" class="control-button iso-button" title="Isometric View">
      Isometric
    </button>
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
  background-color: rgba(45, 45, 45, 0.9); /* Darker, less transparent */
  padding: 5px; /* Slightly less padding */
  border-radius: 22px; /* Slightly more rounded */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  z-index: 1000; /* Keep it on top */
  gap: 6px; /* Slightly less gap */
}

.control-button {
  background-color: #3a3a3a; /* Slightly lighter grey */
  color: #e0e0e0; 
  border: 1px solid #3a3a3a; /* Match background initially */
  padding: 5px 15px; /* Adjusted padding for flatter look */
  margin: 0;
  border-radius: 18px; /* Adjusted rounding */
  cursor: pointer;
  font-size: 13px; 
  font-weight: 500;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  white-space: nowrap;
}

.control-button:hover {
  background-color: #484848;
  border-color: #484848;
  color: #fff;
}

.control-button:active {
  background-color: #555;
  border-color: #555;
}

/* Style for an active/selected button (example, can be added dynamically) */
.control-button.active {
  background-color: #4a90e2; /* Blue background */
  border-color: #4a90e2;
  color: #fff;
}

.axis-gizmo {
  width: 46px; /* Slightly smaller */
  height: 46px;
  border-radius: 50%;
  margin: 0;
  position: relative;
  cursor: pointer;
  background-color: #333; /* Darker gizmo background */
  border: 1px solid #404040; /* Darker border */
  transition: background-color 0.2s ease;
}

.axis-gizmo:hover {
  background-color: #3d3d3d;
}

.gizmo-center {
  position: absolute;
  width: 8px; 
  height: 8px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(80, 80, 80, 0.7); /* Darker, more subtle center */
  border-radius: 50%;
  pointer-events: none;
}

.gizmo-axis {
  position: absolute;
  width: 11px; /* Slightly smaller dots */
  height: 11px;
  border-radius: 50%;
  transition: transform 0.15s ease, filter 0.15s ease, background-color 0.2s ease;
  z-index: 2;
}

.gizmo-axis:hover {
  filter: brightness(1.2);
  transform: scale(1.1);
}

.gizmo-axis.faded {
  background-color: #555 !important; /* Darker grey for inactive */
  opacity: 0.6; /* Less opaque */
}

.gizmo-axis.faded:hover {
  filter: brightness(1.05);
  opacity: 0.7;
}

/* Position axis dots */
.gizmo-pos-y { top: 2px; left: 50%; transform: translateX(-50%); background-color: #2ecc71; } 
.gizmo-neg-y { bottom: 2px; left: 50%; transform: translateX(-50%); }
.gizmo-pos-x { right: 2px; top: 50%; transform: translateY(-50%); background-color: #e74c3c; } 
.gizmo-neg-x { left: 2px; top: 50%; transform: translateY(-50%); }
.gizmo-pos-z { top: 50%; left: 50%; transform: translate(calc(-50% + 9px), calc(-50% - 9px)); background-color: #3498db; } 
.gizmo-neg-z { top: 50%; left: 50%; transform: translate(calc(-50% - 9px), calc(-50% + 9px)); }

/* Axis lines - Change to simple cross */
.gizmo-line {
  position: absolute;
  background-color: rgba(120, 120, 120, 0.4); /* Slightly thicker/less transparent than before */
  pointer-events: none;
  z-index: 1;
}

.line-x {
  width: 60%; /* Make line shorter than full width */
  height: 1px; 
  top: 50%;
  left: 20%; /* Center the line */
  transform: translateY(-50%);
}

.line-y {
  width: 1px; 
  height: 60%; /* Make line shorter than full height */
  top: 20%; /* Center the line */
  left: 50%;
  transform: translateX(-50%);
}

.line-z {
  /* Remove the Z line representation */
  display: none; 
}

</style> 