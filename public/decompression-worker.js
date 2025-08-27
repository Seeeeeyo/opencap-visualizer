// Web Worker for handling animation data decompression
self.onmessage = function(e) {
  const { compressed, workerId } = e.data;
  
  try {
    console.log(`Worker ${workerId}: Starting decompression`);
    const startTime = Date.now();
    
    // Reconstruct the original animation data format with optimized performance
    const animData = {
      time: compressed.t,
      bodies: {}
    };

    const bodyKeys = Object.keys(compressed.b);
    
    // Process bodies efficiently
    bodyKeys.forEach(bodyKey => {
      const compressedBody = compressed.b[bodyKey];
      const body = {
        attachedGeometries: compressedBody.g,
        scaleFactors: compressedBody.s,
        translation: [],
        rotation: []
      };

      // Decompress positions with optimized array operations
      if (compressedBody.p && compressedBody.p.length > 0) {
        const positions = compressedBody.p;
        const translations = new Array(positions.length);
        let currentPos = [0, 0, 0];
        
        for (let frame = 0; frame < positions.length; frame++) {
          if (frame === 0) {
            currentPos = [positions[frame][0], positions[frame][1], positions[frame][2]];
          } else {
            if (positions[frame] !== null) {
              currentPos[0] += positions[frame][0];
              currentPos[1] += positions[frame][1];
              currentPos[2] += positions[frame][2];
            }
          }
          translations[frame] = [currentPos[0], currentPos[1], currentPos[2]];
        }
        body.translation = translations;
      }

      // Decompress rotations with optimized array operations
      if (compressedBody.r && compressedBody.r.length > 0) {
        const rotations = compressedBody.r;
        const rotationArray = new Array(rotations.length);
        let currentRot = [0, 0, 0];
        
        for (let frame = 0; frame < rotations.length; frame++) {
          if (frame === 0) {
            currentRot = [rotations[frame][0], rotations[frame][1], rotations[frame][2]];
          } else {
            if (rotations[frame] !== null) {
              currentRot[0] += rotations[frame][0];
              currentRot[1] += rotations[frame][1];
              currentRot[2] += rotations[frame][2];
            }
          }
          rotationArray[frame] = [currentRot[0], currentRot[1], currentRot[2]];
        }
        body.rotation = rotationArray;
      }

      animData.bodies[bodyKey] = body;
    });

    const endTime = Date.now();
    console.log(`Worker ${workerId}: Decompression completed in ${endTime - startTime}ms`);

    // Send the decompressed data back to the main thread
    self.postMessage({
      success: true,
      data: animData,
      workerId: workerId,
      processingTime: endTime - startTime
    });

  } catch (error) {
    console.error(`Worker ${workerId}: Decompression failed:`, error);
    self.postMessage({
      success: false,
      error: error.message,
      workerId: workerId
    });
  }
};

