<template>
  <div class="viewer-container d-flex">
        <div class="viewer flex-grow-1">
            <div v-if="trial" class="d-flex flex-column h-100">
                <div id="mocap" ref="mocap" class="flex-grow-1" />
        <div style="display: flex; flex-wrap: wrap; align-items: center;">
                      <v-text-field label="Time (s)" type="number" :step="0.01" :value="time"
            dark style="flex: 0.1; margin-right: 5px;" @input="onChangeTime"/>
                      <v-slider :value="frame" :min="0" :max="frames.length - 1" @input="onNavigate" hide-details
                          class="mb-2" style="flex: 1;" />
                      </div>
                  </div>
            <div v-else-if="trialLoading" class="flex-grow-1 d-flex align-center justify-center">
                <v-progress-circular indeterminate color="grey" size="30" width="4" />
              </div>
                  </div>
        <div class="right d-flex flex-column">
            <!-- Add recording controls -->
            <div class="recording-controls mb-4">
                              <v-btn
                    v-if="!isRecording"
                    color="red"
                    dark
                    @click="startRecording"
                    :disabled="isRecording"
                    class="mb-2"
                >
                    <v-icon left>mdi-record</v-icon>
                    Record
                              </v-btn>
                              <v-btn
                                  v-else
                    color="grey"
                    dark
                    @click="stopRecording"
                    class="mb-2"
                >
                    <v-icon left>mdi-stop</v-icon>
                    Stop Recording
                  </v-btn>
              </div>
            <!-- Legend -->
            <div class="legend mb-4">
                <div v-for="(animation, index) in animations" :key="index" class="legend-item mb-2">
                    <div class="d-flex align-center mb-2">
                        <div class="color-box" :style="{ backgroundColor: '#' + colors[index].getHexString() }"></div>
                        <div class="ml-2">
                            <div class="trial-name">{{ animation.trialName }}</div>
                            <div class="file-name text-caption">{{ getFileName(animation) }}</div>
          </div>
                  </div>
                    <!-- Offset controls -->
                    <div class="offset-controls mt-1">
                        <v-text-field
                            label="X Offset"
                            type="number"
                            :step="0.5"
                            :value="animation.offset.x"
                            dense
                            @input="updateOffset(index, 'x', $event)"
                            style="width: 100px"
                        />
                        <v-text-field
                            label="Y Offset"
                            type="number"
                            :step="0.5"
                            :value="animation.offset.y"
                            dense
                            @input="updateOffset(index, 'y', $event)"
                            style="width: 100px"
                        />
                        <v-text-field
                            label="Z Offset"
                            type="number"
                            :step="0.5"
                            :value="animation.offset.z"
                            dense
                            @input="updateOffset(index, 'z', $event)"
                            style="width: 100px"
                        />
              </div>
            </div>
        </div>
            <SpeedControl v-model="playSpeed" />
              <VideoNavigation :playing="playing" :value="frame" :maxFrame="frames.length - 1"
                  :disabled="videoControlsDisabled" @play="togglePlay(true)" @pause="togglePlay(false)"
                  @input="onNavigate" class="mb-2" />
          </div>
      </div>
  </template>
  
  <script>
  import axios from 'axios'
  import * as THREE from 'three'
  import * as THREE_OC from '@/orbitControls'
  import VideoNavigation from '@/components/ui/VideoNavigation'
  import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
  import SpeedControl from '@/components/ui/SpeedControl'
  
