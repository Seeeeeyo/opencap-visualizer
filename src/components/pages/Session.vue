<template>
    <div class="viewer-container d-flex">
      <div class="viewer flex-grow-1" @dragover.prevent @drop.prevent="handleDrop">
        <div v-if="trial" class="d-flex flex-column h-100">
          <div id="mocap" ref="mocap" class="flex-grow-1" />
          <div class="controls-container" style="display: flex; align-items: center; padding: 0 10px;">
            <!-- Video controls on the left -->
            <VideoNavigation 
              :playing="playing" 
              :value="frame" 
              :maxFrame="frames.length - 1" 
              :disabled="videoControlsDisabled" 
              @play="togglePlay(true)" 
              @pause="togglePlay(false)" 
              @input="onNavigate" 
              class="mr-3" 
            />
            <!-- Playback speed control -->
            <div class="mr-3">
              <SpeedControl v-model="playSpeed" />
            </div>
            <!-- Time and slider on the right -->
            <div style="flex: 1; display: flex; flex-wrap: wrap; align-items: center;">
              <v-text-field label="Time (s)" type="number" :step="0.01" :value="formattedTime" dark style="flex: 0.1; min-width: 80px; margin-right: 5px;" @input="onChangeTime" />
              <v-slider :value="frame" :min="0" :max="frames.length - 1" @input="onNavigate" hide-details class="mb-2" style="flex: 1;" />
            </div>
          </div>
        </div>
        <div v-else-if="trialLoading" class="flex-grow-1 d-flex align-center justify-center">
          <v-progress-circular indeterminate color="grey" size="30" width="4" />
        </div>
        <div v-else class="flex-grow-1 d-flex flex-column align-center justify-center">
          <!-- Loading overlay -->
          <div v-if="converting" class="conversion-overlay">
            <v-progress-circular indeterminate color="indigo" size="64" width="6" />
            <div class="mt-4 text-h6 text-center">
              Converting OpenSim Files<br>
              <span class="text-subtitle-1">This may take a moment...</span>
            </div>
          </div>
          
          <!-- Display API error message if it exists -->
          <div v-if="conversionError" class="text-center my-3">
            <v-alert type="error" dense dismissible @input="clearConversionError" prominent>
              <div class="d-flex align-center">
                <v-icon class="mr-2">mdi-alert-circle</v-icon>
                <div>
                  <div class="font-weight-bold mb-1">Conversion Error</div>
                  <div>{{ conversionError }}</div>
                </div>
              </div>
            </v-alert>
          </div>
          
          <div class="text-center drop-zone" :class="{ 'opacity-reduced': converting }">
            <!-- Existing drop zone content -->
            <v-icon size="64" color="grey darken-1">mdi-file-upload-outline</v-icon>
            
            <!-- Show selected files if any, otherwise show the default prompt -->
            <div v-if="osimFile || motFile" class="text-h6 grey--text text--darken-1 mt-4">
              <div v-if="osimFile" class="selected-file mb-2">
                <v-chip small color="indigo" dark>{{ osimFile.name }}</v-chip>
              </div>
              <div v-if="motFile" class="selected-file mb-2">
                <v-chip small color="indigo" dark>{{ motFile.name }}</v-chip>
              </div>
              <div v-if="osimFile && !motFile" class="missing-file-prompt">
                Please add a .mot file to complete the pair
              </div>
              <div v-if="!osimFile && motFile" class="missing-file-prompt">
                Please add an .osim file to complete the pair
              </div>
            </div>
            <div v-else class="text-h6 grey--text text--darken-1 mt-4">
              Drag & drop files here<br>
              .json, or .osim + .mot files accepted
            </div>
          </div>
          
          <v-btn color="grey darken-3" dark class="mt-6" @click="loadSampleFiles" :disabled="converting">
            <v-icon left>mdi-play-circle</v-icon>
            Try with Sample Files
          </v-btn>
        </div>
      </div>
      <div class="right d-flex flex-column">
        <!-- Add recording controls -->
        <div class="recording-controls mb-4">
          <!-- Control buttons row -->
          <div class="d-flex align-center mb-2">
            <v-btn v-if="!isRecording" color="red" dark @click="startRecording" :disabled="isRecording" class="mr-2" style="flex: 2;">
              <v-icon left>mdi-record</v-icon>
              Record
            </v-btn>
            <v-btn v-else color="grey" dark @click="stopRecording" class="mr-2" style="flex: 2;">
              <v-icon left>mdi-stop</v-icon>
              Stop
            </v-btn>
            
            <v-select
              v-model="recordingFormat"
              :items="[{text: 'WebM', value: 'webm'}, {text: 'MP4', value: 'mp4'}]"
              label="Format"
              dense
              dark
              class="format-selector mr-2"
              hide-details
              :disabled="isRecording"
              style="flex: 1; min-width: 70px;"
            ></v-select>
            
            <v-select
              v-model="videoBitrate"
              :items="[
                {text: '2 Mbps', value: 2000000},
                {text: '5 Mbps', value: 5000000},
                {text: '8 Mbps', value: 8000000},
                {text: '12 Mbps', value: 12000000},
                {text: '15 Mbps', value: 15000000},
                {text: '20 Mbps', value: 20000000}
              ]"
              label="Bitrate"
              dense
              dark
              hide-details
              :disabled="isRecording"
              style="flex: 1; min-width: 90px;"
            ></v-select>
            
            <!-- Add info icon with tooltip -->
            <v-tooltip bottom max-width="300">
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  icon
                  x-small
                  v-bind="attrs"
                  v-on="on"
                  class="ml-1 mt-1"
                  color="grey lighten-1"
                >
                  <v-icon x-small>mdi-information-outline</v-icon>
                </v-btn>
              </template>
              <div class="pa-2">
                <p class="mb-1"><strong>For best recording quality:</strong></p>
                <ul class="pl-4 mb-0">
                  <li class="text-left">Maximize your browser window and the application view before recording</li>
                  <li class="text-left">Use WebM format with VP9 codec for better quality than MP4 at the same bitrate</li>
                </ul>
              </div>
            </v-tooltip>
          </div>
          
          <!-- Add capture button row -->
          <div class="d-flex align-center mb-2">
            <v-btn color="teal" dark @click="captureScreenshot" style="flex: 3;" class="mr-2">
              <v-icon left>mdi-camera</v-icon>
              Capture Image
            </v-btn>
            
            <v-select
              v-model="captureMode"
              :items="[
                {text: 'Both Types', value: 'both'},
                {text: 'Normal', value: 'normal'},
                {text: 'Transparent', value: 'transparent'}
              ]"
              label="Background"
              dense
              dark
              class="format-selector"
              hide-details
              style="flex: 1; max-width: 120px;"
            ></v-select>
          </div>
        </div>
        <!-- Add file controls -->
        <div class="file-controls mb-4 position-relative">
          <!-- Show loading overlay when converting -->
          <div v-if="converting" class="conversion-overlay-small">
            <v-progress-circular indeterminate color="indigo" size="24" width="3" />
            <div class="ml-2">Converting files...</div>
          </div>
          
          <!-- Make controls slightly transparent when loading -->
          <div :class="{ 'opacity-reduced': converting }">
            <!-- Existing file inputs and buttons -->
            <input type="file" ref="fileInput" accept=".json" style="display: none" @change="handleFileUpload" multiple />
            <v-btn color="grey darken-3" class="mb-2 white--text" block @click="$refs.fileInput.click()" :disabled="converting">
              <v-icon left>mdi-file-upload</v-icon>
              Load JSON Files
            </v-btn>
            
            <input type="file" ref="osimMotFileInput" accept=".osim,.mot" style="display: none" @change="handleOpenSimFiles" multiple />
            <v-btn color="indigo darken-1" class="mb-2 white--text" block @click="$refs.osimMotFileInput.click()" :disabled="converting">
              <v-icon left>mdi-file-upload-outline</v-icon>
              Load OpenSim (.mot+.osim)
            </v-btn>
            
            <!-- Existing file chips etc. -->
          </div>
        </div>
        <!-- Add sync controls -->
        <div class="sync-controls mb-4">
          <v-btn color="grey darken-3" class="mb-2 white--text" block @click="syncAllAnimations">
            <v-icon left>mdi-sync</v-icon>
            Sync All Subjects
          </v-btn>
        </div>
        <!-- Add scene color controls -->
        <div class="scene-controls mb-4">
          <div class="d-flex align-center mb-2">
            <div class="mr-4 d-flex align-center">
              <div class="mr-2">Background:</div>
              <v-menu offset-y>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn small v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: backgroundColor }"></v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex flex-wrap">
                    <v-btn v-for="color in backgroundColors" :key="color" small icon class="ma-1" @click="updateBackgroundColor(color)">
                      <div class="color-sample" :style="{ backgroundColor: color }"></div>
                    </v-btn>
                  </div>
                </v-card>
              </v-menu>
            </div>
            <div class="d-flex align-center">
              <div class="mr-2">Ground:</div>
              <v-menu offset-y>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn small v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: showGround ? groundColor : 'transparent', border: !showGround ? '1px dashed rgba(255,255,255,0.5)' : '1px solid rgba(255,255,255,0.3)' }"></v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex flex-wrap">
                    <v-btn v-for="color in groundColors" :key="color" small icon class="ma-1" @click="updateGroundColor(color)" :disabled="!showGround">
                      <div class="color-sample" :style="{ backgroundColor: color }"></div>
                    </v-btn>
                  </div>
                  <div class="mt-2 text-center">
                    <v-btn small text @click="toggleGroundVisibility">
                      {{ showGround ? 'Hide Ground' : 'Show Ground' }}
                    </v-btn>
                    <v-btn small text @click="toggleGroundTexture" :disabled="!showGround">
                      {{ useGroundTexture ? 'Remove Texture' : 'Use Texture' }}
                    </v-btn>
                    <v-btn small text @click="toggleCheckerboard" :disabled="!showGround || !useGroundTexture">
                      {{ useCheckerboard ? 'Use Grid' : 'Use Checkerboard' }}
                    </v-btn>
                  </div>
                </v-card>
              </v-menu>
            </div>
          </div>
        </div>
        <!-- Add Timelapse Controls -->
        <div class="timelapse-controls mb-4">
          <v-switch
            v-model="timelapseMode"
            label="Timelapse Mode"
            color="indigo"
            @change="toggleTimelapseMode"
          ></v-switch>
          <div v-if="timelapseMode" class="mt-2">
            <v-slider
              v-model="timelapseInterval"
              label="Frame Interval"
              min="1"
              max="30"
              step="1"
              thumb-label
              :disabled="!timelapseMode"
              @input="updateTimelapse"
            ></v-slider>
            <v-slider
              v-model="timelapseOpacity"
              label="Model Transparency"
              min="0"
              max="1"
              step="0.05"
              thumb-label
              :disabled="!timelapseMode"
              @input="updateTimelapseOpacity"
            ></v-slider>
            <div class="d-flex justify-space-between align-center">
              <v-btn small text @click="clearTimelapse" class="mt-1">
                Clear All
              </v-btn>
              <v-btn small text @click="showTimelapseManager = true" class="mt-1">
                Manage Models
              </v-btn>
            </div>
          </div>

          <!-- Add Timelapse Manager Dialog -->
          <v-dialog v-model="showTimelapseManager" max-width="500">
            <v-card>
              <v-card-title>Manage Timelapse Models</v-card-title>
              <v-card-text>
                <div v-for="(group, animIndex) in timelapseGroups" :key="animIndex" class="mb-4">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <div class="subtitle-1">{{ animations[animIndex]?.trialName || `Subject ${animIndex + 1}` }}</div>
                    <v-btn small text color="error" @click="deleteTimelapseGroup(animIndex)">
                      Delete All
                    </v-btn>
                  </div>
                  <v-list dense>
                    <v-list-item v-for="frame in group" :key="frame" class="mb-1">
                      <v-list-item-content>
                        <v-list-item-title>
                          Frame {{ frame }}
                          <span class="text-caption grey--text ml-2">
                            (Mesh ID: {{ getMeshIdForFrame(animIndex, frame) }})
                          </span>
                        </v-list-item-title>
                      </v-list-item-content>
                      <v-list-item-action>
                        <v-btn small icon color="error" @click="deleteTimelapseFrame(animIndex, frame)">
                          <v-icon small>mdi-delete</v-icon>
                        </v-btn>
                      </v-list-item-action>
                    </v-list-item>
                  </v-list>
                </div>
                <div v-if="Object.keys(timelapseGroups).length === 0" class="text-center grey--text">
                  No timelapse models created yet
                </div>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text @click="showTimelapseManager = false">Close</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </div>
        <!-- Legend -->
        <div class="legend mb-4">
          <div v-for="(animation, index) in animations" :key="index" class="legend-item mb-2">
            <div class="d-flex align-center mb-2">
              <div class="color-box" :style="{ backgroundColor: '#' + colors[index].getHexString() }"></div>
              <div class="ml-2 flex-grow-1">
                <v-text-field v-model="animation.trialName" dense hide-details class="trial-name-input" />
                <div class="file-name text-caption">{{ getFileName(animation) }}</div>
              </div>
              <v-menu offset-y :close-on-content-click="false">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn icon small v-bind="attrs" v-on="on" class="ml-2">
                    <v-icon small>mdi-palette</v-icon>
                  </v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex flex-wrap">
                    <v-btn v-for="color in availableColors" :key="color" small icon class="ma-1" @click="updateSubjectColor(index, color)">
                      <div class="color-sample" :style="{ backgroundColor: color }"></div>
                    </v-btn>
                  </div>
                  <div class="mt-2 text-center">
                    <v-btn small text @click.stop="showRgbPicker = !showRgbPicker">
                      {{ showRgbPicker ? 'Use Preset Colors' : 'Use RGB Picker' }}
                    </v-btn>
                  </div>
                  <div v-if="showRgbPicker" class="rgb-picker mt-2" @click.stop>
                    <v-slider
                      v-model="rgbValues[index].r"
                      :min="0"
                      :max="255"
                      label="Red"
                      hide-details
                      @input="updateRgbColor(index)"
                      @click.stop
                    ></v-slider>
                    <v-slider
                      v-model="rgbValues[index].g"
                      :min="0"
                      :max="255"
                      label="Green"
                      hide-details
                      @input="updateRgbColor(index)"
                      @click.stop
                    ></v-slider>
                    <v-slider
                      v-model="rgbValues[index].b"
                      :min="0"
                      :max="255"
                      label="Blue"
                      hide-details
                      @input="updateRgbColor(index)"
                      @click.stop
                    ></v-slider>
                    <div class="d-flex justify-center mt-2">
                      <div class="color-preview" :style="{ backgroundColor: `rgb(${rgbValues[index].r}, ${rgbValues[index].g}, ${rgbValues[index].b})` }"></div>
                    </div>
                  </div>
                </v-card>
              </v-menu>
              <v-btn icon small class="ml-2" @click="deleteSubject(index)">
                <v-icon small color="error">mdi-delete</v-icon>
              </v-btn>
              <!-- Add visibility toggle button -->
              <v-btn icon small class="ml-2" @click="toggleSubjectVisibility(index)">
                <v-icon small :color="animations[index].visible ? 'white' : 'grey'">
                  {{ animations[index].visible ? 'mdi-eye' : 'mdi-eye-off' }}
                </v-icon>
              </v-btn>
              <!-- Add transparency button -->
              <v-menu offset-y>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn icon small v-bind="attrs" v-on="on" class="ml-2" @click="prepareTransparencyMenu(index)">
                    <v-icon small>mdi-opacity</v-icon>
                  </v-btn>
                </template>
                <v-card class="transparency-picker pa-3" width="250">
                  <div class="text-subtitle-2 mb-2">Transparency</div>
                  <v-slider v-model="alphaValues[index]" :min="0" :max="1" step="0.01" hide-details @input="updateAlpha(index, $event)">
                    <template v-slot:prepend>
                      <div class="text-caption grey--text">0%</div>
                    </template>
                    <template v-slot:append>
                      <div class="text-caption grey--text">100%</div>
                    </template>
                  </v-slider>
                </v-card>
              </v-menu>
            </div>
            <!-- Offset controls -->
            <div class="offset-controls mt-1">
              <div class="d-flex align-center">
                <v-text-field label="X" type="number" :step="0.5" :value="animation.offset.x" dense @input="updateOffset(index, 'x', $event)" style="width: 70px" />
                <v-text-field label="Y" type="number" :step="0.5" :value="animation.offset.y" dense @input="updateOffset(index, 'y', $event)" style="width: 70px" />
                <v-text-field label="Z" type="number" :step="0.5" :value="animation.offset.z" dense @input="updateOffset(index, 'z', $event)" style="width: 70px" />
              </div>
            </div>
            
            <!-- Individual Mesh Controls -->
            <div class="mesh-controls mt-1" v-if="animations[index].visible">
              <v-expansion-panels>
                <v-expansion-panel>
                  <v-expansion-panel-header>
                    <div class="text-subtitle-2">Mesh Objects</div>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <div class="mesh-groups">
                      <div v-for="(items, groupName) in getGroupedMeshes(index)" :key="groupName" class="mb-3">
                        <div class="group-header pa-1 mb-1 d-flex align-center">
                          <v-btn icon small class="mr-2" @click="toggleGroupVisibility(index, groupName, items)">
                            <v-icon small>{{ isGroupVisible(items) ? 'mdi-eye' : 'mdi-eye-off' }}</v-icon>
                          </v-btn>
                          <strong class="text-subtitle-2">{{ groupName }}</strong>
                        </div>
                        <div v-for="item in items" :key="item.key" class="d-flex align-center pa-1 pl-3">
                          <v-btn icon x-small @click="toggleMeshVisibility(item.key)">
                            <v-icon x-small :color="meshes[item.key] && meshes[item.key].visible !== false ? 'white' : 'grey'">
                              {{ meshes[item.key] && meshes[item.key].visible !== false ? 'mdi-eye' : 'mdi-eye-off' }}
                            </v-icon>
                          </v-btn>
                          <span class="ml-2 text-caption">{{ item.name }}</span>
                        </div>
                      </div>
                    </div>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </div>
        </div>
        <!-- Add credits at the bottom -->
        <div class="credits mt-auto pt-2 text-center">
          <div class="text-caption grey--text text--lighten-1">
            Developed by <a href="https://www.linkedin.com/in/selim-gilon/" target="_blank" class="text-decoration-none">Selim Gilon</a><br>
            Based on OpenCap<br>
            <span class="text-caption grey--text text--darken-1">© 2025 PhD Research</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import * as THREE from 'three'
  import * as THREE_OC from '@/orbitControls'
  import VideoNavigation from '@/components/ui/VideoNavigation'
  import SpeedControl from '@/components/ui/SpeedControl'
  import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
  import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
  import { apiError } from '@/util/ErrorMessage.js';
  
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
              resizeObserver: null,
              animations: [], // Array to store multiple animations
              frameRate: 60,
              lastFrameTime: 0,
              playSpeed: 1, // Playback speed multiplier
              colors: [
                  new THREE.Color(0x00ff00),  // Green (first subject)
                  new THREE.Color(0xff8000),  // Orange (second subject)
                  new THREE.Color(0xff0000),  // Red (third subject)
                  new THREE.Color(0x0000ff),  // Blue
                  new THREE.Color(0xffff00),  // Yellow
                  new THREE.Color(0xff00ff),  // Magenta
                  new THREE.Color(0x00ffff),  // Cyan
                  new THREE.Color(0x8000ff),  // Purple
              ],
              mediaRecorder: null,
              recordedChunks: [],
              isRecording: false,
              textSprites: {}, // Store text sprites for each animation
              recordingFileName: 'animation-recording.webm', // Add default filename
              recordingFormat: 'webm', // Default recording format
              availableColors: [
                  'original',  // Change 'transparent' to 'original'
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
              ],
              backgroundColors: [
                  '#000000',
                  '#1a1a1a',
                  '#333333',
                  '#4d4d4d',
                  '#666666',
                  '#808080',
                  '#999999',
                  '#b3b3b3',
                  '#cccccc',
                  '#e6e6e6',
                  '#ffffff',
              ],
              groundColors: [
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
              ],
              backgroundColor: '#808080',
              groundColor: '#cccccc',
              useGroundTexture: true,
              groundMesh: null,
              groundTexture: null,
              useCheckerboard: true,
              gridTexture: null,
              showGround: true,
              alphaValues: [], // Array to store alpha values for each animation
              osimFile: null,
              motFile: null,
              converting: false,
              // apiUrl: 'http://localhost:8000/convert-opensim-to-visualizer-json',
              apiUrl: 'https://opensim-to-visualizer-api.onrender.com/convert-opensim-to-visualizer-json',
              showRgbPicker: false,
              rgbValues: [],
              // Add new timelapse properties
              timelapseMode: false,
              timelapseInterval: 5,
              timelapseMeshes: {}, // Store timelapse meshes
              timelapseFrameCount: 0, // Track number of frames in timelapse
              timelapseOpacity: 0.3, // Default opacity for timelapse models
              showTimelapseManager: false,
              timelapseGroups: {}, // Organized by animation index and frame numbers
              timelapseCounter: null, // Use sequential counter for mesh IDs
              captureMode: 'both', // Options: 'both', 'normal', 'transparent'
              videoBitrate: 5000000, // Video recording bitrate in bits per second (5 Mbps default)
              conversionError: null, // Add this line to store API error message
          }
      },
      computed: {
        videoControlsDisabled() {
          return !this.trial || this.frames.length === 0
        },
        formattedTime() {
          // Round time to 2 decimal places for display
          return parseFloat(this.time).toFixed(2);
        }
      },
    async mounted() {
        console.log('Session component mounted');
        console.log('Current route:', this.$route.path);
        this.initScene();
        // Check if we're on the samples route when component is mounted
        if (this.$route.path === '/samples' || this.$route.path === '/samples/') {
            console.log('Loading sample files from mounted hook');
            this.loadSampleFiles();
        }
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
      },
      animations: {
        handler(newAnimations) {
          newAnimations.forEach((animation, index) => {
            const sprite = this.textSprites[`text_${index}`];
            if (sprite) {
              const canvas = document.createElement('canvas');
              const context = canvas.getContext('2d');
              canvas.width = 256;
              canvas.height = 64;
              
              context.font = 'bold 40px Arial';
              context.textAlign = 'center';
              context.fillStyle = '#' + this.colors[index].getHexString();
              context.fillText(animation.trialName, canvas.width/2, canvas.height/2);
              
              const texture = new THREE.CanvasTexture(canvas);
              if (sprite.material.map) sprite.material.map.dispose();
              sprite.material.map = texture;
              sprite.material.needsUpdate = true;
            }
          });
          
          // Render the scene with updated text
          if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
          }
        },
        deep: true
      },
      osimFile: {
        handler(newVal) {
          if (newVal && this.motFile && !this.converting) {
            this.convertAndLoadOpenSimFiles();
          }
        }
      },
      motFile: {
        handler(newVal) {
          if (newVal && this.osimFile && !this.converting) {
            this.convertAndLoadOpenSimFiles();
          }
        }
      },
      $route(to) {
        console.log('Route changed to:', to.path);
        if (to.path === '/samples' || to.path === '/samples/') {
          console.log('Loading sample files from route watcher');
          this.loadSampleFiles();
        }
      }
    },
    methods: {
    async loadTrial() {
      console.log('loadTrial started')
        this.time = "0.00"

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
            
            // Initialize alpha values
            this.initializeAlphaValue(0);
            
            // Add second animation if available
            if (res2 && res2.data) {
                this.animations.push({ 
                    data: res2.data, 
                    offset: new THREE.Vector3(0, 0, -1),
                    fileName: 'test2.json',
                    trialName: 'Subject 2'
                });
                this.initializeAlphaValue(1);
            }
            
            // Calculate and set frame rate from the JSON file's time data
            this.frameRate = this.calculateFrameRate(res1.data.time);

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
                  this.camera = new THREE.PerspectiveCamera(35, ratio, 0.1, 125)
                  this.camera.position.x = 3.33
                  this.camera.position.z = -2.30
                  this.camera.position.y = 3.5; 

                  this.scene = new THREE.Scene()
                  this.scene.background = new THREE.Color(0x808080)
                  this.renderer = new THREE.WebGLRenderer({antialias: true})
                  this.onResize()
                  container.appendChild(this.renderer.domElement)
                  this.controls = new THREE_OC.OrbitControls(this.camera, this.renderer.domElement)
  

  
                  // add the plane
                  {
                    const planeSize = 20;
  
                    const loader = new THREE.TextureLoader();
                    const texture = loader.load('https://threejsfundamentals.org/threejs/resources/images/checker.png');
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.magFilter = THREE.NearestFilter;
                    const repeats = planeSize;
                    texture.repeat.set(repeats, repeats);
  
                    // Store the texture reference
                    this.groundTexture = texture;

                    const planeGeo = new THREE.PlaneGeometry(planeSize, planeSize);
                    const planeMat = new THREE.MeshPhongMaterial({
                      map: this.useGroundTexture ? texture : null,
                      side: THREE.DoubleSide,
                      color: new THREE.Color(this.groundColor)
                    });
                    const groundMesh = new THREE.Mesh(planeGeo, planeMat);
                    groundMesh.rotation.x = Math.PI * -.5;
                    groundMesh.position.y = .0
                    this.scene.add(groundMesh);
                    
                    // Store the mesh reference inside the block where groundMesh is defined
                    this.groundMesh = groundMesh;
                    
                    // Set initial background color
                    this.scene.background = new THREE.Color(this.backgroundColor);
                  }
  
                  // add sun
                  {
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
                    this.scene.add(light);
                    this.scene.add(light.target);
                  }
  
                  // Load geometries for each animation
                  this.animations.forEach((animation, index) => {
                      for (let body in animation.data.bodies) {
                          let bd = animation.data.bodies[body]
                    bd.attachedGeometries.forEach((geom) => {
                      let path = 'https://mc-opencap-public.s3.us-west-2.amazonaws.com/geometries/' + geom.substr(0, geom.length - 4) + ".obj";
                      objLoader.load(path, (root) => {
                        root.castShadow = false;
                        root.receiveShadow = false;
                                  
                                  // Apply color to all meshes in the geometry
                                  root.traverse((child) => {
                          if (child instanceof THREE.Mesh) {
                            child.castShadow = false;
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
        requestAnimationFrame(this.animate);
          
        // Calculate time since last frame
        const currentTime = performance.now();
        const deltaTime = (currentTime - this.lastFrameTime) / 1000; // Convert to seconds
          
        if (this.playing && deltaTime >= (1 / this.frameRate)) { // Only update time if playing
            // Calculate how many frames should have advanced based on elapsed time
            // Apply playback speed multiplier
            const framesToAdvance = Math.floor(deltaTime * this.frameRate * this.playSpeed);
            
            if (framesToAdvance > 0) {
                // Advance the frame
                this.frame = (this.frame + framesToAdvance) % this.frames.length;
                
                // Update lastFrameTime based on the exact frames we advanced
                // This prevents timing drift by keeping track of actual time used
                this.lastFrameTime = currentTime - (deltaTime - (framesToAdvance / (this.frameRate * this.playSpeed))) * 1000;
                
                // Update displayed time based on actual frames in the JSON
                // If time data is available in frames array, use that, otherwise calculate from frame number
                if (this.frames[this.frame] !== undefined) {
                    this.time = parseFloat(this.frames[this.frame]).toFixed(2);
                } else {
                    this.time = parseFloat(this.frame / this.frameRate).toFixed(2);
                }
                
                // Render the current frame
                this.animateOneFrame();
            }
        } else if (!this.playing) {
            // Still render the scene even when not playing
            this.renderer.render(this.scene, this.camera);
        }
      },
      animateOneFrame() {
        let cframe = this.frame;
  
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

                  // Handle timelapse if enabled
                  if (this.timelapseMode && this.playing && cframe % this.timelapseInterval === 0) {
                    const scale = new THREE.Vector3(
                      json.bodies[body].scaleFactors[0],
                      json.bodies[body].scaleFactors[1],
                      json.bodies[body].scaleFactors[2]
                    );
                    this.createTimelapseMesh(
                      animIndex,
                      body,
                      geom,
                      position.clone(),
                      this.meshes[meshKey].quaternion.clone(),
                      scale
                    );
                  }
                }
              });
            }
          });
  
          this.renderer.render(this.scene, this.camera);
  
          // Frame advancement is now handled in the animate method
          // We're no longer advancing frames here
          if (this.playing && this.timelapseMode && cframe === this.frames.length - 1) {
            // Only stop playback at the end of sequence in timelapse mode
            this.togglePlay(false);
          }
        }
      },
      togglePlay(value) {
        this.playing = value
        if (this.playing) {
          // Reset timing references when starting playback
          this.lastFrameTime = performance.now();
          
          // Make sure first frame gets displayed immediately
          this.animateOneFrame();
        } else if (this.isRecording) {
          this.playing = true;
        }
      },
      onNavigate(frame) {
        this.frame = frame;
        // Use the actual time from the frames array if available, otherwise calculate it
        if (this.frames[frame] !== undefined) {
            this.time = parseFloat(this.frames[frame]).toFixed(2);
        } else {
            this.time = parseFloat(frame / this.frameRate).toFixed(2);
        }
        // Render the frame without advancing
        this.animateOneFrame();
      },
    getFileName(animation) {
        // Extract filename from the URL used to load the animation
        return animation.fileName || 'Animation'
    },
    updateOffset(animationIndex, axis, value) {
        // Get the animation
        const animation = this.animations[animationIndex];
        if (!animation) return;

        // Update the offset value
        animation.offset[axis] = Number(value);
        
        // Update all meshes for this animation
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${animationIndex}_`)) {
                const mesh = this.meshes[key];
                const body = key.split('_')[1].split('.')[0]; // Extract body name from key
                
                // Get current frame's base position
                if (animation.data.bodies[body] && 
                    animation.data.bodies[body].translation && 
                    animation.data.bodies[body].translation[this.frame]) {
                    
                    const basePosition = new THREE.Vector3(
                        animation.data.bodies[body].translation[this.frame][0],
                        animation.data.bodies[body].translation[this.frame][1],
                        animation.data.bodies[body].translation[this.frame][2]
                    );

                    // Apply the offset to the base position
                    mesh.position.copy(basePosition).add(animation.offset);
                }
            }
        });
        
        // Render the scene with updated positions
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
            this.animateOneFrame();
        }
    },
    startRecording() {
      if (!this.renderer) return;
      
      const canvas = this.renderer.domElement;
      const stream = canvas.captureStream(this.frameRate); // Now using dynamic frame rate
      
      // Set the appropriate MIME type and file extension based on the selected format
      let mimeType, fileExtension;
      
      if (this.recordingFormat === 'mp4') {
        mimeType = 'video/mp4';
        fileExtension = '.mp4';
      } else {
        // Default to webm
        mimeType = 'video/webm;codecs=vp9';
        fileExtension = '.webm';
      }
      
      // Update the file name based on the selected format
      this.recordingFileName = `animation-recording${fileExtension}`;
      
      // Try to create MediaRecorder with preferred format, fallback to webm if not supported
      try {
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: mimeType,
          videoBitsPerSecond: this.videoBitrate // Use the selected bitrate
        });
      } catch (error) {
        console.warn(`${mimeType} not supported, falling back to webm format`, error);
        this.recordingFormat = 'webm';
        this.recordingFileName = 'animation-recording.webm';
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'video/webm;codecs=vp9',
          videoBitsPerSecond: this.videoBitrate // Use the selected bitrate
        });
      }
      
      this.recordedChunks = [];
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };
      
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.recordedChunks, { type: mimeType });
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
    },
    calculateFrameRate(timeArray) {
        if (timeArray.length < 2) return 60; // Default to 60 if not enough data
        
        // Calculate total duration
        const totalTime = timeArray[timeArray.length - 1] - timeArray[0];
        
        // For more accurate frame rate calculation, we need to analyze the time step distribution
        // This handles cases where time steps are not uniform
        const timeSteps = [];
        for (let i = 1; i < timeArray.length; i++) {
            const step = timeArray[i] - timeArray[i-1];
            if (step > 0) {  // Ignore zero or negative steps
                timeSteps.push(step);
            }
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
        const finalFrameRate = Math.abs(medianFrameRate - averageFrameRate) < 10 ? 
            medianFrameRate : averageFrameRate;
        
        // Round and constrain to reasonable values
        const calculatedFps = Math.round(finalFrameRate);
        
        // Log the calculated frame rate for debugging
        console.log(`Frame rate calculation: Median=${medianFrameRate.toFixed(2)}, Average=${averageFrameRate.toFixed(2)}, Final=${calculatedFps}`);
        
        // Ensure we have a reasonable fps value (between 24 and 120)
        // Most mocap systems operate between 30-120 fps
        return Math.min(Math.max(calculatedFps, 24), 120);
    },
    handleFileUpload(event) {
        const files = event.target.files;
        if (!files.length) return;

        // Initialize scene if it doesn't exist
        if (!this.scene) {
            this.initScene();
        }

        // Get the current number of animations for offset calculation
        const startIndex = this.animations.length;

        // Create a Promise for each file
        const filePromises = Array.from(files).map(file => {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve({ data: JSON.parse(e.target.result), file });
                reader.readAsText(file);
            });
        });

        // Process all files together
        Promise.all(filePromises).then(results => {
            results.forEach(({ data, file }, index) => {
                const offset = new THREE.Vector3(
                    0,    // X: no offset
                    0,    // Y: no offset
                    0     // Z: no offset (changed from startIndex + index)
                );

                this.animations.push({
                    data: data,
                    offset: offset,
                    fileName: file.name,
                    trialName: `Subject ${startIndex + index + 1}`,
                    visible: true  // Add this line
                });

                if (this.animations.length === 1) {
                    this.frames = data.time;
                    this.trial = { results: [] };
                    // Calculate and set frame rate from first animation
                    this.frameRate = this.calculateFrameRate(data.time);
                }

                // Initialize the alpha value for the new animation
                this.initializeAlphaValue(startIndex + index);
            });

            // Keep track of loaded geometries
            let geometriesLoaded = 0;
            const totalGeometries = results.reduce((total, { data }) => {
                return total + Object.values(data.bodies).reduce((sum, body) => 
                    sum + body.attachedGeometries.length, 0);
            }, 0);

            this.$nextTick(() => {
                if (!this.scene) {
                    this.initScene();
                }
                
                // Only load geometries for new animations
                this.animations.slice(startIndex).forEach((animation, relativeIndex) => {
                    const animIndex = startIndex + relativeIndex;
                    for (let body in animation.data.bodies) {
                        let bd = animation.data.bodies[body];
                        bd.attachedGeometries.forEach((geom) => {
                            let path = 'https://mc-opencap-public.s3.us-west-2.amazonaws.com/geometries/' + 
                                     geom.substr(0, geom.length - 4) + ".obj";
                            objLoader.load(path, (root) => {
                                if (!this.scene) return;
                                
                                root.castShadow = false;
                                root.receiveShadow = false;
                                
                                root.traverse((child) => {
                                    if (child instanceof THREE.Mesh) {
                                        child.castShadow = false;
                                        child.material = new THREE.MeshPhongMaterial({ 
                                            color: this.colors[animIndex % this.colors.length],
                                            transparent: true,
                                            opacity: 0.8
                                        });
                                    }
                                });
                                
                                const meshKey = `anim${animIndex}_${body}${geom}`;
                                this.meshes[meshKey] = root;
                                this.meshes[meshKey].scale.set(
                                    bd.scaleFactors[0], 
                                    bd.scaleFactors[1], 
                                    bd.scaleFactors[2]
                                );
                                root.position.add(animation.offset);
                                this.scene.add(root);

                                // Track loaded geometries
                                geometriesLoaded++;

                                // If all geometries are loaded
                                if (geometriesLoaded === totalGeometries) {
                                    // After loading everything, sync the animations if we have more than one
                                    if (this.animations.length > 1) {
                                        this.syncAllAnimations();
                                    }

                                    // Start animation loop and render first frame
                                    this.animate();
                                    this.frame = 0;
                                    this.animateOneFrame();
                                    // Start playing automatically
                                    this.togglePlay(true);
                                }
                            });
                        });
                    }
                });
            });
        });

        // Clear the file input value so the same file can be selected again
        event.target.value = '';
    },
    initScene() {
        const container = this.$refs.mocap;
        if (!container) return;

        let ratio = container.clientWidth / container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(35, ratio, 0.1, 125);
        this.camera.position.x = 3.33;
        this.camera.position.z = -2.30;
        this.camera.position.y = 3.5;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x808080);
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.shadowMap.enabled = true;
        this.onResize();
        container.appendChild(this.renderer.domElement);
        this.controls = new THREE_OC.OrbitControls(this.camera, this.renderer.domElement);

        // Add plane
        const planeSize = 20;
        const loader = new THREE.TextureLoader();
        const texture = loader.load('https://threejsfundamentals.org/threejs/resources/images/checker.png');
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.magFilter = THREE.NearestFilter;
        const repeats = planeSize;
        texture.repeat.set(repeats, repeats);
        
        // Store the texture reference
        this.groundTexture = texture;

        const planeGeo = new THREE.PlaneGeometry(planeSize, planeSize);
        const planeMat = new THREE.MeshPhongMaterial({
            map: this.useGroundTexture ? texture : null,
            side: THREE.DoubleSide,
            color: new THREE.Color(this.groundColor)
        });
        const groundMesh = new THREE.Mesh(planeGeo, planeMat);
        groundMesh.rotation.x = Math.PI * -.5;
        groundMesh.position.y = 0;
        this.scene.add(groundMesh);
        
        // Store the mesh reference inside the block where groundMesh is defined
        this.groundMesh = groundMesh;
        
        
        // Set initial background color
        this.scene.background = new THREE.Color(this.backgroundColor);

        // Add lights
        const skyColor = 0xB1E1FF;
        const groundColor = 0xB97A20;
        const intensity = 0.5;
        const hemisphereLight = new THREE.HemisphereLight(skyColor, groundColor, intensity);
        this.scene.add(hemisphereLight);

        const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 0.8);
        directionalLight.position.set(2, 3, 1.5);
        directionalLight.target.position.set(0, 0, 0);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = -10;
        directionalLight.shadow.camera.bottom = 10;
        directionalLight.shadow.camera.near = 0;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.zoom = 8;
        this.scene.add(directionalLight);
        this.scene.add(directionalLight.target);

        // Initial render
        this.renderer.render(this.scene, this.camera);
    },
    onChangeTime(time) {
        // Round the time value to 2 decimal places
        this.time = parseFloat(time).toFixed(2);
        this.frame = Math.floor(time * this.frameRate);
        this.animateOneFrame();
    },
    syncAllAnimations() {
        if (this.animations.length <= 1) return;

        // Find the latest start time and earliest end time across all animations
        let latestStart = -Infinity;
        let earliestEnd = Infinity;
        let smallestTimeStep = Infinity;

        // First pass: find time boundaries and smallest time step
        this.animations.forEach(animation => {
            const startTime = animation.data.time[0];
            const endTime = animation.data.time[animation.data.time.length - 1];
            latestStart = Math.max(latestStart, startTime);
            earliestEnd = Math.min(earliestEnd, endTime);

            // Find smallest time step
            for (let i = 1; i < animation.data.time.length; i++) {
                const timeStep = animation.data.time[i] - animation.data.time[i-1];
                smallestTimeStep = Math.min(smallestTimeStep, timeStep);
            }
        });

        // Create a common time array with consistent step size
        const commonTimeArray = [];
        const totalDuration = earliestEnd - latestStart;
        // Calculate a fixed frame rate based on the time array
        const frameRate = this.calculateFrameRate([latestStart, earliestEnd]);
        // Use exact step size for consistent timing
        const timeStep = 1 / frameRate;
        
        // Create evenly spaced time points
        let currentTime = latestStart;
        while (currentTime <= earliestEnd) {
            commonTimeArray.push(currentTime);
            currentTime += timeStep;
        }

        // Sync each animation to the common time array
        this.animations.forEach((animation, index) => {
            const newData = {
                ...animation.data,
                time: commonTimeArray,
                bodies: {}
            };

            // For each body in the animation
            for (let body in animation.data.bodies) {
                newData.bodies[body] = {
                    ...animation.data.bodies[body],
                    translation: [],
                    rotation: []
                };

                // For each frame in the common time array
                commonTimeArray.forEach(time => {
                    // Find the closest original frame
                    const originalIndex = this.findClosestTimeIndex(animation.data.time, time);
                    
                    newData.bodies[body].translation.push([...animation.data.bodies[body].translation[originalIndex]]);
                    newData.bodies[body].rotation.push([...animation.data.bodies[body].rotation[originalIndex]]);
                });
            }

            // Update the animation data
            this.animations[index].data = newData;
        });

        // Update frames array to match the new common time array
        this.frames = commonTimeArray;
        this.frame = 0;
        this.time = parseFloat(this.frames[0]).toFixed(2);
        
        // Update frame rate based on new time steps
        this.frameRate = this.calculateFrameRate(commonTimeArray);

        // Update the view
        this.animateOneFrame();
    },
    findClosestTimeIndex(timeArray, target) {
        let left = 0;
        let right = timeArray.length - 1;
        
        while (left <= right) {
            const mid = Math.floor((left + right) / 2);
            
            if (timeArray[mid] === target) {
                return mid;
            }
            
            if (mid > 0 && timeArray[mid - 1] <= target && target < timeArray[mid]) {
                // Return the closest of the two indices
                return Math.abs(timeArray[mid - 1] - target) < Math.abs(timeArray[mid] - target) 
                    ? mid - 1 
                    : mid;
            }
            
            if (timeArray[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return left;
    },
    updateSubjectColor(index, colorHex) {
        if (colorHex === 'original') {
            // Remove color override, revert to original material
            Object.keys(this.meshes).forEach(key => {
                if (key.startsWith(`anim${index}_`)) {
                    const mesh = this.meshes[key];
                    mesh.traverse((child) => {
                        if (child instanceof THREE.Mesh) {
                            child.material = new THREE.MeshPhongMaterial({ 
                                color: 0xcccccc,  // Default grey color
                                transparent: false,
                                opacity: 1
                            });
                        }
                    });
                }
            });

            // Update color in our array
            this.colors[index] = new THREE.Color(0xcccccc);
            this.$forceUpdate(); // Force update to refresh the color box
        } else {
            // Regular color update
            const newColor = new THREE.Color(colorHex);
            this.colors[index] = newColor;
            this.$forceUpdate(); // Force update to refresh the color box

            Object.keys(this.meshes).forEach(key => {
                if (key.startsWith(`anim${index}_`)) {
                    const mesh = this.meshes[key];
                    mesh.traverse((child) => {
                        if (child instanceof THREE.Mesh) {
                            child.material.color = newColor;
                            child.material.transparent = true;
                            child.material.opacity = 0.8;
                            child.material.needsUpdate = true;
                        }
                    });
                }
            });
        }

        // Update text sprite
        const sprite = this.textSprites[`text_${index}`];
        if (sprite) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 64;
            
            context.font = 'bold 40px Arial';
            context.textAlign = 'center';
            context.fillStyle = colorHex === 'original' ? '#cccccc' : colorHex;
            context.fillText(this.animations[index].trialName, canvas.width/2, canvas.height/2);
            
            const texture = new THREE.CanvasTexture(canvas);
            sprite.material.map.dispose();
            sprite.material.map = texture;
            sprite.material.needsUpdate = true;
        }

        // Render the scene with updated colors
        this.renderer.render(this.scene, this.camera);
    },
    handleDrop(event) {
        const files = Array.from(event.dataTransfer.files);
        
        // Separate files by type
        const jsonFiles = files.filter(file => file.name.toLowerCase().endsWith('.json'));
        const osimFiles = files.filter(file => file.name.toLowerCase().endsWith('.osim'));
        const motFiles = files.filter(file => file.name.toLowerCase().endsWith('.mot'));
        
        // Handle JSON files directly
        if (jsonFiles.length > 0) {
            const dataTransfer = new DataTransfer();
            jsonFiles.forEach(file => dataTransfer.items.add(file));
            
            const fakeEvent = {
                target: {
                    files: dataTransfer.files,
                    value: ''
                }
            };
            
            this.handleFileUpload(fakeEvent);
        }
        
        // Handle OpenSim files
        if (osimFiles.length > 0 || motFiles.length > 0) {
            // If we have exactly one of each type, process them
            if (osimFiles.length === 1 && motFiles.length === 1) {
                this.osimFile = osimFiles[0];
                this.motFile = motFiles[0];
                this.convertAndLoadOpenSimFiles();
            } 
            // Otherwise, just store what we got and wait for the user to provide the missing file
            else {
                if (osimFiles.length === 1) {
                    this.osimFile = osimFiles[0];
                }
                if (motFiles.length === 1) {
                    this.motFile = motFiles[0];
                }
                
                if (osimFiles.length > 1 || motFiles.length > 1) {
                    alert('Please drop exactly one .osim file and one .mot file');
                }
            }
        }
        
        if (files.length === 0 || (jsonFiles.length === 0 && osimFiles.length === 0 && motFiles.length === 0)) {
            console.warn('Please drop JSON, OSIM, or MOT files');
        }
    },
    deleteSubject(index) {
        // Remove meshes for this animation
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${index}_`)) {
                const mesh = this.meshes[key];
                if (mesh) {
                    // Remove from scene
                    this.scene.remove(mesh);
                    // Dispose of geometries and materials
                    mesh.traverse((child) => {
                        if (child instanceof THREE.Mesh) {
                            if (child.geometry) child.geometry.dispose();
                            if (child.material) {
                                if (Array.isArray(child.material)) {
                                    child.material.forEach(material => material.dispose());
                                } else {
                                    child.material.dispose();
                                }
                            }
                        }
                    });
                }
                delete this.meshes[key];
            }
        });

        // Remove text sprite
        const sprite = this.textSprites[`text_${index}`];
        if (sprite) {
            this.scene.remove(sprite);
            if (sprite.material.map) sprite.material.map.dispose();
            sprite.material.dispose();
            delete this.textSprites[`text_${index}`];
        }

        // Remove any timelapse meshes associated with this animation
        if (this.timelapseGroups && this.timelapseGroups[index]) {
            this.deleteTimelapseGroup(index);
        }

        // Remove animation and color
        this.animations.splice(index, 1);
        this.colors.splice(index, 1);

        // Update timelapse indices for remaining animations
        if (this.timelapseGroups) {
            const newTimelapseGroups = {};
            Object.keys(this.timelapseGroups).forEach(key => {
                const animIndex = parseInt(key);
                if (animIndex > index) {
                    // Move the group to one index lower
                    newTimelapseGroups[animIndex - 1] = this.timelapseGroups[animIndex];
                } else if (animIndex < index) {
                    // Keep as is
                    newTimelapseGroups[animIndex] = this.timelapseGroups[animIndex];
                }
                // If animIndex === index, we skip it (it's the one being deleted)
            });
            this.timelapseGroups = newTimelapseGroups;

            // Update indices in timelapseMeshes
            Object.keys(this.timelapseMeshes).forEach(key => {
                const mesh = this.timelapseMeshes[key];
                if (mesh.animIndex > index) {
                    mesh.animIndex = mesh.animIndex - 1;
                }
            });
        }

        if (this.animations.length > 0) {
            // Update remaining subjects if any
            this.animations.forEach((animation, i) => {
                // Update mesh references to use the new animation indices
                Object.keys(this.meshes).forEach(key => {
                    if (key.startsWith(`anim${i + 1}_`)) {
                        // This key needs to be updated
                        const updatedKey = `anim${i}_${key.split('_').slice(1).join('_')}`;
                        this.meshes[updatedKey] = this.meshes[key];
                        delete this.meshes[key];
                    }
                });

                // Update mesh colors based on the new indices
                Object.keys(this.meshes).forEach(key => {
                    if (key.startsWith(`anim${i}_`)) {
                        const mesh = this.meshes[key];
                        mesh.traverse((child) => {
                            if (child instanceof THREE.Mesh) {
                                child.material.color = this.colors[i];
                                child.material.needsUpdate = true;
                            }
                        });
                    }
                });

                // Update text sprite color
                const sprite = this.textSprites[`text_${i}`];
                if (sprite) {
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.width = 256;
                    canvas.height = 64;
                    
                    context.font = 'bold 40px Arial';
                    context.textAlign = 'center';
                    context.fillStyle = '#' + this.colors[i].getHexString();
                    context.fillText(animation.trialName, canvas.width/2, canvas.height/2);
                    
                    const texture = new THREE.CanvasTexture(canvas);
                    if (sprite.material.map) sprite.material.map.dispose();
                    sprite.material.map = texture;
                    sprite.material.needsUpdate = true;
                }
            });

            this.frames = this.animations[0].data.time;
            if (this.animations.length > 1) {
                this.syncAllAnimations();
            }
        } else {
            // Reset to initial state when no animations remain
            this.frames = [];
            this.frame = 0;
            this.time = 0;
            this.trial = null;
            this.playing = false;
            
            // Clear all timelapse meshes
            this.clearTimelapse();
            
            // Clean up the scene completely
            if (this.scene) {
                // Remove all objects from the scene except camera and lights
                const objectsToRemove = [];
                this.scene.traverse((object) => {
                    // Skip lights and camera
                    if (object instanceof THREE.Light || object instanceof THREE.Camera || object === this.scene) {
                        return;
                    }
                    objectsToRemove.push(object);
                });
                
                // Remove collected objects
                objectsToRemove.forEach(object => {
                    if (object.parent) {
                        object.parent.remove(object);
                    }
                });
                
                // Dispose of all geometries and materials
                this.clearAllGeometries();
                
                // Render empty scene
                if (this.renderer) {
                    this.renderer.render(this.scene, this.camera);
                }
                
                // Remove the WebGL canvas from the DOM to fully clean up
                if (this.renderer && this.renderer.domElement) {
                    const container = this.$refs.mocap;
                    if (container && container.contains(this.renderer.domElement)) {
                        container.removeChild(this.renderer.domElement);
                    }
                    
                    // Dispose of the renderer itself
                    this.renderer.dispose();
                    this.renderer = null;
                    this.scene = null;
                }
            }
        }

        // Force render update
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    loadSampleFiles() {
        // Define the URLs for the sample files
        const sampleFiles = [
            '/samples/sample_mocap.json',
            '/samples/sample_mono.json',
            '/samples/sample_wham.json'
        ];
        
        // Show loading indicator
        this.trialLoading = true;
        
        // Clear existing animations before loading new ones
        this.animations = [];
        
        // Fetch all sample files
        Promise.all(sampleFiles.map(url => 
            fetch(url).then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load ${url}`);
                }
                return response.json();
            })
        ))
        .then(results => {
            // Process the sample files first
            results.forEach((data, index) => {
                // Get the filename from the URL
                const fileName = sampleFiles[index].split('/').pop();
                
                // Create animation data with better names
                this.animations.push({
                    data: data,
                    offset: new THREE.Vector3(0, 0, 0),
                    fileName: fileName,
                    trialName: fileName.replace('sample_', '').replace('.json', ''),
                    visible: true  // Add this line
                });
            });
            
            // Set up the trial and frames from the first animation
            if (this.animations.length > 0) {
                this.frames = this.animations[0].data.time;
                this.trial = { results: [] };
                this.frameRate = this.calculateFrameRate(this.animations[0].data.time);
            }
            
            // Force Vue to update the DOM before proceeding
            this.$nextTick(() => {
                // Initialize the scene if needed
                if (!this.scene || !this.renderer) {
                    // Clear the container first
                    const container = this.$refs.mocap;
                    if (container) {
                        while (container.firstChild) {
                            container.removeChild(container.firstChild);
                        }
                    }
                    
                    // Initialize the scene
                    this.initScene();
                    
                    // Wait a bit for the scene to be fully initialized
                    setTimeout(() => {
                        this.loadGeometriesForSamples();
                    }, 100);
                } else {
                    // Clear existing meshes and sprites
                    this.clearExistingObjects();
                    this.loadGeometriesForSamples();
                }
            });
        })
        .catch(error => {
            console.error('Error loading sample files:', error);
            this.trialLoading = false;
        });
    },
    clearExistingObjects() {
        // Clear any existing meshes
        Object.keys(this.meshes).forEach(key => {
            const mesh = this.meshes[key];
            if (mesh) {
                this.scene.remove(mesh);
                mesh.traverse((child) => {
                    if (child instanceof THREE.Mesh) {
                        if (child.geometry) child.geometry.dispose();
                        if (child.material) {
                            if (Array.isArray(child.material)) {
                                child.material.forEach(material => material.dispose());
                            } else {
                                child.material.dispose();
                            }
                        }
                    }
                });
            }
        });
        this.meshes = {};
        
        // Clear any existing text sprites
        Object.keys(this.textSprites).forEach(key => {
            const sprite = this.textSprites[key];
            if (sprite) {
                this.scene.remove(sprite);
                if (sprite.material.map) sprite.material.map.dispose();
                sprite.material.dispose();
            }
        });
        this.textSprites = {};
    },
    loadGeometriesForSamples() {
        // Load geometries
        let geometriesLoaded = 0;
        const totalGeometries = this.animations.reduce((total, animation) => {
            return total + Object.values(animation.data.bodies).reduce((sum, body) => 
                sum + body.attachedGeometries.length, 0);
        }, 0);
        
        if (totalGeometries === 0) {
            console.error('No geometries found in sample files');
            this.finishSampleLoading();
            return;
        }
        
        this.animations.forEach((animation, index) => {
            // Initialize the alpha value for each sample animation
            this.initializeAlphaValue(index);
            
            for (let body in animation.data.bodies) {
                let bd = animation.data.bodies[body];
                bd.attachedGeometries.forEach((geom) => {
                    let path = 'https://mc-opencap-public.s3.us-west-2.amazonaws.com/geometries/' + 
                             geom.substr(0, geom.length - 4) + ".obj";
                    objLoader.load(path, (root) => {
                        if (!this.scene) return;
                        
                        root.castShadow = true;
                        root.receiveShadow = true;
                        
                        root.traverse((child) => {
                            if (child instanceof THREE.Mesh) {
                                child.castShadow = true;
                                child.material = new THREE.MeshPhongMaterial({ 
                                    color: this.colors[index % this.colors.length],
                                    transparent: true,
                                    opacity: 0.8
                                });
                            }
                        });
                        
                        const meshKey = `anim${index}_${body}${geom}`;
                        this.meshes[meshKey] = root;
                        this.meshes[meshKey].scale.set(
                            bd.scaleFactors[0], 
                            bd.scaleFactors[1], 
                            bd.scaleFactors[2]
                        );
                        root.position.add(animation.offset);
                        this.scene.add(root);
                        
                        // Track loaded geometries
                        geometriesLoaded++;
                        
                        // If all geometries are loaded
                        if (geometriesLoaded === totalGeometries) {
                            this.finishSampleLoading();
                        }
                    }, 
                    undefined,
                    (error) => {
                        console.error('Error loading geometry:', error);
                        geometriesLoaded++;
                        if (geometriesLoaded === totalGeometries) {
                            this.finishSampleLoading();
                        }
                    });
                });
            }
        });
    },
    finishSampleLoading() {
        // After loading everything, sync the animations if we have more than one
        if (this.animations.length > 1) {
            this.syncAllAnimations();
        }
        
        // Initialize timing
        this.frame = 0;
        // Use the actual time from the frames array if available
        if (this.frames[0] !== undefined) {
            this.time = parseFloat(this.frames[0]).toFixed(2);
        } else {
            this.time = "0.00";
        }
        
        // Start animation loop and render first frame
        this.animate();
        this.animateOneFrame();
        
        // Hide loading indicator
        this.trialLoading = false;
        
        // Start playing automatically after a short delay to ensure everything is ready
        setTimeout(() => {
            this.togglePlay(true);
        }, 100);
    },
    updateBackgroundColor(color) {
        this.backgroundColor = color;
        if (this.scene) {
            this.scene.background = new THREE.Color(color);
            this.renderer.render(this.scene, this.camera);
        }
    },
    updateGroundColor(color) {
        this.groundColor = color;
        if (this.groundMesh && this.groundMesh.material) {
            // If not using texture, just set the color
            if (!this.useGroundTexture) {
                this.groundMesh.material.color = new THREE.Color(color);
            } else {
                // If using texture, create a new material with both texture and color
                const oldMaterial = this.groundMesh.material;
                const newMaterial = new THREE.MeshPhongMaterial({
                    map: this.groundTexture,
                    side: THREE.DoubleSide,
                    color: new THREE.Color(color)
                });
                
                this.groundMesh.material = newMaterial;
                
                // Dispose of old material
                if (oldMaterial) oldMaterial.dispose();
            }
            
            this.renderer.render(this.scene, this.camera);
        }
    },
    toggleGroundTexture() {
        this.useGroundTexture = !this.useGroundTexture;
        
        if (this.groundMesh) {
            const oldMaterial = this.groundMesh.material;
            
            if (this.useGroundTexture) {
                // Use textured material with either checkerboard or grid
                const textureToUse = this.useCheckerboard ? this.groundTexture : this.gridTexture;
                this.groundMesh.material = new THREE.MeshPhongMaterial({
                    map: textureToUse,
                    side: THREE.DoubleSide,
                    color: new THREE.Color(this.groundColor)
                });
            } else {
                // Use plain colored material
                this.groundMesh.material = new THREE.MeshPhongMaterial({
                    color: new THREE.Color(this.groundColor),
                    side: THREE.DoubleSide
                });
            }
            
            // Dispose of old material
            if (oldMaterial) oldMaterial.dispose();
            
            this.renderer.render(this.scene, this.camera);
        }
    },
    toggleCheckerboard() {
        this.useCheckerboard = !this.useCheckerboard;
        
        if (this.groundMesh && this.useGroundTexture) {
            const oldMaterial = this.groundMesh.material;
            
            // Load the appropriate texture
            if (!this.useCheckerboard && !this.gridTexture) {
                // Create grid texture if it doesn't exist
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.width = 512;
                canvas.height = 512;
                
                // Fill with background color
                context.fillStyle = '#ffffff';
                context.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw grid lines
                context.strokeStyle = '#000000';
                context.lineWidth = 1;
                
                
                const gridSize = 32; // Size of grid cells
                
                // Draw vertical lines
                for (let x = 0; x <= canvas.width; x += gridSize) {
                    context.beginPath();
                    context.moveTo(x, 0);
                    context.lineTo(x, canvas.height);
                    context.stroke();
                }
                
                // Draw horizontal lines
                for (let y = 0; y <= canvas.height; y += gridSize) {
                    context.beginPath();
                    context.moveTo(0, y);
                    context.lineTo(canvas.width, y);
                    context.stroke();
                }
                
                // Create texture from canvas
                this.gridTexture = new THREE.CanvasTexture(canvas);
                this.gridTexture.wrapS = THREE.RepeatWrapping;
                this.gridTexture.wrapT = THREE.RepeatWrapping;
                this.gridTexture.repeat.set(10, 10); // Adjust repeat to match plane size
            }
            
            // Create new material with the appropriate texture
            const newMaterial = new THREE.MeshPhongMaterial({
                map: this.useCheckerboard ? this.groundTexture : this.gridTexture,
                side: THREE.DoubleSide,
                color: new THREE.Color(this.groundColor)
            });
            
            this.groundMesh.material = newMaterial;
            
            // Dispose of old material
            if (oldMaterial) oldMaterial.dispose();
            
            this.renderer.render(this.scene, this.camera);
        }
    },
    toggleGroundVisibility() {
        this.showGround = !this.showGround;
        
        if (this.groundMesh) {
            this.groundMesh.visible = this.showGround;
            this.renderer.render(this.scene, this.camera);
        }
    },
    captureScreenshot() {
        if (!this.renderer) return;
        
        // Store original states
        const originalWidth = this.renderer.domElement.width;
        const originalHeight = this.renderer.domElement.height;
        const originalBackground = this.scene.background;
        const originalGroundVisibility = this.groundMesh ? this.groundMesh.visible : false;
        const originalClearColor = this.renderer.getClearColor();
        const originalClearAlpha = this.renderer.getClearAlpha();
        const originalPreserveDrawingBuffer = this.renderer.preserveDrawingBuffer;
        
        // Set to high resolution for screenshot (4x)
        const scale = 4;
        
        // Create a new renderer for the transparent version
        const transparentRenderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            preserveDrawingBuffer: true
        });
        transparentRenderer.setSize(originalWidth * scale, originalHeight * scale);
        
        // Determine which captures to create based on user selection
        let captures = [];
        
        if (this.captureMode === 'both' || this.captureMode === 'normal') {
            captures.push({ 
                name: 'mocap-capture.png', 
                background: originalBackground,
                showGround: originalGroundVisibility,
                transparent: false,
                useMainRenderer: true
            });
        }
        
        if (this.captureMode === 'both' || this.captureMode === 'transparent') {
            captures.push({ 
                name: 'mocap-capture-transparent.png', 
                background: null,
                showGround: false,
                transparent: true,
                useMainRenderer: false
            });
        }
        
        // Set main renderer to high resolution
        this.renderer.setSize(originalWidth * scale, originalHeight * scale);
        
        // Force camera aspect ratio update
        this.camera.aspect = (originalWidth * scale) / (originalHeight * scale);
        this.camera.updateProjectionMatrix();
        
        // Create download links for the selected version(s)
        captures.forEach(capture => {
            // Set background (null for transparent)
            this.scene.background = capture.background;
            
            // Set ground visibility
            if (this.groundMesh) {
                this.groundMesh.visible = capture.showGround;
            }
            
            const currentRenderer = capture.useMainRenderer ? this.renderer : transparentRenderer;
            
            // Set renderer properties for transparency
            if (capture.transparent) {
                currentRenderer.setClearColor(0x000000, 0);
                currentRenderer.setClearAlpha(0);
            } else {
                currentRenderer.setClearColor(originalClearColor, originalClearAlpha);
            }
            
            // Render the scene
            currentRenderer.render(this.scene, this.camera);
            
            // Capture the image
            const dataURL = currentRenderer.domElement.toDataURL('image/png');
            
            // Create and trigger download
            const link = document.createElement('a');
            link.href = dataURL;
            link.download = capture.name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
        
        // Clean up transparent renderer
        transparentRenderer.dispose();
        
        // Restore original settings
        this.renderer.setSize(originalWidth, originalHeight);
        this.camera.aspect = originalWidth / originalHeight;
        this.camera.updateProjectionMatrix();
        this.scene.background = originalBackground;
        if (this.groundMesh) {
            this.groundMesh.visible = originalGroundVisibility;
        }
        this.renderer.setClearColor(originalClearColor, originalClearAlpha);
        
        // Re-render at original size
        this.renderer.render(this.scene, this.camera);
        
        // Show a success message with appropriate text based on capture mode
        this.$nextTick(() => {
            let message = '';
            if (this.captureMode === 'both') {
                message = 'Images captured and downloaded!\nTwo versions saved: with background/ground and fully transparent.';
            } else if (this.captureMode === 'normal') {
                message = 'Image captured and downloaded with background/ground.';
            } else {
                message = 'Transparent image captured and downloaded.';
            }
            alert(message);
        });
    },
    updateAlpha(animationIndex, value) {
        // Update the alpha value for the specified animation
        this.alphaValues[animationIndex] = value;

        // Update all meshes for this animation
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${animationIndex}_`)) {
                const mesh = this.meshes[key];
                mesh.traverse((child) => {
                    if (child instanceof THREE.Mesh) {
                        child.material.opacity = value; // Set the new alpha value
                        child.material.transparent = true; // Ensure transparency is enabled
                        child.material.needsUpdate = true; // Update the material
                    }
                });
            }
        });

        // Render the scene with updated transparency
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    initializeAlphaValue(index) {
        // Set default opacity to 0.8, which matches what we set when creating materials
        if (!this.alphaValues[index] && this.alphaValues[index] !== 0) {
            this.$set(this.alphaValues, index, 0.8);
        }
        // Initialize RGB values
        this.initializeRgbValues(index);
    },
    initializeRgbValues(index) {
      if (!this.rgbValues[index]) {
        this.$set(this.rgbValues, index, { r: 128, g: 128, b: 128 });
      }
    },
    updateRgbColor(index) {
      const { r, g, b } = this.rgbValues[index];
      const colorHex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
      this.updateSubjectColor(index, colorHex);
    },
    prepareTransparencyMenu(index) {
        // Get the current opacity from the first mesh we find for this animation
        let currentOpacity = null;
        
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${index}_`) && currentOpacity === null) {
                const mesh = this.meshes[key];
                mesh.traverse((child) => {
                    if (child instanceof THREE.Mesh && currentOpacity === null) {
                        currentOpacity = child.material.opacity;
                    }
                });
            }
        });
        
        // If we found an opacity value, update the alphaValues array
        if (currentOpacity !== null) {
            this.$set(this.alphaValues, index, currentOpacity);
        }
        // If not found, initialize with default
        else {
            this.initializeAlphaValue(index);
        }
    },
    selectOsimFile(event) {
        const file = event.target.files[0];
        if (file && file.name.endsWith('.osim')) {
            this.osimFile = file;
            // If we already have a .mot file, auto-convert
            if (this.motFile) {
                this.convertAndLoadOpenSimFiles();
            }
        }
        // Clear the input so the same file can be selected again
        event.target.value = '';
    },
    selectMotFile(event) {
        const file = event.target.files[0];
        if (file && file.name.endsWith('.mot')) {
            this.motFile = file;
            // If we already have an .osim file, auto-convert
            if (this.osimFile) {
                this.convertAndLoadOpenSimFiles();
            }
        }
        // Clear the input so the same file can be selected again
        event.target.value = '';
    },
    async convertAndLoadOpenSimFiles() {
        if (!this.osimFile || !this.motFile) {
            alert('Please select both .osim and .mot files');
            return;
        }
        
        this.converting = true;
        this.conversionError = null; // Reset any previous error
        
        try {
            console.log('Converting files using API:', this.apiUrl);
            
            // Create a FormData object to send the files
            const formData = new FormData();
            formData.append('osim_file', this.osimFile);
            formData.append('mot_file', this.motFile);
            
            // Call the API to convert the files
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                body: formData,
            });
            
            // Check if response is not ok before trying to parse JSON
            if (!response.ok) {
                let errorText = '';
                try {
                    // Try to get detailed error from response body
                    const errorData = await response.json();
                    errorText = errorData.error || errorData.message || errorData.detail || JSON.stringify(errorData);
                } catch (e) {
                    // If can't parse JSON, use status text
                    errorText = await response.text() || `${response.status} ${response.statusText}`;
                }
                
                this.conversionError = errorText;
                apiError(errorText);
                // Clear the files on error
                this.osimFile = null;
                this.motFile = null;
                throw new Error(errorText);
            }
            
            // Parse the JSON response (only if response was ok)
            const data = await response.json();
            
            // Check if the API returned an error in a successful response
            if (data.error) {
                this.conversionError = data.error;
                apiError(data.error);
                // Clear the files on error
                this.osimFile = null;
                this.motFile = null;
                throw new Error(data.error);
            }
            
            // Create a "virtual" File object with the JSON data
            const jsonBlob = new Blob([JSON.stringify(data)], { type: 'application/json' });
            const jsonFile = new File([jsonBlob], `${this.osimFile.name.replace('.osim', '')}.json`, { type: 'application/json' });
            
            // Use our existing file handler with a fake event
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(jsonFile);
            
            const fakeEvent = {
                target: {
                    files: dataTransfer.files,
                    value: ''
                }
            };
            
            // Process the converted JSON
            this.handleFileUpload(fakeEvent);
            
            // Clear the selected files after successful conversion
            this.osimFile = null;
            this.motFile = null;
            
        } catch (error) {
            console.error('Error converting OpenSim files:', error);
            // Only show alert if apiError wasn't already called
            if (!this.conversionError) {
                apiError(`Error converting files: ${error.message}`);
                this.conversionError = `Error converting files: ${error.message}`;
            }
            // Clear the files on any error
            this.osimFile = null;
            this.motFile = null;
        } finally {
            this.converting = false;
        }
    },
    handleOpenSimFiles(event) {
        const files = Array.from(event.target.files);
        
        // Filter for osim and mot files
        const osimFiles = files.filter(file => file.name.toLowerCase().endsWith('.osim'));
        const motFiles = files.filter(file => file.name.toLowerCase().endsWith('.mot'));
        
        // Only update the files that the user is explicitly selecting now
        // Don't clear existing selections unless we're replacing them
        
        // Handle .osim files
        if (osimFiles.length === 1) {
            this.osimFile = osimFiles[0];
        } else if (osimFiles.length > 1) {
            alert('Please select only one .osim file at a time');
            // Don't change existing selection if multiple files were selected
        }
        
        // Handle .mot files
        if (motFiles.length === 1) {
            this.motFile = motFiles[0];
        } else if (motFiles.length > 1) {
            alert('Please select only one .mot file at a time');
            // Don't change existing selection if multiple files were selected
        }
        
        // If we now have a complete pair, process them
        if (this.osimFile && this.motFile) {
            this.convertAndLoadOpenSimFiles();
        } else {
            // Otherwise provide guidance on what's still needed
            if (this.osimFile && !this.motFile) {
                alert('Please also select a .mot file');
            } else if (!this.osimFile && this.motFile) {
                alert('Please also select an .osim file');
            }
        }
        
        // Clear input value so same files can be selected again
        event.target.value = '';
    },
    toggleSubjectVisibility(index) {
        // Toggle the visibility state
        this.animations[index].visible = !this.animations[index].visible;
        
        // Update all meshes for this animation
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${index}_`)) {
                const mesh = this.meshes[key];
                mesh.visible = this.animations[index].visible;
            }
        });
        
        // Update text sprite visibility
        const sprite = this.textSprites[`text_${index}`];
        if (sprite) {
            sprite.visible = this.animations[index].visible;
        }
        
        // Render the scene with updated visibility
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    toggleTimelapseMode() {
        if (!this.timelapseMode) {
          // Clear existing timelapse meshes when turning off
          this.clearTimelapse();
        } else {
          // Reset frame count when turning on
          this.timelapseFrameCount = 0;
        }
      },

      updateTimelapse() {
        // Clear existing timelapse and start fresh with new interval
        this.clearTimelapse();
        this.timelapseFrameCount = 0;
      },

      clearTimelapse() {
        // Remove all timelapse meshes from scene
        Object.values(this.timelapseMeshes).forEach(({mesh}) => {
          if (mesh) {
            this.scene.remove(mesh);
            mesh.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                  if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                  } else {
                    child.material.dispose();
                  }
                }
              }
            });
          }
        });
        this.timelapseMeshes = {};
        this.timelapseGroups = {};
        this.timelapseFrameCount = 0;
        
        // Re-render the scene
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },

      createTimelapseMesh(animationIndex, body, geom, position, rotation, scale) {
        // Use sequential counter for mesh ID
        if (!this.timelapseCounter) {
          this.timelapseCounter = 1;
        }
        const meshId = this.timelapseCounter++;
        const meshKey = `timelapse_${meshId}`;
        
        // Clone the original mesh
        const originalMesh = this.meshes[`anim${animationIndex}_${body}${geom}`];
        if (!originalMesh) return;

        const clone = originalMesh.clone();
        
        // Set position and rotation
        clone.position.copy(position);
        clone.quaternion.copy(rotation);
        
        // Apply scale
        clone.scale.copy(scale);
        
        // Make material more transparent for timelapse
        clone.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            const material = child.material.clone();
            material.transparent = true;
            material.opacity = this.timelapseOpacity;
            child.material = material;
          }
        });
        
        // Add to scene and store reference
        this.scene.add(clone);
        
        // Store metadata with the mesh
        this.timelapseMeshes[meshKey] = {
          mesh: clone,
          frame: this.frame,
          animIndex: animationIndex,
          body: body,
          geom: geom,
          id: meshId
        };

        // Update timelapse groups for management
        if (!this.timelapseGroups[animationIndex]) {
          this.$set(this.timelapseGroups, animationIndex, []);
        }
        if (!this.timelapseGroups[animationIndex].includes(this.frame)) {
          this.timelapseGroups[animationIndex].push(this.frame);
          // Sort frames in ascending order
          this.timelapseGroups[animationIndex].sort((a, b) => a - b);
        }
        
        this.timelapseFrameCount++;
      },

      updateTimelapseOpacity() {
        // Update opacity for all existing timelapse meshes
        Object.values(this.timelapseMeshes).forEach(mesh => {
          if (mesh) {
            mesh.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                child.material.opacity = this.timelapseOpacity;
                child.material.needsUpdate = true;
              }
            });
          }
        });
        
        // Re-render the scene
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },

      deleteTimelapseGroup(animIndex) {
        // Count meshes before deletion
        const beforeCount = Object.keys(this.timelapseMeshes).length;
        const toDelete = [];
        
        // First collect all keys to delete (without modifying during iteration)
        Object.entries(this.timelapseMeshes).forEach(([key, value]) => {
          if (value.animIndex === animIndex) {
            toDelete.push(key);
          }
        });
        
        // Now delete and remove meshes
        toDelete.forEach(key => {
          const data = this.timelapseMeshes[key];
          
          if (data && data.mesh) {
            // First check if the mesh is actually in the scene
            if (this.scene && this.scene.children && this.scene.children.includes(data.mesh)) {
              this.scene.remove(data.mesh);
            }
            
            // Dispose resources
            data.mesh.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                  if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                  } else {
                    child.material.dispose();
                  }
                }
              }
            });
          }
          
          // Remove from timelapseMeshes
          delete this.timelapseMeshes[key];
        });

        // Remove the group from timelapseGroups
        if (this.timelapseGroups && this.timelapseGroups[animIndex] !== undefined) {
          this.$delete(this.timelapseGroups, animIndex);
        }
        
        // Force re-render
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },

      deleteTimelapseFrame(animIndex, frame) {
        // Count meshes before deletion
        const beforeCount = Object.keys(this.timelapseMeshes).length;
        const toDelete = [];
        
        // First collect all keys to delete
        Object.entries(this.timelapseMeshes).forEach(([key, value]) => {
          // Convert to numbers for comparison
          const dataFrame = Number(value.frame);
          const targetFrame = Number(frame);
          const dataAnimIndex = Number(value.animIndex);
          const targetAnimIndex = Number(animIndex);
          
          if (dataAnimIndex === targetAnimIndex && dataFrame === targetFrame) {
            toDelete.push(key);
          }
        });
        
        // Now delete and remove meshes
        toDelete.forEach(key => {
          const data = this.timelapseMeshes[key];
          
          if (data && data.mesh) {
            // Check if mesh is in scene
            if (this.scene.children.includes(data.mesh)) {
              this.scene.remove(data.mesh);
            }
            
            // Dispose resources
            data.mesh.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                  if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                  } else {
                    child.material.dispose();
                  }
                }
              }
            });
          }
          
          // Remove from timelapseMeshes
          delete this.timelapseMeshes[key];
        });

        // Remove the frame from the group
        const frameIndex = this.timelapseGroups[animIndex].indexOf(Number(frame));
        if (frameIndex !== -1) {
          this.timelapseGroups[animIndex].splice(frameIndex, 1);
        }

        // If no more frames in this group, remove the group
        if (this.timelapseGroups[animIndex].length === 0) {
          this.$delete(this.timelapseGroups, animIndex);
        }

        // Force re-render
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },
      getMeshIdForFrame(animIndex, frame) {
        // Find the mesh ID for this frame and animation
        const mesh = Object.values(this.timelapseMeshes).find(m => {
          // Convert to numbers to ensure exact comparison
          const dataFrame = Number(m.frame);
          const targetFrame = Number(frame);
          const dataAnimIndex = Number(m.animIndex);
          const targetAnimIndex = Number(animIndex);
          
          return dataAnimIndex === targetAnimIndex && dataFrame === targetFrame;
        });
        
        return mesh ? mesh.id : 'N/A';
      },
      getMeshKeysForAnimation(index) {
        return Object.keys(this.meshes).filter(key => key.startsWith(`anim${index}_`));
      },
      getMeshName(meshKey) {
        // Format of key is anim{index}_{body}{geom}
        const parts = meshKey.split('_');
        if (parts.length < 2) return meshKey;
        
        // Get the part after the first underscore (body+geom)
        const bodyAndGeom = parts[1];
        
        // Extract the geom part which is the filename
        // Typically these are named like 'lunate_lvs.vtp' or 'triquetrum_rvs.vtp'
        // We want to display just the bone name like 'lunate' or 'triquetrum'
        
        // First look for _lvs or _rvs pattern to extract the bone name
        if (bodyAndGeom.includes('_lvs') || bodyAndGeom.includes('_rvs')) {
          const boneName = bodyAndGeom.split('_')[0];
          return boneName; 
        }
        
        // Fallback to the original bodyAndGeom
        return bodyAndGeom;
      },
      toggleMeshVisibility(meshKey) {
        const mesh = this.meshes[meshKey];
        if (mesh) {
          mesh.visible = !mesh.visible;
          this.renderer.render(this.scene, this.camera);
        }
      },
      getGroupedMeshes(index) {
        // Get all mesh keys for this animation
        const meshKeys = this.getMeshKeysForAnimation(index);
        
        // Group object to organize meshes
        const groups = {
          'Hands': [],
          'Arms': [],
          'Other': []
        };
        
        // Categorize each mesh
        meshKeys.forEach(key => {
          const name = this.getMeshName(key);
          
          // Check if it's a hand-related mesh
          if (name.includes('hand') || 
              name.includes('lunate') || 
              name.includes('pisiform') || 
              name.includes('triquetrum') || 
              name.includes('thumb') || 
              name.includes('index') || 
              name.includes('middle') || 
              name.includes('ring') || 
              name.includes('little')) {
            groups['Hands'].push({key, name});
          }
          // Check if it's an arm-related mesh
          else if (name.includes('humerus') || 
                  name.includes('ulna') || 
                  name.includes('radius')) {
            groups['Arms'].push({key, name});
          }
          // Everything else
          else {
            groups['Other'].push({key, name});
          }
        });
        
        // Remove empty groups
        Object.keys(groups).forEach(key => {
          if (groups[key].length === 0) {
            delete groups[key];
          }
        });
        
        return groups;
      },
      toggleGroupVisibility(animIndex, groupName, items) {
        // Check the current visibility state of meshes in this group
        // If all are visible, hide all. If some or all are hidden, show all.
        
        // Check if at least one mesh is visible
        const hasVisibleMesh = items.some(item => 
          this.meshes[item.key] && this.meshes[item.key].visible !== false
        );
        
        // Set all to the opposite state
        const newVisibility = !hasVisibleMesh;
        
        // Update all meshes in this group
        items.forEach(item => {
          if (this.meshes[item.key]) {
            this.meshes[item.key].visible = newVisibility;
          }
        });
        
        // Re-render the scene
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },
      isGroupVisible(items) {
        // Check if any mesh in this group is visible
        return items.some(item => 
          this.meshes[item.key] && this.meshes[item.key].visible !== false
        );
      },
      clearAllGeometries() {
        // Dispose of all geometries and materials for clean memory usage
        THREE.Cache.clear();
        
        // Helper function to dispose material
        const disposeMaterial = (material) => {
            if (material.map) material.map.dispose();
            if (material.lightMap) material.lightMap.dispose();
            if (material.bumpMap) material.bumpMap.dispose();
            if (material.normalMap) material.normalMap.dispose();
            if (material.specularMap) material.specularMap.dispose();
            if (material.envMap) material.envMap.dispose();
            material.dispose();
        };
        
        // Process all scene objects and dispose geometries and materials
        this.scene.traverse(object => {
            if (object instanceof THREE.Mesh) {
                if (object.geometry) {
                    object.geometry.dispose();
                }
                
                if (object.material) {
                    if (Array.isArray(object.material)) {
                        object.material.forEach(material => disposeMaterial(material));
                    } else {
                        disposeMaterial(object.material);
                    }
                }
            } else if (object instanceof THREE.Sprite) {
                if (object.material && object.material.map) {
                    object.material.map.dispose();
                }
                if (object.material) object.material.dispose();
            }
        });
        
        // Reset meshes and text sprites
        this.meshes = {};
        this.textSprites = {};
        this.timelapseMeshes = {};
        this.timelapseGroups = {};
    },
    clearConversionError() {
        this.conversionError = null;
        // Also make sure files are cleared when error is dismissed
        this.osimFile = null;
        this.motFile = null;
    },
    }
  }
  </script>
  
  <style lang="scss">
