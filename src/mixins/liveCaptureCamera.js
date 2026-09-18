import * as THREE from 'three';

const defaultPose = () => ({
  enabled: false,
  streamVisible: false,
  viewerVisible: true,
  position: { x: 0, y: 1.5, z: 2 },
  rotation: { x: 0, y: 180, z: 0 }
});

// Local +Z is the rear lens direction, +Y is the top of the phone.
export function createCapturePhone() {
  const phone = new THREE.Group();
  phone.name = 'liveCaptureCamera';
  const add = (geometry, color, x = 0, y = 0, z = 0) => {
    const mesh = new THREE.Mesh(geometry, new THREE.MeshPhongMaterial({ color, shininess: 70 }));
    mesh.position.set(x, y, z);
    phone.add(mesh);
    return mesh;
  };
  add(new THREE.BoxGeometry(0.075, 0.15, 0.008), 0x8c929b);
  add(new THREE.BoxGeometry(0.069, 0.142, 0.001), 0x101722, 0, 0, -0.0045);
  const lens = add(new THREE.CylinderGeometry(0.008, 0.008, 0.003, 32), 0x18202c, -0.024, 0.059, 0.0055);
  lens.rotation.x = Math.PI / 2;
  add(new THREE.CircleGeometry(0.005, 32), 0x37668c, -0.024, 0.059, 0.0071);
  return phone;
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
      const rotation = this.normalizeLiveTargetRotation(raw.rotation, 'degrees') ||
        this.normalizeLiveTargetRotation(raw.rotationRadians, 'radians');
      const streamVisible = raw.visible !== false && raw.enabled !== false;
      this.liveCaptureCamera = {
        ...this.liveCaptureCamera,
        streamVisible,
        enabled: streamVisible && this.liveCaptureCamera.viewerVisible !== false,
        ...(position ? { position } : {}),
        ...(rotation ? { rotation } : {})
      };
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
      this.updateLiveCaptureCamera();
    },
    updateLiveCaptureCamera() {
      if (!this.liveCaptureCamera.enabled) {
        this.disposeLiveCaptureCamera();
      } else if (this.scene) {
        if (!this.liveCaptureCameraMesh) this.liveCaptureCameraMesh = createCapturePhone();
        const phone = this.liveCaptureCameraMesh;
        if (phone.parent !== this.scene) this.scene.add(phone);
        const { position, rotation } = this.liveCaptureCamera;
        phone.position.set(position.x, position.y, position.z);
        phone.rotation.set(...['x', 'y', 'z'].map(axis => THREE.Math.degToRad(rotation[axis])), 'XYZ');
      }
      if (this.renderer && this.scene && this.camera) this.renderer.render(this.scene, this.camera);
    }
  }
};
