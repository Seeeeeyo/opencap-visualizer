/**
 * Animation utility functions
 * Pure functions for animation data processing
 */

/**
 * Calculate frame rate from time array
 * @param {Array<number>} timeArray - Array of time values
 * @returns {number} Calculated frame rate (frames per second)
 */
export function calculateFrameRate(timeArray) {
  if (!Array.isArray(timeArray) || timeArray.length < 2) {
    return 60; // Default to 60 if not enough data
  }

  // Calculate total duration
  const totalTime = timeArray[timeArray.length - 1] - timeArray[0];

  // For more accurate frame rate calculation, we need to analyze the time step distribution
  // This handles cases where time steps are not uniform
  const timeSteps = [];
  for (let i = 1; i < timeArray.length; i++) {
    const step = timeArray[i] - timeArray[i - 1];
    if (step > 0) {  // Ignore zero or negative steps
      timeSteps.push(step);
    }
  }

  if (timeSteps.length === 0) {
    return 60; // Default if no valid time steps
  }

  // Sort time steps to find the most common ones (mode)
  timeSteps.sort((a, b) => a - b);

  // Find the median time step for more stability
  const medianTimeStep = timeSteps[Math.floor(timeSteps.length / 2)];

  // Use frames per total duration as a fallback
  const averageFrameRate = (timeArray.length - 1) / totalTime;

  // Use the median-based frame rate if it's reasonable, otherwise use the average
  const medianFrameRate = medianTimeStep > 0 ? 1 / medianTimeStep : averageFrameRate;

  // Determine the final frame rate - prefer median for stability unless it's very different
  const finalFrameRate = Math.abs(medianFrameRate - averageFrameRate) < 10
    ? medianFrameRate : averageFrameRate;

  // Round and constrain to reasonable values
  const calculatedFps = Math.round(finalFrameRate);

  // Log the calculated frame rate for debugging
  console.log('Calculated frame rate:', {
    totalTime,
    frameCount: timeArray.length,
    medianTimeStep,
    medianFrameRate,
    averageFrameRate,
    finalFrameRate,
    calculatedFps
  });

  // Constrain to reasonable values (1-240 fps)
  return Math.max(1, Math.min(240, calculatedFps));
}

/**
 * Format time value for display
 * @param {number} time - Time in seconds
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted time string
 */
export function formatTime(time, decimals = 2) {
  const num = parseFloat(time);
  if (!Number.isFinite(num)) {
    return '0.00';
  }
  return num.toFixed(decimals);
}

/**
 * Format video duration for display (MM:SS format)
 * @param {number} duration - Duration in seconds
 * @returns {string} Formatted duration string (e.g., "1:23")
 */
export function formatVideoDuration(duration) {
  if (!Number.isFinite(duration) || duration <= 0) {
    return '0:00';
  }
  const totalSeconds = Math.max(0, duration);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * Generate time array from frame count and frame rate
 * @param {number} frameCount - Number of frames
 * @param {number} fps - Frames per second
 * @returns {Array<number>} Array of time values
 */
export function generateTimeArray(frameCount, fps) {
  const timeArray = [];
  if (!frameCount || frameCount <= 0) return timeArray;
  const step = fps ? 1 / fps : 1 / 60; // Default to 60 fps if not provided
  for (let i = 0; i < frameCount; i++) {
    timeArray.push(i * step);
  }
  return timeArray;
}

/**
 * Get frame time in seconds from frame index
 * @param {number} frameIndex - Frame index
 * @param {Array<number>} frames - Array of frame time values
 * @param {number} frameRate - Frame rate (fallback if frames array is empty)
 * @returns {number} Time in seconds
 */
export function getFrameSeconds(frameIndex, frames = [], frameRate = 60) {
  const framesLength = Array.isArray(frames) ? frames.length : 0;
  const safeRate = Number.isFinite(frameRate) && frameRate > 0 ? frameRate : 60;
  
  if (framesLength === 0) {
    return Number.isFinite(frameIndex) ? frameIndex / safeRate : 0;
  }
  
  const clampedIndex = Number.isFinite(frameIndex)
    ? Math.min(Math.max(Math.round(frameIndex), 0), framesLength - 1)
    : 0;
  
  const raw = frames[clampedIndex];
  if (typeof raw === 'number' && Number.isFinite(raw)) {
    return raw;
  }
  
  const parsed = parseFloat(raw);
  if (Number.isFinite(parsed)) {
    return parsed;
  }
  
  return clampedIndex / safeRate;
}

/**
 * Clamp frame index to valid range
 * @param {number} frameIndex - Frame index to clamp
 * @param {number} maxFrame - Maximum frame index
 * @returns {number} Clamped frame index
 */
export function clampFrameIndex(frameIndex, maxFrame) {
  return Math.min(Math.max(Math.round(frameIndex), 0), maxFrame);
}

/**
 * Find common time range across multiple animations
 * @param {Array<Object>} animations - Array of animation objects with data.time arrays
 * @param {Array<number>} markerTimes - Optional marker time data
 * @returns {Object} Object with start, end, and commonTimeArray
 */
export function findCommonTimeRange(animations = [], markerTimes = null) {
  let latestStart = -Infinity;
  let earliestEnd = Infinity;
  let smallestTimeStep = Infinity;

  // First pass: find time boundaries and smallest time step from animations
  animations.forEach(animation => {
    if (animation && animation.data && animation.data.time && animation.data.time.length > 0) {
      const startTime = animation.data.time[0];
      const endTime = animation.data.time[animation.data.time.length - 1];
      latestStart = Math.max(latestStart, startTime);
      earliestEnd = Math.min(earliestEnd, endTime);

      // Find smallest time step
      for (let i = 1; i < animation.data.time.length; i++) {
        const timeStep = animation.data.time[i] - animation.data.time[i - 1];
        if (timeStep > 0) {
          smallestTimeStep = Math.min(smallestTimeStep, timeStep);
        }
      }
    }
  });

  // Also consider marker time data if available
  if (markerTimes && Array.isArray(markerTimes) && markerTimes.length > 0) {
    const markerStart = markerTimes[0];
    const markerEnd = markerTimes[markerTimes.length - 1];
    latestStart = Math.max(latestStart, markerStart);
    earliestEnd = Math.min(earliestEnd, markerEnd);

    // Find smallest time step in markers
    for (let i = 1; i < markerTimes.length; i++) {
      const timeStep = markerTimes[i] - markerTimes[i - 1];
      if (timeStep > 0) {
        smallestTimeStep = Math.min(smallestTimeStep, timeStep);
      }
    }
  }

  // Generate common time array
  const commonTimeArray = [];
  if (latestStart !== -Infinity && earliestEnd !== Infinity && smallestTimeStep !== Infinity) {
    for (let t = latestStart; t <= earliestEnd; t += smallestTimeStep) {
      commonTimeArray.push(parseFloat(t.toFixed(6))); // Round to avoid floating point issues
    }
  }

  return {
    start: latestStart !== -Infinity ? latestStart : 0,
    end: earliestEnd !== Infinity ? earliestEnd : 0,
    smallestTimeStep: smallestTimeStep !== Infinity ? smallestTimeStep : 1 / 60,
    commonTimeArray
  };
}
