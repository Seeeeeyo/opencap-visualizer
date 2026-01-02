/**
 * Three.js utility functions
 * Helper functions for Three.js geometry, materials, and scene management
 */

import * as THREE from 'three';

/**
 * Create arrow head geometry for force visualization
 * @returns {THREE.CylinderGeometry} Arrow head geometry
 */
export function createArrowHeadGeometry() {
  // Create a traditional arrow head using CylinderGeometry
  // This creates a pointed arrow head that tapers to a point
  const arrowHead = new THREE.CylinderGeometry(
    0,        // radiusTop (pointed tip)
    0.02,     // radiusBottom (base width)
    0.1,      // height
    8,        // radialSegments
    1,        // heightSegments
    false     // openEnded
  );

  // Don't rotate the geometry here - keep it aligned with Y-axis like the shaft
  // The rotation will be applied to the mesh during updates

  return arrowHead;
}

/**
 * Create cylinder geometry for arrow shaft
 * @param {number} radius - Radius of the cylinder (default: 0.004)
 * @param {number} height - Height of the cylinder (default: 1)
 * @returns {THREE.CylinderGeometry} Cylinder geometry
 */
export function createArrowShaftGeometry(radius = 0.004, height = 1) {
  return new THREE.CylinderGeometry(radius, radius, height, 8);
}

/**
 * Create sphere geometry for markers
 * @param {number} radius - Radius of the sphere (default: 0.01)
 * @param {number} segments - Number of segments (default: 16)
 * @returns {THREE.SphereGeometry} Sphere geometry
 */
export function createMarkerSphereGeometry(radius = 0.01, segments = 16) {
  return new THREE.SphereGeometry(radius, segments, segments);
}

/**
 * Create text sprite for labels
 * @param {string} text - Text to display
 * @param {Object} options - Options for text sprite
 * @param {string} options.color - Text color (default: '#ffffff')
 * @param {number} options.fontSize - Font size (default: 24)
 * @param {string} options.fontFamily - Font family (default: 'Arial')
 * @returns {THREE.Sprite} Text sprite
 */
export function createTextSprite(text, options = {}) {
  const {
    color = '#ffffff',
    fontSize = 24,
    fontFamily = 'Arial'
  } = options;

  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  
  // Set canvas size
  canvas.width = 256;
  canvas.height = 64;
  
  // Set text style
  context.font = `Bold ${fontSize}px ${fontFamily}`;
  context.fillStyle = color;
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  
  // Draw text
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  
  // Create texture from canvas
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  
  // Create sprite material
  const spriteMaterial = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    alphaTest: 0.1
  });
  
  // Create sprite
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.scale.set(1, 0.25, 1);
  
  return sprite;
}

/**
 * Dispose of Three.js object and its resources
 * @param {THREE.Object3D} object - Three.js object to dispose
 */
export function disposeThreeObject(object) {
  if (!object) return;
  
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      if (child.geometry) {
        child.geometry.dispose();
      }
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(material => disposeMaterial(material));
        } else {
          disposeMaterial(child.material);
        }
      }
    } else if (child instanceof THREE.Sprite) {
      if (child.material) {
        disposeMaterial(child.material);
      }
    }
  });
  
  if (object.parent) {
    object.parent.remove(object);
  }
}

/**
 * Dispose of Three.js material and its resources
 * @param {THREE.Material} material - Material to dispose
 */
export function disposeMaterial(material) {
  if (!material) return;
  
  if (material.map) {
    material.map.dispose();
  }
  if (material.normalMap) {
    material.normalMap.dispose();
  }
  if (material.bumpMap) {
    material.bumpMap.dispose();
  }
  if (material.roughnessMap) {
    material.roughnessMap.dispose();
  }
  if (material.metalnessMap) {
    material.metalnessMap.dispose();
  }
  if (material.aoMap) {
    material.aoMap.dispose();
  }
  if (material.emissiveMap) {
    material.emissiveMap.dispose();
  }
  if (material.alphaMap) {
    material.alphaMap.dispose();
  }
  
  material.dispose();
}

/**
 * Create a color from various input types
 * @param {string|number|THREE.Color|Object} colorInput - Color input
 * @returns {THREE.Color} Three.js Color object
 */
export function createColor(colorInput) {
  if (colorInput instanceof THREE.Color) {
    return colorInput.clone();
  }
  
  if (typeof colorInput === 'string') {
    return new THREE.Color(colorInput);
  }
  
  if (typeof colorInput === 'number') {
    return new THREE.Color(colorInput);
  }
  
  if (colorInput && typeof colorInput === 'object') {
    if (colorInput.hex) {
      return new THREE.Color(colorInput.hex);
    }
    if (colorInput.r !== undefined && colorInput.g !== undefined && colorInput.b !== undefined) {
      return new THREE.Color(colorInput.r, colorInput.g, colorInput.b);
    }
  }
  
  return new THREE.Color(0xffffff); // Default to white
}

/**
 * Convert color to hex string
 * @param {THREE.Color|string|number} color - Color to convert
 * @returns {string} Hex color string (e.g., "#ffffff")
 */
export function colorToHexString(color) {
  if (typeof color === 'string') {
    return color.startsWith('#') ? color : `#${color}`;
  }
  
  if (typeof color === 'number') {
    return `#${color.toString(16).padStart(6, '0')}`;
  }
  
  if (color && typeof color.getHexString === 'function') {
    return `#${color.getHexString()}`;
  }
  
  return '#ffffff'; // Default to white
}
