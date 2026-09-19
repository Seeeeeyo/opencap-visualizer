import * as THREE from 'three';

const defaultPose = () => ({
  enabled: false,
  streamVisible: false,
  viewerVisible: true,
  position: { x: 0, y: 1.5, z: 2 },
  rotation: { x: 0, y: 180, z: 0 },
  quaternion: null
});

// Local +Z is the rear lens direction, +Y is the top of the phone.
// Dimensions match iPhone 12: 71.5 × 146.7 × 7.4 mm.
export function createCapturePhone() {
  const phone = new THREE.Group();
  phone.name = 'liveCaptureCamera';
  const W = 0.0715;
  const H = 0.1467;
  const D = 0.0074;
  const add = (geometry, color, x = 0, y = 0, z = 0) => {
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshPhongMaterial({ color, shininess: 70 })
    );
    mesh.position.set(x, y, z);
    phone.add(mesh);
    return mesh;
  };
  add(new THREE.BoxGeometry(W, H, D), 0x8c929b);
  add(new THREE.BoxGeometry(W - 0.006, H - 0.008, 0.001), 0x101722, 0, 0, -D * 0.55);
  const lensR = 0.008;
  const lens = add(
    new THREE.CylinderGeometry(lensR, lensR, 0.003, 32),
    0x18202c,
    -W * 0.28,
    H * 0.34,
    D * 0.55
  );
  lens.rotation.x = Math.PI / 2;
  add(
    new THREE.CircleGeometry(lensR * 0.62, 32),
    0x37668c,
    -W * 0.28,
    H * 0.34,
    D * 0.55 + 0.0016
  );
  return phone;
}

function normalizeQuaternion(value) {
  if (Array.isArray(value) && value.length >= 4) {
    const q = value.slice(0, 4).map(Number);
    return q.every(Number.isFinite) ? { x: q[0], y: q[1], z: q[2], w: q[3] } : null;
  }
  if (value && typeof value === 'object') {
    const x = Number(value.x);
    const y = Number(value.y);
    const z = Number(value.z);
    const w = Number(value.w);
    return [x, y, z, w].every(Number.isFinite) ? { x, y, z, w } : null;
  }
  return null;
}

function roundCaptureNumber(value, digits) {
  const num = Number(value);
  if (!Number.isFinite(num)) return value;
  const scale = 10 ** digits;
  return Math.round(num * scale) / scale;
}

function roundCaptureVec3(vec, digits) {
  if (!vec || typeof vec !== 'object') return vec;
  return {
    x: roundCaptureNumber(vec.x, digits),
    y: roundCaptureNumber(vec.y, digits),
    z: roundCaptureNumber(vec.z, digits)
  };
}

export default {
  data() {
    return { liveCaptureCamera: defaultPose(), liveCaptureCameraMesh: null };
  },
  methods: {
    disposeLiveCaptureCamera() {
      const phone = this.liveCaptureCameraMesh;
      if (!phone) return;
      if (phone.parent) phone.parent.remove(phone);
      phone.traverse(part => {
        if (part.geometry) part.geometry.dispose();
        if (part.material) part.material.dispose();
      });
      this.liveCaptureCameraMesh = null;
    },
    resetLiveCaptureCamera() {
      this.disposeLiveCaptureCamera();
      this.liveCaptureCamera = defaultPose();
    },
    setLiveCaptureCameraVisibility() {
      this.$set(
        this.liveCaptureCamera,
        'enabled',
        this.liveCaptureCamera.streamVisible !== false && this.liveCaptureCamera.viewerVisible !== false
      );
    },
    handleLiveCaptureCamera(raw) {
      if (raw === null || raw === false) raw = { visible: false };
      if (!raw || typeof raw !== 'object') return;
      const position = this.normalizeLiveTargetPosition(raw.position);
      const quaternion = normalizeQuaternion(raw.quaternion || raw.quat);
      const rotation = this.normalizeLiveTargetRotation(raw.rotation, 'degrees') ||
        this.normalizeLiveTargetRotation(raw.rotationRadians, 'radians');
      const streamVisible = raw.visible !== false && raw.enabled !== false;
      // Keep the same object identity so Vue 2 v-model on nested fields stays live.
      this.$set(this.liveCaptureCamera, 'streamVisible', streamVisible);
      this.setLiveCaptureCameraVisibility();
      if (position) this.$set(this.liveCaptureCamera, 'position', roundCaptureVec3(position, 3));
      if (quaternion) {
        this.$set(this.liveCaptureCamera, 'quaternion', quaternion);
        // Keep the UI euler fields in sync when possible.
        if (!rotation) {
          const e = new THREE.Euler().setFromQuaternion(
            new THREE.Quaternion(quaternion.x, quaternion.y, quaternion.z, quaternion.w),
            'XYZ'
          );
          this.$set(this.liveCaptureCamera, 'rotation', roundCaptureVec3({
            x: THREE.Math.radToDeg(e.x),
            y: THREE.Math.radToDeg(e.y),
            z: THREE.Math.radToDeg(e.z)
          }, 1));
        }
      } else if (rotation) {
        this.$set(this.liveCaptureCamera, 'quaternion', null);
      }
      if (rotation) this.$set(this.liveCaptureCamera, 'rotation', roundCaptureVec3(rotation, 1));
      this.updateLiveCaptureCamera();
    },
    onLiveCaptureCameraEnabledChange(value) {
      this.$set(this.liveCaptureCamera, 'viewerVisible', value === true);
      if (value === true && this.liveCaptureCamera.streamVisible === false) {
        this.$set(this.liveCaptureCamera, 'streamVisible', true);
      }
      this.setLiveCaptureCameraVisibility();
      this.updateLiveCaptureCamera();
    },
    onLiveCaptureCameraInput(field, axis, value) {
      if (value === '' || !Number.isFinite(Number(value))) return;
      this.$set(this.liveCaptureCamera[field], axis, Number(value));
      // Manual UI edits are Euler-based.
      this.$set(this.liveCaptureCamera, 'quaternion', null);
      this.updateLiveCaptureCamera();
    },
    updateLiveCaptureCamera() {
      if (!this.liveCaptureCamera.enabled) {
        this.disposeLiveCaptureCamera();
      } else if (this.scene) {
        if (!this.liveCaptureCameraMesh) {
          this.liveCaptureCameraMesh = createCapturePhone();
        }
        const phone = this.liveCaptureCameraMesh;
        if (phone.parent !== this.scene) this.scene.add(phone);
        const { position, rotation, quaternion } = this.liveCaptureCamera;
        phone.position.set(position.x, position.y, position.z);
        // Prefer quaternion: phone look is often near ±X after Ry90, which is an
        // XYZ-Euler singularity and made landscape roll tip into the floor.
        if (quaternion) {
          phone.quaternion.set(quaternion.x, quaternion.y, quaternion.z, quaternion.w);
        } else {
          phone.rotation.order = 'XYZ';
          phone.rotation.set(
            THREE.Math.degToRad(rotation.x),
            THREE.Math.degToRad(rotation.y),
            THREE.Math.degToRad(rotation.z)
          );
        }
      }
      if (this.renderer && this.scene && this.camera) this.renderer.render(this.scene, this.camera);
    }
  }
};