// Create a new axios instance without a base URL
const axiosInstance = axios.create();
  
  const objLoader = new OBJLoader();
  
  export default {
      name: 'Session',
      components: {
          VideoNavigation,
          SpeedControl
      },
      data() {
          return {
              trial: null,
              frames: [],
              trialLoading: false,
              synced: false,
              camera: null,
              scene: null,
              renderer: null,
              controls: null,
              meshes: {},
              frame: 0,
              time: 0,
              playing: false,
              playSpeed: 1,
              resizeObserver: null,
              animations: [], // Array to store multiple animations
              frameRate: 60,
              lastFrameTime: 0,
              colors: [
                  new THREE.Color(0x00ff00), // Green for first model
                  new THREE.Color(0xff0000)  // Red for second model
              ],
              mediaRecorder: null,
              recordedChunks: [],
              isRecording: false,
              textSprites: {}, // Store text sprites for each animation
              recordingFileName: 'animation-recording.webm', // Add default filename
          }
      },
      computed: {
        videoControlsDisabled() {
          return !this.trial || this.frames.length === 0
    }
      },
    async mounted() {
    this.loadTrial()
    },
    beforeDestroy() {
      if (this.resizeObserver) {
        this.resizeObserver.unobserve(this.$refs.mocap)
      }
      
      // Clean up sprites
      Object.values(this.textSprites).forEach(sprite => {
          if (sprite.material.map) sprite.material.map.dispose();
          if (sprite.material) sprite.material.dispose();
      });
    },
    watch: {
      trial() {
        if (this.trial) {
          this.$nextTick(() => {
            this.resizeObserver = new ResizeObserver(this.onResize)
            this.resizeObserver.observe(this.$refs.mocap)
          })
        } else {
        this.resizeObserver?.unobserve(this.$refs.mocap)
      }
    }
    },
    methods: {
    async loadTrial() {
      console.log('loadTrial started')
        this.time = 0

        if (!this.trialLoading) {
          this.frame = 0
          this.trial = null
          this.synced = false
          this.trialLoading = true
  
          try {
            // Load first JSON file
            console.log('Attempting to load JSON files')
            const res1 = await axiosInstance.get('/test.json')
            console.log('First JSON file loaded')
            
            // Try to load second JSON file if it exists
            let res2 = null
            try {
                res2 = await axiosInstance.get('/test2.json')
                console.log('Second JSON file loaded')
            } catch (error) {
                console.log('No second JSON file found, continuing with single animation')
            }
            
            this.trial = { results: [] }
            this.frames = res1.data.time // Use first animation's time
            this.animations = [
                { 
                    data: res1.data, 
                    offset: new THREE.Vector3(0, 0, 0),
                    fileName: 'test.json',
                    trialName: 'Subject 1'
                }
            ]
            
            // Add second animation if available
            if (res2 && res2.data) {
                this.animations.push({ 
                    data: res2.data, 
                    offset: new THREE.Vector3(0, 0, -1),
                    fileName: 'test2.json',
                    trialName: 'Subject 2'
                })
            }

              this.$nextTick(() => {
                try {
                  console.log('Setting up 3D scene')
                  while (this.$refs.mocap.lastChild) {
                    this.$refs.mocap.removeChild(this.$refs.mocap.lastChild)
                  }
  
                  // setup3d
                  const container = this.$refs.mocap
                  console.log('Container:', container)
  
                  let ratio = container.clientWidth / container.clientHeight
                  this.camera = new THREE.PerspectiveCamera(45, ratio, 0.1, 125)
                  this.camera.position.x = 4.5
                  this.camera.position.z = -3
                  this.camera.position.y = 3
  
                  this.scene = new THREE.Scene()
                  this.scene.background = new THREE.Color(0x808080)
                  this.renderer = new THREE.WebGLRenderer({antialias: true})
                  this.renderer.shadowMap.enabled = true;
                  this.onResize()
                  container.appendChild(this.renderer.domElement)
                  this.controls = new THREE_OC.OrbitControls(this.camera, this.renderer.domElement)
  
                  // add the plane
                  {
                console.log('Adding plane')
                    const planeSize = 5;
  
                    const loader = new THREE.TextureLoader();
                    const texture = loader.load('https://threejsfundamentals.org/threejs/resources/images/checker.png');
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.magFilter = THREE.NearestFilter;
                    const repeats = planeSize * 2;
                    texture.repeat.set(repeats, repeats);
  
                    const planeGeo = new THREE.PlaneGeometry(planeSize, planeSize);
                    const planeMat = new THREE.MeshPhongMaterial({
                      map: texture,
                      side: THREE.DoubleSide,
                    });
                    const mesh = new THREE.Mesh(planeGeo, planeMat);
                    mesh.rotation.x = Math.PI * -.5;
                    mesh.position.y = .0
                    mesh.receiveShadow = true;
                    this.scene.add(mesh);
                  }
  
                  // add sun
                  {
                console.log('Adding lights')
                    const skyColor = 0xB1E1FF;  // light blue
                    const groundColor = 0xB97A20;  // brownish orange
                    const intensity = 0.5
                    const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
                    this.scene.add(light);
                  }
  
                  // add directional light
                  {
                    const color = 0xFFFFFF;
                    const intensity = 0.8;
                    const light = new THREE.DirectionalLight(color, intensity);
                    light.position.set(2, 3, 1.5);
                    light.target.position.set(0, 0, 0);
                    light.castShadow = true;
                    light.shadow.camera.left = -10
                    light.shadow.camera.right = 10
                    light.shadow.camera.top = -10
                    light.shadow.camera.bottom = 10
                    light.shadow.camera.near = 0
                    light.shadow.camera.far = 50
                    light.shadow.camera.zoom = 8
                    this.scene.add(light);
                    this.scene.add(light.target);
                  }
  
                  // Load geometries for each animation
                  this.animations.forEach((animation, index) => {
                      for (let body in animation.data.bodies) {
                          let bd = animation.data.bodies[body]
                    bd.attachedGeometries.forEach((geom) => {
                      let path = 'https://mc-opencap-public.s3.us-west-2.amazonaws.com/geometries/' + geom.substr(0, geom.length - 4) + ".obj";
                              console.log('Loading geometry from:', path)
                      objLoader.load(path, (root) => {
                        root.castShadow = true;
                        root.receiveShadow = true;
                                  
                                  // Apply color to all meshes in the geometry
                                  root.traverse((child) => {
                          if (child instanceof THREE.Mesh) {
                            child.castShadow = true;
                                          child.material = new THREE.MeshPhongMaterial({ 
                                              color: this.colors[index],
                                              transparent: true,
                                              opacity: 0.8 // Slight transparency to better distinguish overlapping parts
                                          });
                                      }
                                  });
                                  
                                  // Store with unique key for each animation
                                  const meshKey = `anim${index}_${body}${geom}`;
                                  this.meshes[meshKey] = root;
                                  this.meshes[meshKey].scale.set(bd.scaleFactors[0], bd.scaleFactors[1], bd.scaleFactors[2]);
                                  
                                  // Apply initial offset
                                  root.position.add(animation.offset);
                                  
                        this.scene.add(root);
                                  console.log('Added geometry to scene:', meshKey);
                              });
                          });
                  }
                  });

                  // Create text sprites for each animation
                  this.animations.forEach((animation, index) => {
                      const canvas = document.createElement('canvas');
                      const context = canvas.getContext('2d');
                      canvas.width = 256;
                      canvas.height = 64;
                      
                      // Set text style
                      context.font = 'bold 40px Arial';
                      context.textAlign = 'center';
                      context.fillStyle = '#' + this.colors[index].getHexString();
                      
                      // Draw text
                      context.fillText(animation.trialName, canvas.width/2, canvas.height/2);
                      
                      // Create sprite
                      const texture = new THREE.CanvasTexture(canvas);
                      const spriteMaterial = new THREE.SpriteMaterial({ 
                          map: texture,
                          transparent: true,
                          opacity: 0.4
                      });
                      
                      const sprite = new THREE.Sprite(spriteMaterial);
                      sprite.scale.set(1, 0.25, 1); // Adjust size
                      
                      // Position sprite above model
                      sprite.position.copy(animation.offset);
                      sprite.position.y += 2; // Position above the model
                      
                      this.textSprites[`text_${index}`] = sprite;
                      this.scene.add(sprite);
                  });

                  // Initial render
                  this.renderer.render(this.scene, this.camera);
                } finally {
                  this.trialLoading = false
                }
  
                this.onResize()
  
                function delay(time) {
                  return new Promise(resolve => setTimeout(resolve, time));
                }

                let timeout = 2000
                if (navigator.connection) {
                  console.log('supported: connection', navigator.connection.downlink)
                  timeout = Math.trunc(10000 / navigator.connection.downlink)
                }

                delay(timeout).then(() => {
                  this.togglePlay(true)
                });
              })
          } catch (error) {
          console.error('Error loading trial:', error)
            this.trialLoading = false
          }
        }
      },
      onResize() {
        const container = this.$refs.mocap
        if (container && this.renderer) {
          this.renderer.setSize(container.clientWidth, container.clientHeight)
        }
  
        if (this.renderer) {
          const canvas = this.renderer.domElement;
          this.camera.aspect = canvas.clientWidth / canvas.clientHeight;
          this.camera.updateProjectionMatrix();
        }
      },
      animate() {
        if (!this.trialLoading) {
          requestAnimationFrame(this.animate)
          
          // Calculate time since last frame
          const currentTime = performance.now();
          const deltaTime = (currentTime - this.lastFrameTime) / 1000; // Convert to seconds
          
          if (deltaTime >= (1 / this.frameRate)) { // Only update if enough time has passed
            this.lastFrameTime = currentTime;
          this.animateOneFrame()
          }
        }
      },
      animateOneFrame() {
          let cframe = this.frame
  
          if (cframe < this.frames.length) {
              // Update each animation
              this.animations.forEach((animation, animIndex) => {
                  let json = animation.data;
            for (let body in json.bodies) {
              json.bodies[body].attachedGeometries.forEach((geom) => {
                          const meshKey = `anim${animIndex}_${body}${geom}`;
                          if (this.meshes[meshKey]) {
                              // Get base position from animation data
                              const position = new THREE.Vector3(
                      json.bodies[body].translation[cframe][0],
                      json.bodies[body].translation[cframe][1],
                                  json.bodies[body].translation[cframe][2]
                              );
                              
                              // Add animation offset
                              position.add(animation.offset);
                              
                              // Set final position
                              this.meshes[meshKey].position.copy(position);
                              
                              // Set rotation
                  var euler = new THREE.Euler(
                      json.bodies[body].rotation[cframe][0],
                      json.bodies[body].rotation[cframe][1],
                                  json.bodies[body].rotation[cframe][2]
                              );
                              this.meshes[meshKey].quaternion.setFromEuler(euler);
                          }
                      });
                  }
              });
          }
  
          this.renderer.render(this.scene, this.camera);

          if (this.playing) {
              this.frame = (this.frame + 1) % this.frames.length;
              this.time = this.frame / this.frameRate;
          }
      },
      togglePlay(value) {
        this.playing = value
        if (this.playing) {
          this.lastFrameTime = performance.now() // Reset timing when starting playback
          this.animate()
        } else if (this.isRecording) {
          this.playing = true;
        }
      },
      onNavigate(frame) {
      this.frame = frame
      this.time = frame / this.frameRate
        this.animateOneFrame()
      },
      onChangeTime(time) {
      this.time = time
      this.frame = Math.floor(time * this.frameRate)
        this.animateOneFrame()
      },
    getFileName(animation) {
        // Extract filename from the URL used to load the animation
        return animation.fileName || 'Animation'
    },
    updateOffset(animationIndex, axis, value) {
        const offset = this.animations[animationIndex].offset
        offset[axis] = Number(value)
        
        // Update all meshes for this animation
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${animationIndex}_`)) {
                const mesh = this.meshes[key]
                // Reset position to remove old offset
                mesh.position.sub(new THREE.Vector3().copy(offset))
                // Apply new offset
                mesh.position.add(offset)
            }
        })
        
        // Update sprite position
        const sprite = this.textSprites[`text_${animationIndex}`];
        if (sprite) {
            sprite.position.copy(offset);
            sprite.position.y += 2; // Keep it above the model
        }
        
        // Render the scene with updated positions
        this.renderer.render(this.scene, this.camera)
    },
    startRecording() {
      if (!this.renderer) return;
      
      const canvas = this.renderer.domElement;
      const stream = canvas.captureStream(this.frameRate); // Capture at our animation frame rate
      
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 5000000 // 5 Mbps for good quality
      });
      
      this.recordedChunks = [];
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };
      
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        document.body.appendChild(a);
        a.style = 'display: none';
        a.href = url;
        a.download = this.recordingFileName;
        a.click();
        window.URL.revokeObjectURL(url);
        this.recordedChunks = [];
      };
      
      // Start recording
      this.mediaRecorder.start();
      this.isRecording = true;
      
      // If not already playing, start playback
      if (!this.playing) {
        this.togglePlay(true);
      }
    },
    stopRecording() {
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
        this.isRecording = false;
      }
    }
    }
  }
  </script>
  
  <style lang="scss">
.viewer-container {
  height: 100vh;
  
    .viewer {
      height: 100%;
  
      #mocap {
        width: 100%;
        overflow: hidden;
  
        canvas {
          width: 100% !important;
        }
      }
    }
  
    .right {
      flex: 0 0 200px;
      height: 100%;
      padding: 10px;

      .recording-controls {
        text-align: center;
        
        .v-btn {
          width: 100%;
        }
      }

      .legend {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
        padding: 10px;

        .legend-item {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          padding: 5px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);

          &:last-child {
            border-bottom: none;
          }

          .color-box {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            display: inline-block;
            vertical-align: middle;
          }

          .trial-name {
            font-weight: bold;
            font-size: 14px;
          }

          .file-name {
            opacity: 0.7;
            font-size: 12px;
          }

          .offset-controls {
            display: flex;
            gap: 10px;
            width: 100%;
            flex-wrap: wrap; // Allow controls to wrap on narrow screens
          }
        }
      }
    }
  }
  </style>
  
  