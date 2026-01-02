/**
 * Color utility functions
 * Helper functions for color management and conversion
 */

import * as THREE from 'three';

/**
 * Convert color value to hex string
 * @param {string|Object|THREE.Color} colorValue - Color input (hex string, color picker object, or THREE.Color)
 * @returns {string} Hex color string (e.g., "#ffffff")
 */
export function colorToHex(colorValue) {
  if (!colorValue) {
    return '#ffffff'; // Default to white
  }
  
  // If it's already a hex string
  if (typeof colorValue === 'string') {
    return colorValue.startsWith('#') ? colorValue : `#${colorValue}`;
  }
  
  // If it's a color picker object
  if (colorValue && typeof colorValue === 'object') {
    if (colorValue.hex) {
      return colorValue.hex.startsWith('#') ? colorValue.hex : `#${colorValue.hex}`;
    }
    if (colorValue.r !== undefined && colorValue.g !== undefined && colorValue.b !== undefined) {
      const r = Math.round(colorValue.r * 255).toString(16).padStart(2, '0');
      const g = Math.round(colorValue.g * 255).toString(16).padStart(2, '0');
      const b = Math.round(colorValue.b * 255).toString(16).padStart(2, '0');
      return `#${r}${g}${b}`;
    }
  }
  
  // If it's a THREE.Color object
  if (colorValue && typeof colorValue.getHexString === 'function') {
    return `#${colorValue.getHexString()}`;
  }
  
  return '#ffffff'; // Default to white
}

/**
 * Convert hex string to THREE.Color
 * @param {string} hexString - Hex color string
 * @returns {THREE.Color} Three.js Color object
 */
export function hexToThreeColor(hexString) {
  if (!hexString) {
    return new THREE.Color(0xffffff);
  }
  
  const hex = hexString.startsWith('#') ? hexString.substring(1) : hexString;
  return new THREE.Color(`#${hex}`);
}

/**
 * Get display color for color picker from THREE.Color
 * @param {THREE.Color|string} color - Color input
 * @returns {string} Hex color string for display
 */
export function getDisplayColor(color) {
  if (!color) {
    return '#ffffff';
  }
  
  if (typeof color === 'string') {
    return color.startsWith('#') ? color : `#${color}`;
  }
  
  if (color && typeof color.getHexString === 'function') {
    return `#${color.getHexString()}`;
  }
  
  return '#ffffff';
}

/**
 * Default color palette
 */
export const DEFAULT_COLORS = [
  new THREE.Color(0xd3d3d3),  // Light Grey
  new THREE.Color(0x4995e0),  // Blue
  new THREE.Color(0xe35335),  // Red
  new THREE.Color(0x0000ff),  // Blue
  new THREE.Color(0xffff00),  // Yellow
  new THREE.Color(0xff00ff),  // Magenta
  new THREE.Color(0x00ffff),  // Cyan
  new THREE.Color(0x8000ff),  // Purple
];

/**
 * Available color swatches for color picker
 */
export const AVAILABLE_COLORS = [
  'original',
  '#00ff00', // Green
  '#ff0000', // Red
  '#0000ff', // Blue
  '#ffff00', // Yellow
  '#ff00ff', // Magenta
  '#00ffff', // Cyan
  '#ff8000', // Orange
  '#8000ff', // Purple
  '#ffffff', // White
  '#808080', // Gray
  '#ff8080', // Light Red
  '#80ff80', // Light Green
  '#8080ff', // Light Blue
  '#ff80ff', // Light Pink
  '#80ffff', // Light Cyan
  '#ffa040', // Light Orange
];

/**
 * Background color options
 */
export const BACKGROUND_COLORS = [
  '#000000',
  '#111111',
  '#1a1a1a',
  '#222222',
  '#333333',
  '#4d4d4d',
  '#666666',
  '#808080',
  '#999999',
  '#b3b3b3',
  '#cccccc',
  '#e6e6e6',
  '#ffffff',
];

/**
 * Ground color options
 */
export const GROUND_COLORS = [
  '#cccccc',
  '#ffffff',
  '#e6e6e6',
  '#b3b3b3',
  '#999999',
  '#666666',
  '#333333',
  '#000000',
  '#d9f2d9',
  '#b3e6b3',
  '#8cd98c',
  '#d9d9f2',
  '#b3b3e6',
  '#8c8cd9',
  '#6666cc',
];
