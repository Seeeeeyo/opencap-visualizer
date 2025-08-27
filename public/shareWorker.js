// Web Worker for processing share data
self.onmessage = function(e) {
  const { type, data } = e.data;
  
  switch (type) {
    case 'compress':
      const compressed = compressShareData(data);
      self.postMessage({ type: 'compressed', data: compressed });
      break;
      
    case 'decompress':
      const decompressed = decompressShareData(data);
      self.postMessage({ type: 'decompressed', data: decompressed });
      break;
      
    case 'optimizeForces':
      const optimized = optimizeForcesData(data);
      self.postMessage({ type: 'forcesOptimized', data: optimized });
      break;
  }
};

function optimizeForcesData(forcesData) {
  const optimized = {};
  
  Object.keys(forcesData).forEach(animationIndex => {
    const forceData = forcesData[animationIndex];
    optimized[animationIndex] = {
      fileName: forceData.fileName,
      data: {}
    };
    
    Object.keys(forceData.data).forEach(channelName => {
      const channelData = forceData.data[channelName];
      
      // Check if all values are zero
      const allZero = channelData.every(val => val === 0);
      const nonZeroCount = channelData.filter(val => val !== 0).length;
      const zeroRatio = (channelData.length - nonZeroCount) / channelData.length;
      
      if (allZero) {
        optimized[animationIndex].data[channelName] = {
          type: 'zeros',
          count: channelData.length
        };
      } else if (zeroRatio > 0.8) {
        const nonZeroValues = [];
        channelData.forEach((val, index) => {
          if (val !== 0) {
            nonZeroValues.push([index, val]);
          }
        });
        optimized[animationIndex].data[channelName] = {
          type: 'sparse',
          values: nonZeroValues,
          length: channelData.length
        };
      } else {
        optimized[animationIndex].data[channelName] = {
          type: 'full',
          values: channelData.map(val => Math.round(val * 1000) / 1000)
        };
      }
    });
  });
  
  return optimized;
}

function compressShareData(data) {
  // Simple compression for share data
  const jsonString = JSON.stringify(data);
  return btoa(encodeURIComponent(jsonString));
}

function decompressShareData(compressed) {
  try {
    const jsonString = decodeURIComponent(atob(compressed));
    return JSON.parse(jsonString);
  } catch (error) {
    throw new Error('Failed to decompress data');
  }
}
