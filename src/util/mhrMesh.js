import * as THREE from 'three';

const DEFAULT_MHR_COLOR = 0x7ec8e3;

export function decodeBase64Float32(b64, expectedLength = null) {
  if (!b64 || typeof b64 !== 'string') return null;
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  const array = new Float32Array(bytes.buffer);
  if (expectedLength != null && array.length !== expectedLength) {
    console.warn('[mhr] Float32 length mismatch', { expectedLength, actualLength: array.length });
    return null;
  }
  return array;
}

export function parseLiveFloat32Payload(payload, expectedLength) {
  if (payload == null) return null;
  if (payload instanceof Float32Array) {
    if (expectedLength != null && payload.length !== expectedLength) return null;
    return payload;
  }
  if (Array.isArray(payload)) {
    const array = new Float32Array(payload);
    if (expectedLength != null && array.length !== expectedLength) return null;
    return array;
  }
  if (typeof payload === 'string') {
    return decodeBase64Float32(payload, expectedLength);
  }
  return null;
}

function normalizeFaces(faces, vertexCount) {
  if (!faces || !faces.length) return [];
  let facesArray = faces;
  if (Array.isArray(facesArray[0])) {
    facesArray = facesArray.flat();
  }
  const typedIndices = facesArray.constructor === Uint16Array || facesArray.constructor === Uint32Array
    ? facesArray
    : (vertexCount > 65535 ? new Uint32Array(facesArray) : new Uint16Array(facesArray));
  return typedIndices;
}

export function createMhrMeshGeometry(meta, templateVertices) {
  const vertexCount = Number(meta.vertexCount || meta.vertex_count) || 0;
  if (!vertexCount || !templateVertices) return null;

  const positionAttribute = new THREE.Float32BufferAttribute(
    templateVertices.slice(0, vertexCount * 3),
    3
  );
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', positionAttribute);

  if (meta.faces && meta.faces.length) {
    const typedIndices = normalizeFaces(meta.faces, vertexCount);
    geometry.setIndex(new THREE.BufferAttribute(typedIndices, 1));
  }

  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  return { geometry, positionAttribute, vertexCount };
}

export function buildMhrMesh(meta, templateVertices, color = DEFAULT_MHR_COLOR) {
  const built = createMhrMeshGeometry(meta, templateVertices);
  if (!built) return null;

  const material = new THREE.MeshPhongMaterial({
    color: new THREE.Color(color),
    transparent: false,
    opacity: 1.0,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(built.geometry, material);
  mesh.castShadow = false;
  mesh.receiveShadow = false;
  mesh.frustumCulled = false;
  return { mesh, ...built };
}

export function updateMhrSequenceFrame(sequence, frameIndex, force = false) {
  if (!sequence || frameIndex < 0) return;
  const clampedFrame = Math.min(frameIndex, Math.max(sequence.frameCount - 1, 0));
  if (!force && sequence.lastRenderedFrame === clampedFrame) return;

  if (sequence.mesh && sequence.vertices && sequence.vertexCount > 0) {
    const start = clampedFrame * sequence.frameStride;
    const end = start + sequence.frameStride;
    if (
      sequence.positionAttribute &&
      end <= sequence.vertices.length &&
      sequence.positionAttribute.array.length >= sequence.frameStride
    ) {
      sequence.positionAttribute.array.set(sequence.vertices.subarray(start, end));
      sequence.positionAttribute.needsUpdate = true;
      if (sequence.geometry) {
        if (sequence.geometry.attributes.position !== sequence.positionAttribute) {
          sequence.geometry.setAttribute('position', sequence.positionAttribute);
        }
        sequence.geometry.computeVertexNormals();
      }
    }
    if (sequence.mesh) {
      sequence.mesh.rotation.copy(sequence.rotation);
      if (sequence.offset) {
        sequence.mesh.position.set(sequence.offset.x, sequence.offset.y, sequence.offset.z);
      }
    }
  }

  sequence.lastRenderedFrame = clampedFrame;
}

export function centerCameraOnMhrSequence(sequence, camera, controls, renderer, scene) {
  if (!sequence || !sequence.mesh || !camera || !controls) return;

  sequence.mesh.geometry.computeBoundingBox();
  if (sequence.mesh.parent) {
    sequence.mesh.parent.updateMatrixWorld(true);
  }
  sequence.mesh.updateMatrixWorld(true);

  const boundingBox = new THREE.Box3().setFromObject(sequence.mesh);
  const center = new THREE.Vector3();
  boundingBox.getCenter(center);

  const size = new THREE.Vector3();
  boundingBox.getSize(size);
  const maxDim = Math.max(size.x, size.y, size.z);

  const fov = camera.fov * (Math.PI / 180);
  const distance = Math.max(Math.abs(maxDim / Math.sin(fov / 2)) * 1.5, 1.0);
  const direction = new THREE.Vector3(1, 1, 1).normalize();
  const position = center.clone().add(direction.multiplyScalar(distance));

  camera.position.copy(position);
  camera.lookAt(center);
  controls.target.copy(center);
  controls.update();

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

export function disposeMhrSequence(sequence, scene) {
  if (!sequence) return;
  if (sequence.mesh && scene) {
    scene.remove(sequence.mesh);
    if (sequence.mesh.geometry) sequence.mesh.geometry.dispose();
    const mat = sequence.mesh.material;
    if (Array.isArray(mat)) {
      mat.forEach((m) => m.dispose && m.dispose());
    } else if (mat && mat.dispose) {
      mat.dispose();
    }
  }
}

export function trimLiveMhrMotionBuffers(sequence, maxLiveFrames) {
  if (!sequence || !sequence.isLive || !maxLiveFrames) return;
  if (!Array.isArray(sequence.time) || sequence.time.length <= maxLiveFrames) return;

  const excess = sequence.time.length - maxLiveFrames;
  sequence.time.splice(0, excess);

  const vertexStride = sequence.frameStride || 0;
  if (vertexStride > 0 && sequence.vertices && sequence.vertices.length >= excess * vertexStride) {
    sequence.vertices = sequence.vertices.slice(excess * vertexStride);
  }

  sequence.frameCount = sequence.time.length;
}

export function appendLiveMhrFrame(sequence, streamData, parsePayload) {
  if (!sequence || !sequence.isLive || !streamData) return false;

  const t = typeof streamData.time === 'number'
    ? streamData.time
    : (sequence.time.length > 0 ? sequence.time[sequence.time.length - 1] : 0);

  const vertexStride = sequence.frameStride || 0;
  let frameVerts = null;
  if (sequence.liveHasMesh && vertexStride > 0 && streamData.vertices != null) {
    frameVerts = parsePayload(streamData.vertices, vertexStride);
  }
  if (!frameVerts) return false;

  sequence.time.push(t);

  const prev = sequence.vertices || new Float32Array(0);
  const next = new Float32Array(prev.length + vertexStride);
  if (prev.length > 0) next.set(prev);
  next.set(frameVerts, prev.length);
  sequence.vertices = next;

  sequence.frameCount = sequence.time.length;
  return true;
}