.viewer-container {
  height: 100vh;
  position: relative;
  
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
      flex: 0 0 350px;
      height: 100%;
      padding: 10px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;

      &::-webkit-scrollbar {
        width: 8px;
      }

      &::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        
        &:hover {
          background: rgba(255, 255, 255, 0.4);
        }
      }

      .recording-controls {
        text-align: center;
        flex-shrink: 0;
        
        .v-btn {
          width: 100%;
        }
        
        .format-selector {
          min-width: 80px;
        }
        
        .d-flex {
          width: 100%;
        }
        
        // Override width for buttons inside flex container
        .d-flex .v-btn {
          width: auto;
          flex: 1;
        }
      }

      .file-controls {
        text-align: center;
        flex-shrink: 0;
        
        .v-btn {
          width: 100%;
        }
      }

      .sync-controls {
        text-align: center;
        flex-shrink: 0;
        
        .v-btn {
          width: 100%;
        }
      }

      .scene-controls {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
        padding: 10px;
      }

      .color-preview {
        width: 32px !important;
        min-width: 32px !important;
        height: 24px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
      }

      .legend {
        flex: 1;
        overflow-y: auto;
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
            flex-wrap: wrap;
          }

          // Add new styles for button spacing
          .v-btn {
            margin-left: 4px !important;
            min-width: 32px !important;
            width: 32px !important;
            height: 32px !important;
            padding: 0 !important;
          }
        }
      }
    }

    .controls-container {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 4px;
      margin: 5px;
      padding: 8px;
    }
  }

.trial-name-input {
    .v-input__slot {
        margin-bottom: 0 !important;
    }
    input {
        font-weight: bold !important;
        font-size: 14px !important;
    }
}

.color-picker {
    background: #424242 !important;
    max-width: 200px;
}

.color-sample {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.1);

    &[style*="original"] {
        background-color: #cccccc !important;
        position: relative;
        
        &::after {
            content: "O";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #000;
            font-size: 12px;
            font-weight: bold;
      }
    }
  }

.drop-zone {
    width: 90%;
    height: 80%;
    min-height: 350px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border: 3px dashed rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    margin: 20px;
    transition: all 0.3s ease;
    
    &:hover {
        border-color: rgba(255, 255, 255, 0.4);
        background: rgba(255, 255, 255, 0.08);
    }
  }

.transparency-picker {
    background: #424242 !important;
}

.selected-files-info {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
  font-size: 12px;
}

.conversion-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 10;
  border-radius: 8px;
  padding: 20px;
  color: white;
}

.conversion-overlay-small {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 10;
  border-radius: 4px;
  padding: 10px;
  color: white;
}

.opacity-reduced {
  opacity: 0.3;
  pointer-events: none;
}

.position-relative {
  position: relative;
}

.rgb-picker {
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}
  </style>
  
  