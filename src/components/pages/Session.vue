<template>
    <div class="viewer-container d-flex">
      <!-- Top-level video container - always rendered -->
      <div id="video-overlay" v-if="videoFile" :style="{
        position: 'fixed',
        top: videoPosition.y + 'px',
        left: videoPosition.x + 'px',
        width: videoSize.width + 'px',
        background: '#000',
        border: '2px solid #fff',
        borderRadius: '8px',
        zIndex: 99999,
        boxShadow: '0 4px 20px rgba(0,0,0,0.8)',
        overflow: 'hidden',
        cursor: isDragging ? 'grabbing' : 'default'
      }">
        <div 
          :style="{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '4px',
            background: 'rgba(0,0,0,0.8)',
            cursor: 'grab'
          }"
          @mousedown="startDrag"
          @touchstart="startDrag"
        >
          <div style="display: flex; align-items: center;">
            <v-icon x-small dark class="mr-1">mdi-drag</v-icon>
            <span class="caption white--text">Drag to move</span>
          </div>
          <div>
            <v-btn icon x-small dark @click="toggleVideoPreview" class="mr-1">
              <v-icon>{{ videoMinimized ? 'mdi-arrow-expand' : 'mdi-arrow-collapse' }}</v-icon>
            </v-btn>
            <v-btn icon x-small dark @click="closeVideo">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </div>
        <video 
          ref="videoPreview" 
          :style="{ width: '100%', height: 'auto', minHeight: videoMinimized ? '120px' : '200px' }"
          @loadedmetadata="handleVideoMetadata"
          controls
        >
          <source :src="videoUrl" :type="videoFile.type">
          Your browser does not support the video tag.
        </video>
        
        <!-- Resize handle -->
        <div 
          :style="{
            position: 'absolute',
            bottom: '0',
            right: '0',
            width: '20px',
            height: '20px',
            cursor: 'nwse-resize',
            background: 'linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.5) 50%)'
          }"
          @mousedown="startResize"
          @touchstart="startResize"
        ></div>
      </div>
      
      <div class="viewer flex-grow-1" :class="{ 'sidebar-hidden': !showSidebar, 'is-embedded': $route.query.embed === 'true' }" @dragover.prevent @drop.prevent="handleDrop">
        <div v-if="trial" class="d-flex flex-column h-100">
          <div id="mocap" ref="mocap" class="flex-grow-1 position-relative">
            <!-- Debug info -->
            <div v-if="videoFile && !$refs.videoPreview" class="debug-info">
              Video file loaded but preview not mounted
            </div>
          </div>
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
            <!-- Add Loop button here -->
            <v-btn icon dark @click="toggleLooping" :disabled="videoControlsDisabled" class="mr-2">
              <v-icon :color="isLooping ? 'indigo lighten-1' : 'grey'">{{ isLooping ? 'mdi-repeat' : 'mdi-repeat-off' }}</v-icon>
            </v-btn>
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
            <div v-if="osimFile || motFile || videoFile" class="text-h6 grey--text text--darken-1 mt-4">
              <div v-if="osimFile" class="selected-file mb-2">
                <v-chip small color="indigo" dark>{{ osimFile.name }}</v-chip>
              </div>
              <div v-if="motFile" class="selected-file mb-2">
                <v-chip small color="indigo" dark>{{ motFile.name }}</v-chip>
              </div>
              <div v-if="videoFile" class="selected-file mb-2">
                <v-chip small color="cyan" dark>{{ videoFile.name }}</v-chip>
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
              .json, .trc, .osim + .mot files, or video (mp4/webm) accepted
            </div>
          </div>
          
          <v-btn color="grey darken-3" dark class="mt-6" @click="loadSampleFiles" :disabled="converting">
            <v-icon left>mdi-play-circle</v-icon>
            Try with Sample Files
          </v-btn>
        </div>
      </div>

      <!-- Toggle button for sidebar -->
      <v-btn
        icon
        dark
        class="sidebar-toggle"
        @click="showSidebar = !showSidebar"
        :style="{ right: showSidebar ? '370px' : '10px' }"
        v-if="$route.query.embed !== 'true'"
      >
        <v-icon>{{ showSidebar ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
      </v-btn>

      <!-- Right Panel: Controls, Legend, etc. -->
      <div class="right d-flex flex-column" :class="{ 'hidden': !showSidebar }" v-if="$route.query.embed !== 'true'">
        <!-- Recording controls -->
        <div class="recording-controls mb-4">
          <!-- Video Recording Section -->
          <div class="recording-section mb-6 pa-3" style="background: rgba(0, 0, 0, 0.2); border-radius: 8px;">
            <div class="section-title mb-3" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">Video Recording</div>
            <!-- Record button row -->
            <div class="d-flex align-center mb-3">
              <v-btn v-if="!isRecording" color="#EF4444" dark @click="startRecording" :disabled="isRecording" class="custom-btn" style="flex: 1;">
                <v-icon left>mdi-record</v-icon>
                Record
              </v-btn>
              <v-btn v-else color="grey" dark @click="stopRecording" class="custom-btn" style="flex: 1;">
                <v-icon left>mdi-stop</v-icon>
                Stop
                <span v-if="loopCount !== Infinity" class="caption ml-1">({{ currentLoop }}/{{ loopCount }})</span>
              </v-btn>
            </div>
            
            <!-- Video options row -->
            <div class="d-flex align-center">
              <v-select
                v-model="loopCount"
                :items="[
                  {text: 'Infinite ∞', value: Infinity},
                  {text: '1 Loop', value: 1},
                  {text: '2 Loops', value: 2},
                  {text: '3 Loops', value: 3},
                  {text: '4 Loops', value: 4},
                  {text: '5 Loops', value: 5}
                ]"
                label="Loops"
                dense
                dark
                class="mr-2"
                hide-details
                :disabled="isRecording"
                style="flex: 1;"
              ></v-select>
              
              <v-select
                v-model="recordingFormat"
                :items="[{text: 'WebM', value: 'webm'}, {text: 'MP4', value: 'mp4'}]"
                label="Format"
                dense
                dark
                class="mr-2"
                hide-details
                :disabled="isRecording"
                style="flex: 1;"
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
                style="flex: 1;"
              ></v-select>
              
              <!-- Add info icon with tooltip -->
              <v-tooltip bottom max-width="300">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    icon
                    x-small
                    v-bind="attrs"
                    v-on="on"
                    class="ml-1"
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
          </div>

          <!-- Image Capture Section -->
          <div class="capture-section pa-3" style="background: rgba(0, 0, 0, 0.2); border-radius: 8px;">
            <div class="section-title mb-3" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">Image Capture</div>
            <!-- Capture button row -->
            <div class="d-flex align-center mb-3">
              <v-btn 
                color="#6B7280" 
                dark 
                @click="captureScreenshot" 
                class="custom-btn" 
                style="flex: 1;"
              >
                <v-icon left>mdi-camera</v-icon>
                Capture Image
              </v-btn>
            </div>
            
            <!-- Image options row -->
            <div class="d-flex align-center">
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
                hide-details
                style="flex: 1;"
              ></v-select>
            </div>
          </div>
        </div>

        <!-- File controls -->
        <div class="file-controls mb-4 position-relative">
          <!-- Show loading overlay when converting -->
          <div v-if="converting" class="conversion-overlay-small">
            <v-progress-circular indeterminate color="indigo" size="24" width="3" />
            <div class="ml-2">Converting files...</div>
          </div>
          
          <!-- Make controls slightly transparent when loading -->
          <div :class="{ 'opacity-reduced': converting }">
            <!-- Existing file inputs and buttons -->
            <input type="file" ref="fileInput" accept=".json,.trc" style="display: none" @change="handleFileUpload" multiple />
            <v-btn color="#4B5563" class="mb-2 white--text custom-btn" block @click="$refs.fileInput.click()" :disabled="converting">
              <v-icon left>mdi-file-upload</v-icon>
              Load JSON Files
            </v-btn>
            
            <!-- Add TRC file upload option -->
            <input type="file" ref="trcFileInput" accept=".trc" style="display: none" @change="handleTrcFileUpload" multiple />
            <v-btn color="#3B82F6" class="mb-2 white--text custom-btn" block @click="$refs.trcFileInput.click()" :disabled="converting">
              <v-icon left>mdi-file-upload-outline</v-icon>
              Load Markers (.trc)
            </v-btn>
            
            <input type="file" ref="osimMotFileInput" accept=".osim,.mot" style="display: none" @change="handleOpenSimFiles" multiple />
            <v-btn color="#6366F1" class="mb-2 white--text custom-btn" block @click="$refs.osimMotFileInput.click()" :disabled="converting">
              <v-icon left>mdi-file-upload-outline</v-icon>
              Load OpenSim (.mot+.osim)
            </v-btn>
            
            <!-- Add video file upload button -->
            <input type="file" ref="videoFileInput" accept="video/mp4,video/webm" style="display: none" @change="handleVideoUpload" />
            <v-btn color="#06B6D4" class="mb-2 white--text custom-btn" block @click="$refs.videoFileInput.click()">
              <v-icon left>mdi-video</v-icon>
              Load Video (mp4/webm)
            </v-btn>
            
            <!-- Existing file chips etc. -->
          </div>
        </div>

        <!-- Sync controls -->
        <div class="sync-controls mb-4">
          <v-btn color="#9CA3AF" class="mb-2 white--text custom-btn" block @click="syncAllAnimations">
            <v-icon left>mdi-sync</v-icon>
            Sync All Subjects
          </v-btn>
        </div>

        <!-- Scene color controls -->
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
                  <!-- Add Eyedropper button -->
                  <div class="mt-2 text-center">
                    <v-btn small icon @click.stop="openBackgroundEyedropper" title="Pick color from screen">
                      <v-icon small>mdi-eyedropper-variant</v-icon>
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
                  <!-- Add Eyedropper button -->
                  <div class="mt-2 text-center">
                    <v-btn small icon @click.stop="openGroundEyedropper" title="Pick color from screen" :disabled="!showGround">
                      <v-icon small>mdi-eyedropper-variant</v-icon>
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
            <!-- Add Light Intensity control here -->
            <div class="d-flex align-center ml-4 flex-grow-1">
              <div class="mr-2">Light:</div>
              <v-slider
                v-model="globalLightIntensity"
                min="0"
                max="3"
                step="0.1"
                thumb-label
                dense
                hide-details
                @input="updateGlobalLightIntensity"
                class="mt-0"
              ></v-slider>
            </div>
          </div>
          
        </div>

        <!-- Timelapse Controls -->
        <div class="timelapse-controls mb-4">
          <v-switch
            v-model="timelapseMode"
            label="Timelapse Mode"
            color="indigo"
            @change="toggleTimelapseMode"
          ></v-switch>
          <div v-if="timelapseMode" class="mt-2">
            <div class="d-flex align-center mb-2">
              <div class="text-subtitle-2">Frame Interval <span class="text-caption ml-2">({{ timelapseInterval }} frames)</span></div>
            </div>
            <v-slider
              v-model="timelapseInterval"
              min="1"
              max="30"
              step="1"
              thumb-label
              thumb-size="24"
              :disabled="!timelapseMode"
              @input="updateTimelapse"
              hide-details
              class="mb-4"
            >
              <template v-slot:thumb-label="{ value }">
                {{ value }}
              </template>
              <template v-slot:prepend>
                <div class="text-caption grey--text">1</div>
              </template>
              <template v-slot:append>
                <div class="text-caption grey--text">30</div>
              </template>
            </v-slider>

            <div class="d-flex align-center mb-2">
              <div class="text-subtitle-2">Model Transparency <span class="text-caption ml-2">({{ Math.round(timelapseOpacity * 100) }}%)</span></div>
            </div>
            <v-slider
              :value="timelapseOpacity * 100"
              @input="value => timelapseOpacity = value / 100"
              min="0"
              max="100"
              step="1"
              thumb-label
              thumb-size="24"
              :disabled="!timelapseMode"
              @change="updateTimelapseOpacity"
              hide-details
              class="mb-4"
            >
              <template v-slot:thumb-label="{ value }">
                {{ Math.round(value) }}%
              </template>
              <template v-slot:prepend>
                <div class="text-caption grey--text">0%</div>
              </template>
              <template v-slot:append>
                <div class="text-caption grey--text">100%</div>
              </template>
            </v-slider>
            <div class="d-flex justify-space-between align-center">
              <v-btn small text @click="clearTimelapse" class="mt-1">
                Clear All
              </v-btn>
              <v-btn small text @click="showTimelapseManager = true" class="mt-1">
                Manage Models
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Timelapse Manager Dialog -->
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

        <!-- Legend -->
        <div class="legend flex-grow-1 mb-4">
          <!-- Animation Files List -->
          <div v-for="(animation, index) in animations" :key="index" class="legend-item mb-2">
            <div class="d-flex align-center mb-2">
              <div class="color-box" :style="{ backgroundColor: '#' + colors[index].getHexString() }"></div>
              <div class="ml-2" style="width: 120px; min-width: 120px;">
                <v-text-field v-model="animation.trialName" dense hide-details class="trial-name-input" />
                <div class="file-name text-caption">{{ getFileName(animation) }}</div>
                <!-- Add FPS display here -->
                <div v-if="animation.calculatedFps" class="fps-info text-caption grey--text">
                  {{ animation.calculatedFps }} FPS
                </div>
              </div>
              <div class="d-flex align-center flex-grow-1">
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
                    <!-- Recent Colors Section -->
                    <div v-if="recentSubjectColors.length > 0" class="mt-3">
                      <div class="text-caption grey--text mb-1">Recent Colors</div>
                      <div class="d-flex flex-wrap">
                        <v-btn v-for="color in recentSubjectColors" :key="color" small icon class="ma-1" @click="updateSubjectColor(index, color)">
                          <div class="color-sample" :style="{ backgroundColor: color }"></div>
                        </v-btn>
                      </div>
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
                    <!-- Add Eyedropper button -->
                    <div class="mt-2 text-center">
                      <v-btn small icon @click.stop="openEyedropper(index)" title="Pick color from screen">
                        <v-icon small>mdi-eyedropper-variant</v-icon>
                      </v-btn>
                    </div>
                  </v-card>
                </v-menu>
                <v-btn icon small class="ml-2" @click="deleteSubject(index)">
                  <v-icon small color="error">mdi-delete</v-icon>
                </v-btn>
                <v-btn icon small class="ml-2" @click="toggleSubjectVisibility(index)">
                  <v-icon small :color="animations[index].visible ? 'white' : 'grey'">
                    {{ animations[index].visible ? 'mdi-eye' : 'mdi-eye-off' }}
                  </v-icon>
                </v-btn>
                <v-menu offset-y>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small v-bind="attrs" v-on="on" class="ml-2" @click="prepareTransparencyMenu(index)">
                      <v-icon small>mdi-opacity</v-icon>
                    </v-btn>
                  </template>
                  <v-card class="transparency-picker pa-3" width="250">
                    <div class="text-subtitle-2 mb-2">
                      Transparency
                      <span class="text-caption ml-2">
                        ({{ Math.round((1 - alphaValues[index]) * 100) }}%)
                      </span>
                    </div>
                    <v-slider 
                      :value="(1 - alphaValues[index]) * 100"
                      @input="value => updateAlpha(index, 1 - value / 100)"
                      :min="0" 
                      :max="100" 
                      step="1" 
                      hide-details 
                      :thumb-label="true"
                      thumb-size="24"
                    >
                      <template v-slot:thumb-label="{ value }">
                        {{ Math.round(value) }}%
                      </template>
                      <template v-slot:prepend>
                        <div class="text-caption grey--text">0%</div>
                      </template>
                      <template v-slot:append>
                        <div class="text-caption grey--text">100%</div>
                      </template>
                    </v-slider>
                  </v-card>
                </v-menu>

                <v-btn 
                  small 
                  text 
                  class="ml-2" 
                  v-if="animations[index].visible"
                  @click="openMeshDialog(index)"
                >
                  <v-icon left small>mdi-cube-outline</v-icon>
                  Meshes
                </v-btn>
              </div>
            </div>
            
            <!-- Offset controls -->
            <div class="offset-controls mt-1">
              <div class="d-flex align-center">
                <v-text-field label="X" type="number" :step="0.5" :value="animation.offset.x" dense @input="updateOffset(index, 'x', $event)" style="width: 70px" />
                <v-text-field label="Y" type="number" :step="0.5" :value="animation.offset.y" dense @input="updateOffset(index, 'y', $event)" style="width: 70px" />
                <v-text-field label="Z" type="number" :step="0.5" :value="animation.offset.z" dense @input="updateOffset(index, 'z', $event)" style="width: 70px" />
              </div>
            </div>

            <!-- Add mesh dialog -->
            <v-dialog
              v-model="meshDialogs[index]"
              max-width="400"
            >
              <v-card>
                <v-card-title class="text-subtitle-1">
                  Mesh Objects - {{ animation.trialName }}
                  <v-spacer></v-spacer>
                  <v-btn icon small @click="meshDialogs[index] = false">
                    <v-icon small>mdi-close</v-icon>
                  </v-btn>
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text class="pa-4">
                  <div class="mesh-groups">
                    <div v-for="(items, groupName) in getGroupedMeshes(index)" :key="groupName" class="mb-3">
                      <div class="group-header pa-2 d-flex align-center">
                        <v-btn icon x-small class="mr-2" @click="toggleGroupVisibility(index, groupName, items)">
                          <v-icon x-small>{{ isGroupVisible(items) ? 'mdi-eye' : 'mdi-eye-off' }}</v-icon>
                        </v-btn>
                        <strong>{{ groupName }}</strong>
                      </div>
                      <div v-for="item in items" :key="item.key" class="mesh-item d-flex align-center pa-2 pl-6">
                        <v-btn icon x-small @click="toggleMeshVisibility(item.key)">
                          <v-icon x-small :color="meshes[item.key] && meshes[item.key].visible !== false ? 'white' : 'grey'">
                            {{ meshes[item.key] && meshes[item.key].visible !== false ? 'mdi-eye' : 'mdi-eye-off' }}
                          </v-icon>
                        </v-btn>
                        <span class="ml-2">{{ item.name }}</span>
                      </div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-dialog>
          </div>

          <!-- Marker Files List -->
          <div v-for="(markerFile, markerIndex) in loadedMarkerFiles" :key="`marker-${markerIndex}`" class="legend-item mb-2">
              <div class="d-flex align-center mb-2">
                  <!-- Swatch using global markerColor -->
                  <div class="color-box" :style="{ backgroundColor: markerColor }"></div>
                  <div class="ml-2" style="width: 120px; min-width: 120px;">
                      <!-- Use v-model for trialName if editable, or just display -->
                      <v-text-field v-model="markerFile.trialName" dense hide-details class="trial-name-input" />
                      <div class="file-name text-caption">{{ markerFile.fileName }}</div>
                      <!-- Maybe add marker count here? -->
                      <div class="fps-info text-caption grey--text">
                          {{ Object.keys(markers).length }} Markers
                      </div>
                  </div>
                  <div class="d-flex align-center flex-grow-1">
                      <!-- Color Picker for Markers (1st) -->
                      <v-menu offset-y>
                          <template v-slot:activator="{ on, attrs }">
                              <v-btn icon small v-bind="attrs" v-on="on" class="ml-2">
                                  <v-icon small>mdi-palette</v-icon>
                              </v-btn>
                          </template>
                          <v-card class="color-picker pa-2">
                              <v-color-picker
                                  v-model="markerColor"
                                  hide-inputs
                                  hide-mode-switch
                                  @input="updateMarkerColor"
                              ></v-color-picker>
                          </v-card>
                      </v-menu>
                      <!-- Delete Button (2nd) -->
                      <v-btn icon small class="ml-2" @click="deleteMarkerFile(markerIndex)">
                          <v-icon small color="error">mdi-delete</v-icon>
                      </v-btn>
                      <!-- Visibility Toggle (3rd) -->
                      <v-btn icon small class="ml-2" @click="toggleMarkerVisibility">
                          <v-icon small :color="showMarkers ? 'white' : 'grey'">
                              {{ showMarkers ? 'mdi-eye' : 'mdi-eye-off' }}
                          </v-icon>
                      </v-btn>
                      <!-- Add Transparency Menu (4th) -->
                      <v-menu offset-y>
                          <template v-slot:activator="{ on, attrs }">
                              <v-btn icon small v-bind="attrs" v-on="on" class="ml-2">
                                  <v-icon small>mdi-opacity</v-icon>
                              </v-btn>
                          </template>
                          <v-card class="transparency-picker pa-3" width="250">
                              <div class="text-subtitle-2 mb-2">
                                  Marker Transparency
                                  <span class="text-caption ml-2">
                                      ({{ Math.round((1 - markerOpacity) * 100) }}%)
                                  </span>
                              </div>
                              <v-slider 
                                  :value="(1 - markerOpacity) * 100"
                                  @input="value => updateMarkerOpacity(1 - value / 100)"
                                  :min="0" 
                                  :max="100" 
                                  step="1" 
                                  hide-details 
                                  :thumb-label="true"
                                  thumb-size="24"
                              >
                                  <template v-slot:thumb-label="{ value }">
                                      {{ Math.round(value) }}%
                                  </template>
                                  <template v-slot:prepend>
                                      <div class="text-caption grey--text">0%</div>
                                  </template>
                                  <template v-slot:append>
                                      <div class="text-caption grey--text">100%</div>
                                  </template>
                              </v-slider>
                          </v-card>
                      </v-menu>
                      <!-- Markers List Button (5th) -->
                      <v-btn 
                          small 
                          text 
                          class="ml-2" 
                          v-if="Object.keys(markers).length > 0"
                          @click="showMarkerDialog = true"
                      >
                          <v-icon left small>mdi-vector-point</v-icon>
                          Markers
                      </v-btn>
                      <!-- Add Sync button at the end -->
                      <v-tooltip bottom v-if="animations.length > 0">
                          <template v-slot:activator="{ on, attrs }">
                              <v-btn icon small class="ml-2" @click="syncMarkersWithAnimations" v-bind="attrs" v-on="on">
                                  <v-icon small>mdi-sync</v-icon>
                              </v-btn>
                          </template>
                          <span>Sync Markers with Animations</span>
                      </v-tooltip>
                  </div>
              </div>
              <!-- No offset controls for markers -->
          </div>
        </div>

        <!-- Add Marker Visibility Dialog -->
        <v-dialog v-model="showMarkerDialog" max-width="400">
            <v-card>
                <v-card-title class="text-subtitle-1">
                    Marker Visibility
                    <v-spacer></v-spacer>
                    <v-btn icon small @click="showMarkerDialog = false">
                        <v-icon small>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text class="pa-4" style="max-height: 400px; overflow-y: auto;">
                    <div v-if="Object.keys(markers).length > 0">
                        <div v-for="(marker, name) in markers" :key="name" class="mesh-item d-flex align-center pa-1 pl-2">
                            <v-btn icon x-small @click="toggleSingleMarkerVisibility(name)">
                                <v-icon x-small :color="marker.visible !== false ? 'white' : 'grey'">
                                    {{ marker.visible !== false ? 'mdi-eye' : 'mdi-eye-off' }}
                                </v-icon>
                            </v-btn>
                            <span class="ml-2">{{ name }}</span>
                        </div>
                    </div>
                    <div v-else class="text-center grey--text">No markers loaded.</div>
                </v-card-text>
            </v-card>
        </v-dialog>

        <!-- Credits -->
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
                  new THREE.Color(0xd3d3d3),  // Changed from Green to Light Grey (211, 211, 211)
                  new THREE.Color(0x4995e0),  // Changed from Orange to RGB(73, 149, 224)
                  new THREE.Color(0xe35335),  // Changed from Red to RGB(227, 83, 53)
                  new THREE.Color(0x0000ff),  // Blue
                  new THREE.Color(0xffff00),  // Yellow
                  new THREE.Color(0xff00ff),  // Magenta
                  new THREE.Color(0x00ffff),  // Cyan
                  new THREE.Color(0x8000ff),  // Purple
              ],
              mediaRecorder: null,
              recordedChunks: [],
              isRecording: false,
              loopCount: Infinity, // Default to Infinite
              currentLoop: 0, // Stays 0 for infinite
              isLooping: true, // Add this for playback looping
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
              globalLightIntensity: 1.0, // Add global light intensity control
              lights: { hemisphere: null, directionals: [] }, // Store light references
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
              // Add TRC marker properties
              trcFile: null,
              markers: {},
              markerMeshes: {},
              markerSize: 0.02, // Default size for marker spheres (increased from 0.015)
              markerColor: '#ff0000', // Default color for markers (red)
              showMarkers: true, // Toggle to show/hide markers - **Ensure this defaults to true**
              markerScale: 1.0, // Scale factor for marker positions
              markerLight: null, // Remove this line
              markerTimeData: null, // Store marker time data
              markerOpacity: 1.0, // Add opacity control for markers
              // Video preview props
              videoFile: null,
              videoUrl: null,
              videoMinimized: false,
              videoDuration: 0,
              videoFrameRate: 30, // Default estimate
              videoPosition: { x: 20, y: 20 }, // Default position
              videoSize: { width: 300, height: 'auto' }, // Default size
              isDragging: false,
              isResizing: false,
              dragOffset: { x: 0, y: 0 },
              resizeStartPosition: { x: 0, y: 0 },
              resizeStartSize: { width: 0, height: 0 },
              showSidebar: true, // Add this line to control sidebar visibility
              meshDialogs: {}, // Add this line to store mesh dialog states
              recentSubjectColors: [], // Store recent colors used for subjects
              maxRecentColors: 8, // Maximum number of recent colors to store
              loadedMarkerFiles: [], // Add list to track loaded marker files
              showMarkerDialog: false, // Flag for the new marker visibility dialog
              markerLabels: {}, // Store marker label sprites
              activeMarkerLabel: null, // Track currently displayed label
              markerLabelTimeout: null, // For label auto-hide timeout
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
        console.log('Query params:', this.$route.query);

        // Load settings from localStorage first
        this.loadSettings();

        // Handle black and black_background parameters
        if (this.$route.query.black === 'true') {
            console.log('Setting black background AND hiding ground due to black=true');
            this.backgroundColor = '#000000';
            this.showGround = false; // Only hide ground for black=true
        } else if (this.$route.query.black_background === 'true') {
            console.log('Setting black background ONLY due to black_background=true');
            this.backgroundColor = '#000000';
            // Leave this.showGround as loaded from settings or default
        }

        // Add keyboard event listeners
        window.addEventListener('keydown', this.handleKeyDown);

        // Initialize the scene first
        this.initScene(); // initScene will now call applyLoadedSceneSettings

        // Determine if we need to load samples and which set
        let sampleSetToLoad = null;
        if (this.$route.query.sample_set && ['squat', 'walk', 'STS', 'rmasb'].includes(this.$route.query.sample_set)) {
            sampleSetToLoad = this.$route.query.sample_set;
            console.log(`Query parameter found, loading sample set: ${sampleSetToLoad}`);
        } else if (this.$route.query.load_samples === 'true') {
            sampleSetToLoad = 'STS'; // Default set for the generic query
            console.log('Generic load_samples query found, loading default set: STS');
        } else if (this.$route.path === '/samples' || this.$route.path === '/samples/') {
            sampleSetToLoad = 'STS'; // Default set for the /samples route
            console.log('/samples route found, loading default set: STS');
        }

        if (sampleSetToLoad) {
            console.log(`Loading sample set: ${sampleSetToLoad}`);
            // Add a small delay to ensure scene is fully initialized
            setTimeout(() => {
                this.loadSampleFiles(sampleSetToLoad);
            }, 100);
        }
        
        // Add message listener for iframe communication
        window.addEventListener('message', this.handleIframeMessage);
    },
    beforeDestroy() {
      // Clean up video URL
      if (this.videoUrl) {
        URL.revokeObjectURL(this.videoUrl);
      }
      
      if (this.resizeObserver) {
        this.resizeObserver.unobserve(this.$refs.mocap)
      }
      
      // Clean up sprites
      Object.values(this.textSprites).forEach(sprite => {
          if (sprite.material.map) sprite.material.map.dispose();
          if (sprite.material) sprite.material.dispose();
      });
      
      // Clean up marker labels
      Object.values(this.markerLabels).forEach(label => {
          if (label.material.map) label.material.map.dispose();
          if (label.material) label.material.dispose();
      });
      
      // Remove double-click event listener
      if (this.renderer && this.renderer.domElement) {
          this.renderer.domElement.removeEventListener('dblclick', this.handleMarkerDoubleClick);
      }
      
      // Remove message listener
      window.removeEventListener('message', this.handleIframeMessage);

      // Remove keyboard event listener
      window.removeEventListener('keydown', this.handleKeyDown);
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
        
        // Handle black and black_background parameters
        if (to.query.black === 'true') {
            console.log('Setting black background AND hiding ground due to black=true');
            this.backgroundColor = '#000000';
            this.showGround = false; // Hide ground for black=true
            // Apply settings immediately if scene exists
            if (this.scene) {
                this.scene.background = new THREE.Color(this.backgroundColor);
                if (this.groundMesh) {
                    this.groundMesh.visible = false;
                }
                this.renderer.render(this.scene, this.camera);
            }
        } else if (to.query.black_background === 'true') {
            console.log('Setting black background ONLY due to black_background=true');
            this.backgroundColor = '#000000';
            // Apply settings immediately if scene exists
            if (this.scene) {
                this.scene.background = new THREE.Color(this.backgroundColor);
                // Do NOT change ground visibility here
                this.renderer.render(this.scene, this.camera);
            }
        }
        
        if (to.path === '/samples' || to.path === '/samples/') {
          console.log('Loading sample files from route watcher');
          // Add a small delay to ensure scene is ready
          setTimeout(() => {
            this.loadSampleFiles();
          }, 100);
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
                    trialName: 'Subject 1',
                    calculatedFps: 0 // Add this line
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
                    trialName: 'Subject 2',
                    calculatedFps: 0 // Add this line
                });
                this.initializeAlphaValue(1);
            }
            
            // Calculate and set frame rate from the JSON file's time data
            this.frameRate = this.calculateFrameRate(res1.data.time);
            // Store FPS for the first animation
            this.animations[0].calculatedFps = this.frameRate;
            // Calculate and store FPS for the second animation if it exists
            if (this.animations.length > 1) {
              this.animations[1].calculatedFps = this.calculateFrameRate(this.animations[1].data.time);
            }

              this.$nextTick(() => {
                try {
                  console.log('Setting up 3D scene')
                  // while (this.$refs.mocap.lastChild) { // Keep this if needed for clearing, or remove if initScene handles it
                  //   this.$refs.mocap.removeChild(this.$refs.mocap.lastChild)
                  // }
                  
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
                                              transparent: false, // Default to opaque
                                              opacity: 1.0 // Default to fully opaque
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
        // Always schedule the next frame first
        requestAnimationFrame(this.animate);

        // If not playing, just render the current state and exit
        if (!this.playing) {
          if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
          }
          return;
        }

        // Calculate time since last frame
        const currentTime = performance.now();
        const deltaTime = (currentTime - this.lastFrameTime) / 1000; // Convert to seconds

        // Check if we have markers or animations to animate
        const hasContent = this.animations.length > 0 || Object.keys(this.markers).length > 0;

        // Only advance frames if playing, enough time passed, and content exists
        if (deltaTime >= (1 / this.frameRate) && hasContent) {
            const framesToAdvance = Math.floor(deltaTime * this.frameRate * this.playSpeed);

            if (framesToAdvance > 0) {
                let nextFrame = this.frame + framesToAdvance;
                let loopNeedsReset = false;

                // Check for loop completion *only* if recording AND loopCount is finite
                if (this.isRecording && this.loopCount !== Infinity && nextFrame >= this.frames.length) {
                    console.log(`Animate: Loop end detected. Loop ${this.currentLoop}/${this.loopCount}. Frame ${this.frame} -> ${nextFrame}`);
                    if (this.currentLoop < this.loopCount) {
                        this.currentLoop++;
                        console.log(`Animate: Starting loop ${this.currentLoop}.`);
                        // Reset frame to 0 for the new loop start
                        nextFrame = 0;
                        loopNeedsReset = true;
                    } else {
                        console.log('Animate: All loops completed. Stopping recording.');
                        // Set frame to the last frame before stopping
                        this.frame = this.frames.length - 1;
                        this.time = parseFloat(this.frames[this.frame]).toFixed(2);
                        this.animateOneFrame(); // Render the final frame
                        this.stopRecording(); 
                        this.playing = false; // Force playing to false immediately
                        // Since stopRecording sets this.playing = false, the check at the
                        // start of the next animate call will prevent further frame advancement.
                        return; // Exit this specific animate cycle
                    }
                } else if (nextFrame >= this.frames.length) {
                    // If not recording OR loopCount is Infinite, check playback looping
                    if (this.isLooping) {
                      // Loop back normally using modulo
                      nextFrame = nextFrame % this.frames.length;
                    } else {
                      // If not looping, stop at the last frame
                      nextFrame = this.frames.length - 1;
                      this.playing = false; // Stop playback
                    }
                }
                // If nextFrame < this.frames.length, it's a normal advance.

                // Update the frame
                this.frame = nextFrame;

                // Update lastFrameTime
                this.lastFrameTime = currentTime - (deltaTime - (framesToAdvance / (this.frameRate * this.playSpeed))) * 1000;

                // Update displayed time
                if (this.frames[this.frame] !== undefined) {
                    this.time = parseFloat(this.frames[this.frame]).toFixed(2);
                } else {
                    this.time = parseFloat(this.frame / this.frameRate).toFixed(2);
                }
                
                // Render the current frame
                this.animateOneFrame();

                // If a loop was just completed and we are starting the next one
                if (loopNeedsReset) {
                    // Ensure onNavigate syncs things like video if needed
                    this.onNavigate(this.frame); 
                }
            }
        } else if (!this.playing || !hasContent) {
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
          
          // Update marker positions if we have marker data
          if (Object.keys(this.markers).length > 0 && this.showMarkers) {
            this.updateMarkerPositions(cframe);
          }
        }
      },
      
      updateMarkerPositions(frame) {
        // Only update if we have markers
        if (Object.keys(this.markers).length === 0) {
            return;
        }
        
        // Update position of each marker for the current frame
        Object.keys(this.markers).forEach(markerName => {
            const marker = this.markers[markerName]; // Get marker data (including visibility)
            const mesh = this.markerMeshes[markerName]; // Get the mesh
            
            if (mesh) {
                let dataIsValid = false;
                if (frame < marker.positions.length) {
                    const pos = marker.positions[frame];
                    dataIsValid = pos && pos.x !== null && pos.y !== null && pos.z !== null;
                    
                    if (dataIsValid) {
                        // Apply scale factor to position
                        mesh.position.set(
                            pos.x * this.markerScale,
                            pos.y * this.markerScale,
                            pos.z * this.markerScale
                        );
                    }
                }
                
                // Set visibility based on global toggle, individual toggle, AND data validity
                mesh.visible = this.showMarkers && marker.visible !== false && dataIsValid;
            }
        });
    },
    togglePlay(value) {
        // Call the original method implementation
        this.playing = value;
        if (this.playing) {
          // Reset timing references when starting playback
          this.lastFrameTime = performance.now();
          
          // Make sure first frame gets displayed immediately
          this.animateOneFrame();
        } else if (this.isRecording) {
          this.playing = true;
        }
        
        // Add video playback control with proper error handling
        if (this.videoFile && this.$refs.videoPreview) {
          try {
            if (value) {
              const playPromise = this.$refs.videoPreview.play();
              if (playPromise !== undefined) {
                playPromise.catch(error => {
                  console.log('Video playback error:', error);
                  // Don't throw the error, just log it
                });
              }
            } else {
              this.$refs.videoPreview.pause();
            }
          } catch (error) {
            console.log('Video control error:', error);
          }
        }
        
        // Send play/pause state to parent window if running in an iframe
        if (window.parent && window.parent !== window) {
          try {
            parent.postMessage({ type: value ? 'play' : 'pause' }, '*'); // Use targetOrigin '*' or specify parent domain
          } catch (error) {
            console.error('Error sending message to parent:', error);
          }
        }
      },
      onNavigate(frame) {
        // Update frame and time
        this.frame = frame;
        if (this.frames[frame] !== undefined) {
            this.time = parseFloat(this.frames[frame]).toFixed(2);
        } else {
            this.time = parseFloat(frame / this.frameRate).toFixed(2);
        }
        
        // Render the frame without advancing
        this.animateOneFrame();
        
        // Sync video playback position with proper error handling
        if (this.videoFile && this.$refs.videoPreview) {
          try {
            const totalFrames = this.frames.length - 1;
            const videoTimePosition = (frame / totalFrames) * this.videoDuration;
            this.$refs.videoPreview.currentTime = videoTimePosition;
          } catch (error) {
            console.log('Video sync error:', error);
          }
        }
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
      
      // Reset to beginning when starting recording
      this.frame = 0;
      this.onNavigate(0);
      
      const canvas = this.renderer.domElement;
      const stream = canvas.captureStream(this.frameRate);
      
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
          videoBitsPerSecond: this.videoBitrate
        });
      } catch (error) {
        console.warn(`${mimeType} not supported, falling back to webm format`, error);
        this.recordingFormat = 'webm';
        this.recordingFileName = 'animation-recording.webm';
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'video/webm;codecs=vp9',
          videoBitsPerSecond: this.videoBitrate
        });
      }
      
      this.recordedChunks = [];
      // Only reset currentLoop if not in infinite mode
      if (this.loopCount !== Infinity) {
        this.currentLoop = 1;
      } else {
        this.currentLoop = 0; // Keep it 0 for infinite
      }
      
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
        this.currentLoop = 0;
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
        this.mediaRecorder.stop(); // This triggers the onstop event handler eventually
        this.isRecording = false;
        this.playing = false; // Explicitly stop playback
        this.currentLoop = 0;
        console.log('stopRecording called. isRecording and playing set to false.');
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

                // Calculate FPS for this specific file
                const fileFps = this.calculateFrameRate(data.time);

                this.animations.push({
                    data: data,
                    offset: offset,
                    fileName: file.name,
                    trialName: `Subject ${startIndex + index + 1}`,
                    visible: true,  // Add this line
                    calculatedFps: fileFps // Store calculated FPS
                });

                if (this.animations.length === 1) {
                    this.frames = data.time;
                    this.trial = { results: [] };
                    // Set the global frameRate based on the first file loaded
                    this.frameRate = fileFps;
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
                                            transparent: false, // Default to opaque
                                            opacity: 1.0 // Default to fully opaque
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
        const planeSize = 12; // Reduced size
        const loader = new THREE.TextureLoader();
        const texture = loader.load('https://threejsfundamentals.org/threejs/resources/images/checker.png');
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.magFilter = THREE.NearestFilter;
        const repeats = planeSize; // Use the new planeSize for repeats
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
        const intensity = 0.1; // Base intensity for hemisphere light
        const hemisphereLight = new THREE.HemisphereLight(skyColor, groundColor, intensity * this.globalLightIntensity);
        this.scene.add(hemisphereLight);
        this.lights.hemisphere = hemisphereLight; // Store reference

        // Add four directional lights from corners
        const cornerPositions = [
            { x: 10, y: 10, z: 10 },
            { x: -10, y: 10, z: 10 },
            { x: 10, y: 10, z: -10 },
            { x: -10, y: 10, z: -10 }
        ];
        const lightIntensity = 0.5; // Base intensity for directional lights
        const lightColor = 0xFFFFFF;

        this.lights.directionals = []; // Clear previous references
        cornerPositions.forEach(pos => {
            const directionalLight = new THREE.DirectionalLight(lightColor, lightIntensity * this.globalLightIntensity);
            directionalLight.position.set(pos.x, pos.y, pos.z);
            directionalLight.target.position.set(0, 0, 0);
            directionalLight.castShadow = false; // Disable shadows for performance initially
            this.scene.add(directionalLight);
            this.scene.add(directionalLight.target);
        });

        // Initial render
        this.renderer.render(this.scene, this.camera);

        // Apply loaded settings *after* scene is fully initialized
        console.log('[initScene] Calling applyLoadedSceneSettings() at the end of initScene.');
        this.applyLoadedSceneSettings();
    },
    onChangeTime(time) {
        // Round the time value to 2 decimal places
        this.time = parseFloat(time).toFixed(2);
        this.frame = Math.floor(time * this.frameRate);
        this.animateOneFrame();
    },
    syncAllAnimations() {
        if (this.animations.length <= 1 && !this.markerTimeData) return;

        // Find the latest start time and earliest end time across all animations and markers
        let latestStart = -Infinity;
        let earliestEnd = Infinity;
        let smallestTimeStep = Infinity;

        // First pass: find time boundaries and smallest time step from animations
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
        
        // Also consider marker time data if available
        if (this.markerTimeData && this.markerTimeData.times.length > 0) {
            const markerTimes = this.markerTimeData.times;
            const markerStartTime = markerTimes[0];
            const markerEndTime = markerTimes[markerTimes.length - 1];
            
            latestStart = Math.max(latestStart, markerStartTime);
            earliestEnd = Math.min(earliestEnd, markerEndTime);
            
            // Find smallest time step in marker data
            for (let i = 1; i < markerTimes.length; i++) {
                const timeStep = markerTimes[i] - markerTimes[i-1];
                if (timeStep > 0) {
                    smallestTimeStep = Math.min(smallestTimeStep, timeStep);
                }
            }
            
            console.log(`Including marker data in sync - Marker times: ${markerTimes.length}`);
        }

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
        
        // Sync marker data if available
        if (this.markerTimeData && Object.keys(this.markers).length > 0) {
            console.log('Resampling marker data to common timeline');
            this.syncMarkerDataToTimeline(this.markerTimeData.times);
        }

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
        // Add color to recent colors if it's not 'original'
        if (colorHex !== 'original' && !this.recentSubjectColors.includes(colorHex)) {
            // Add new color to the beginning of the array
            this.recentSubjectColors.unshift(colorHex);
            // Keep only the maximum number of recent colors
            if (this.recentSubjectColors.length > this.maxRecentColors) {
                this.recentSubjectColors.pop();
            }
            this.saveSettings(); // Save after updating recent colors
        }

        if (colorHex === 'original') {
            // Remove color override, revert to original material
            Object.keys(this.meshes).forEach(key => {
                if (key.startsWith(`anim${index}_`)) {
                    const mesh = this.meshes[key];
                    mesh.traverse((child) => {
                        if (child instanceof THREE.Mesh) {
                            child.material = new THREE.MeshPhongMaterial({ 
                                color: 0xcccccc,  // Default grey color
                                transparent: false, // Revert to opaque
                                opacity: 1.0 // Revert to fully opaque
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
                            // Keep current transparency settings when changing color
                            // child.material.transparent = this.alphaValues[index] < 1.0;
                            child.material.opacity = this.alphaValues[index];
                            child.material.transparent = this.alphaValues[index] < 1.0; // Set transparent based on alpha
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
      event.preventDefault();
      
        const files = Array.from(event.dataTransfer.files);
        
        // Separate files by type
        const markerFiles = files.filter(file => {
          const lowerCaseName = file.name.toLowerCase();
          return lowerCaseName.endsWith('.json') || lowerCaseName.endsWith('.trc');
        });
        const osimFiles = files.filter(file => file.name.toLowerCase().endsWith('.osim'));
        const motFiles = files.filter(file => file.name.toLowerCase().endsWith('.mot'));
      const videoFiles = files.filter(file => file.type === 'video/mp4' || file.type === 'video/webm');
      
      // Handle video files
      if (videoFiles.length > 0) {
        this.videoFile = videoFiles[0];
        this.videoUrl = URL.createObjectURL(this.videoFile);
      }
        
        // Handle JSON and TRC files directly
        if (markerFiles.length > 0) {
            const dataTransfer = new DataTransfer();
            markerFiles.forEach(file => dataTransfer.items.add(file));

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
        
      if (files.length === 0 || (markerFiles.length === 0 && osimFiles.length === 0 && motFiles.length === 0 && videoFiles.length === 0)) {
        console.warn('Please drop JSON, TRC, OSIM, MOT, or video files');
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
    loadSampleFiles(sampleSet = 'STS') { // Default to 'STS' if no set is provided
        console.log(`loadSampleFiles called for set: ${sampleSet}`);
        
        // Validate sample set name, default to 'STS' if invalid
        const validSets = ['squat', 'walk', 'STS', 'rmasb']; // Added rmasb here too
        if (!validSets.includes(sampleSet)) {
            console.warn(`Invalid sample set "${sampleSet}" provided. Defaulting to 'STS'.`);
            sampleSet = 'STS';
        }

        // Define the URLs for the sample files relative to the root and the specific set
        const sampleFiles = [
            `/samples/${sampleSet}/sample_mocap.json`,
            `/samples/${sampleSet}/sample_mono.json`,
            `/samples/${sampleSet}/sample_wham.json`
        ];
        
        console.log('Attempting to fetch potential sample files:', sampleFiles);

        // Show loading indicator
        this.trialLoading = true;
        
        // Clear existing animations before loading new ones
        this.animations = [];
        this.clearExistingObjects(); // Clear meshes and sprites from previous loads
        
        // Fetch all potential sample files, handling individual failures
        Promise.all(sampleFiles.map(url => 
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        // Log warning but don't throw error, return null to indicate failure
                        console.warn(`Sample file not found or failed to load: ${url} (${response.status})`);
                        return null; 
                    }
                    // If response is OK, parse JSON and pair with URL
                    return response.json().then(data => ({ data, url }));
                })
                .catch(error => {
                    // Catch network or other fetch errors
                    console.warn(`Error fetching sample file ${url}:`, error);
                    return null; // Indicate failure
                })
        ))
        .then(results => {
            // Filter out null results (failed fetches)
            const successfulResults = results.filter(r => r !== null);

            console.log(`Successfully loaded ${successfulResults.length} sample files.`);

            // If no files were loaded successfully, show an error or message
            if (successfulResults.length === 0) {
                console.error('No valid sample files found for set:', sampleSet);
                alert(`Could not load any sample files for the set: ${sampleSet}. Please check the /public/samples/${sampleSet} folder.`);
                this.trialLoading = false;
                return; // Stop processing
            }

            // Process the successfully loaded files
            successfulResults.forEach(({ data, url }, index) => {
                // Get the filename from the URL
                const fileName = url.split('/').pop();
                
                // Calculate FPS for this specific file
                const fileFps = this.calculateFrameRate(data.time);

                // Create animation data with better names
                this.animations.push({
                    data: data,
                    offset: new THREE.Vector3(0, 0, 0),
                    fileName: fileName,
                    trialName: fileName.replace('sample_', '').replace('.json', ''),
                    visible: true,  // Ensure visibility is true by default
                    calculatedFps: fileFps // Store calculated FPS
                });
                
                // Set up the trial and frames from the *first successfully loaded* animation
                if (index === 0) {
                    this.frames = data.time;
                    this.trial = { results: [] };
                    // Set the global frameRate based on the first sample file loaded
                    this.frameRate = this.animations[0].calculatedFps;
                    console.log(`Using timeline and frame rate from: ${fileName}`);
                }
            });
            
            // Force Vue to update the DOM before proceeding
            this.$nextTick(() => {
                // Initialize the scene if needed
                if (!this.scene || !this.renderer) {
                    console.log('Initializing scene for sample files...');
                    // Clear the container first (should be handled by clearExistingObjects if needed)
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
                    // Scene already exists, just load geometries
                    console.log('Scene already exists, loading geometries for new samples...');
                    this.loadGeometriesForSamples();
                }
            });
        })
        .catch(error => {
            // This catch is for potential errors in the processing logic after Promise.all
            console.error('Error processing sample files:', error);
            this.trialLoading = false;
            alert('An unexpected error occurred while processing sample files.');
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
                                    transparent: false, // Default to opaque
                                    opacity: 1.0 // Default to fully opaque
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
        console.log(`[updateBackgroundColor] Method called with color: ${color}`); // Add log here
        if (this.scene) {
            this.scene.background = new THREE.Color(color);
            this.renderer.render(this.scene, this.camera);
        }
        this.saveSettings(); // Explicitly save
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
        this.saveSettings(); // Explicitly save
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
        this.saveSettings(); // Explicitly save
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
        this.saveSettings(); // Explicitly save
    },
    toggleGroundVisibility() {
        // We need to update the data property first for the watcher/save to work
        this.showGround = !this.showGround;

        if (this.groundMesh) {
            this.groundMesh.visible = this.showGround;
            this.renderer.render(this.scene, this.camera);
        }
        // Watcher should handle saving now that this.showGround is updated
        this.saveSettings(); // Let watcher handle this one as example
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
        this.saveSettings(); // Save light intensity setting
    },
    updateAlpha(animationIndex, value) {
        // Update the alpha value for the specified animation
        console.log(`[updateAlpha] Updating alpha for index ${animationIndex} to ${value}`);
        this.$set(this.alphaValues, animationIndex, value); // Use $set for reactivity

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
        this.saveSettings(); // Save light intensity setting
    },
    initializeAlphaValue(index) {
        // Set default opacity to 0.8, which matches what we set when creating materials
        if (this.alphaValues[index] === undefined) { // Check specifically for undefined
            this.$set(this.alphaValues, index, 1.0); // Default to 1.0 (fully opaque)
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
        
        // Save references to marker meshes before clearing
        const markerKeys = Object.keys(this.markerMeshes);
        console.log(`Preserving ${markerKeys.length} marker meshes during geometry cleanup`);
        
        // Process all scene objects and dispose geometries and materials
        this.scene.traverse(object => {
            // Skip marker meshes - we want to keep them
            if (markerKeys.length > 0 && Object.values(this.markerMeshes).includes(object)) {
                return;
            }
            
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
        
        // Reset meshes and text sprites but keep marker meshes
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
    handleTrcFileUpload(event) {
        const files = event.target.files;
        if (!files.length) return;

        // Initialize scene if it doesn't exist or reinitialize it
        if (!this.scene) {
            console.log('Initializing scene for TRC file');
            this.initScene();
        }

        // Only support one TRC file at a time for now
        const trcFile = files[0];
        this.trcFile = trcFile;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            // Parse TRC file content
            this.parseTrcFile(e.target.result);
        };
        reader.readAsText(trcFile);

        // Clear the file input value so the same file can be selected again
        event.target.value = '';
    },

    parseTrcFile(trcContent) {
        console.log('Parsing TRC file...');
        
        // Clear any existing marker meshes
        this.clearMarkers();

        // Initialize trial data first
        if (!this.trial) {
            this.trial = { results: [] };
        }

        // Initialize scene if it doesn't exist
        if (!this.scene) {
            console.log('Initializing scene for TRC file');
            this.initScene();
            
            // Wait for scene initialization to complete
            this.$nextTick(() => {
                // Set initial camera position for better marker viewing
                if (this.camera) {
                    this.camera.position.set(3.33, 3.5, -2.30);
                    this.camera.lookAt(0, 1, 0);
                }
                
                // Continue with TRC parsing after scene is initialized
                this.processTrcContent(trcContent);
            });
            return;
        }

        // If scene already exists, proceed directly
        this.processTrcContent(trcContent);
    },

    processTrcContent(trcContent) {
        const lines = trcContent.split('\n');
        let dataHeaderLineIndex = -1;
        let columnNames = [];
        let xyzLabelsLineIndex = -1;
        let dataStartLineIndex = -1;
        let frameTimeIndex = -1;
        let dataRows = [];
        let frameTimes = [];
        
        console.log(`TRC file contains ${lines.length} lines`);
        
        // First pass: find the data section marker lines (Frame# and coordinate labels)
        console.log("--- TRC Header Inspection Start ---");
        for (let i = 0; i < Math.min(20, lines.length); i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            // Log the header line being checked
            console.log(`Inspecting Header Line ${i}: ${line}`);
            
            // Look for the line with "Frame" and "Time" which indicates column headers
            if (line.match(/Frame#?\s+Time/i)) {
                dataHeaderLineIndex = i;
                console.log(`Found column header line at index ${i}`);
                
                // The next line usually contains X1 Y1 Z1 etc.
                if (i+1 < lines.length && lines[i+1].trim().match(/X\d*\s+Y\d*\s+Z\d*/i)) {
                    xyzLabelsLineIndex = i+1;
                    console.log(`Found XYZ labels line at index ${i+1}`);
                    dataStartLineIndex = i+2; // Data starts after the XYZ labels
                    console.log(`XYZ Labels Line Content: ${lines[xyzLabelsLineIndex]}`);
                } else {
                    dataStartLineIndex = i+1; // Data starts right after headers
                }
                
                break;
            }
        }
        
        if (dataHeaderLineIndex === -1) {
            console.error('Could not find data header line with Frame# and Time');
            return;
        }
        
        // Extract column names from the header line
        columnNames = lines[dataHeaderLineIndex].split(/[\t\s]+/).filter(name => name.trim().length > 0);
        console.log(`Data Header Line Content: ${lines[dataHeaderLineIndex]}`);
        console.log('Extracted Column Names:', columnNames);
        
        // Find the index of the time column
        frameTimeIndex = columnNames.indexOf('Time');
        if (frameTimeIndex === -1) {
            frameTimeIndex = columnNames.findIndex(col => 
                ['time', 'TIME', 'Times', 'times', 't'].includes(col));
        }
        console.log('Time column index:', frameTimeIndex);
        
        // Process data rows
        for (let i = dataStartLineIndex; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || !line.match(/^\d/)) continue; // Skip empty lines or non-data lines
            
            // Split data by tabs or multiple spaces
            const values = line.split(/[\t\s]+/).filter(val => val.trim().length > 0);
            
            // Extract time value if available
            if (frameTimeIndex !== -1 && frameTimeIndex < values.length) {
                frameTimes.push(parseFloat(values[frameTimeIndex]));
            } else if (values.length > 1) {
                // If we couldn't find a time column, use the second column (often time)
                frameTimes.push(parseFloat(values[1]));
            }
            
            dataRows.push(values);
        }
        
        console.log(`Parsed ${dataRows.length} data rows`);
        console.log(`Found ${columnNames.length} columns`);
        console.log("--- TRC Header Inspection End ---");
        
        if (dataRows.length === 0) {
            console.error('No data rows found in TRC file');
            return;
        }
        
        // Get XYZ coordinate labels if they exist
        let xyzLabels = [];
        if (xyzLabelsLineIndex !== -1) {
            xyzLabels = lines[xyzLabelsLineIndex].split(/[\t\s]+/).filter(label => label.trim().length > 0);
            console.log('XYZ labels:', xyzLabels);
        }
        
        // Process the marker data to create marker objects
        this.markers = {};
        
        // Store the original time array for marker data
        this.markerTimeData = {
            times: frameTimes,
            fileName: this.trcFile ? this.trcFile.name : 'markers.trc'
        };

        // Initialize scene if it doesn't exist
        if (!this.scene) {
            console.log('Initializing scene for TRC file');
            this.initScene();
        }

        // Ensure ground plane exists if scene exists but ground doesn't
        if (this.scene && !this.groundMesh) {
            console.log('Adding ground plane for markers');
            const planeSize = 20;
            const planeGeo = new THREE.PlaneGeometry(planeSize, planeSize);
            const planeMat = new THREE.MeshPhongMaterial({
                map: this.useGroundTexture ? this.groundTexture : null,
                side: THREE.DoubleSide,
                color: new THREE.Color(this.groundColor)
            });
            this.groundMesh = new THREE.Mesh(planeGeo, planeMat);
            this.groundMesh.rotation.x = Math.PI * -.5;
            this.groundMesh.position.y = 0;
            this.scene.add(this.groundMesh);
        }

        // Ensure markers are shown by default
        this.showMarkers = true;
        
        // Determine marker columns and their X,Y,Z patterns
        // Skip Frame# and Time columns (first two)
        const markerCount = columnNames.length - 2; // Use the actual number of names found
        console.log(`Using actual marker count from header: ${markerCount}`);
        
        // Process each marker
        for (let i = 0; i < markerCount; i++) {
            const xCol = 2 + (i * 3);       // X data column index in the data rows
            const yCol = xCol + 1;           // Y data column index
            const zCol = xCol + 2;           // Z data column index

            // Get the marker name using the direct index from the cleaned column names array
            const markerNameFromHeader = columnNames[2 + i]; 
            console.log(`[Marker ${i}] Name from Header Index ${2 + i}: "${markerNameFromHeader}"`);

            // Check if we have enough data columns for this marker index
            // Note: We compare zCol against the number of values found in the *first* data row as a proxy 
            // for expected data columns, as the header might be misleading due to spacing.
            if (dataRows.length > 0 && zCol >= dataRows[0].length) {
                console.warn(`[Marker ${i}] Not enough data columns found in data rows for marker index ${i} (Name: ${markerNameFromHeader}). Expected column ${zCol}, but found ${dataRows[0].length}. Skipping.`);
                continue;
            }

            // Use the name extracted directly from the header array
            let markerName = markerNameFromHeader; 

            // Initialize marker data structure
            this.markers[markerName] = {
                positions: [],
                originalPositions: [] // Store the original positions for resampling
            };

            // Extract positions for this marker across all frames
            for (let rowIndex = 0; rowIndex < dataRows.length; rowIndex++) {
                const row = dataRows[rowIndex];

                // Make sure we have enough columns in this specific row for data extraction
                if (zCol < row.length) {
                    // XYZ coordinates for this marker in this frame
                    const x = parseFloat(row[xCol]);
                    const y = parseFloat(row[yCol]);
                    const z = parseFloat(row[zCol]);

                    // Create position object
                    const pos = {
                        x: isNaN(x) ? null : x,
                        y: isNaN(y) ? null : y,
                        z: isNaN(z) ? null : z
                    };

                    // Add to marker positions, checking for NaN values
                    this.markers[markerName].positions.push({...pos});
                    // Also store in original positions
                    this.markers[markerName].originalPositions.push({...pos});
                } else {
                    // Add null position if row doesn't have enough data
                    const nullPos = { x: null, y: null, z: null };
                    this.markers[markerName].positions.push({...nullPos});
                    this.markers[markerName].originalPositions.push({...nullPos});
                }
            }
        }

        console.log(`[parseTrcFile] Finished processing all potential markers based on header names. Found ${Object.keys(this.markers).length} markers.`);
        console.log('[parseTrcFile] Marker keys found:', Object.keys(this.markers));

        // --- Move this block UP --- 
        // Add marker data to the list of loaded marker files *before* checking if markers were found
        // This ensures the file appears in the list even if parsing fails
        this.loadedMarkerFiles.push({
            fileName: this.trcFile.name,
            trialName: this.trcFile.name.replace('.trc', ''), // Basic name derivation
        });
        console.log('[parseTrcFile] Added marker file to loadedMarkerFiles:', JSON.stringify(this.loadedMarkerFiles));
        // --- End Moved Block --- 

        // If no markers were found, something went wrong
        if (Object.keys(this.markers).length === 0) {
            console.error('[parseTrcFile] No valid markers found in TRC file. Stopping further marker processing (meshes, sync). File entry was still added to the list.');
            // We don't return here anymore, but subsequent steps depending on markers might fail
            // The functions createMarkerMeshes and syncMarkerDataToTimeline already handle empty markers gracefully.
        }

        // Handle different scenarios for timeline integration
        if (!this.trial || !this.frames.length) {
            // Case 1: First data loaded - use the TRC file's timeline
            console.log('Setting up animation timing from TRC file');
            this.frames = frameTimes;
            this.trial = { results: [] };
            this.frameRate = this.calculateFrameRate(frameTimes);
        } else if (this.animations.length > 0) {
            // Case 2: Animation data already exists - sync the markers to it
            console.log('Syncing marker data with existing animation timeline');
            this.syncMarkerDataToTimeline(frameTimes);
        } else {
            // Case 3: We have a timeline but no animations - just add marker data
            console.log('Adding marker data to existing timeline');
            // Handle case where we want to merge with existing frames
            // This would happen if loading multiple TRC files
            if (this.frames.length > 0 && this.frames[0] !== frameTimes[0]) {
                this.syncMarkerDataToTimeline(frameTimes);
            }
        }
        
        // Make sure the scene is initialized properly and create marker meshes
        this.createMarkerMeshes();

        // Start animation loop if this is the first data loaded
        if (!this.playing && (!this.animations || this.animations.length === 0)) {
            console.log('Starting animation loop for markers');
            this.animate();
            this.frame = 0;
            this.animateOneFrame();
            this.togglePlay(true);
        }
    },
    
    // New method to sync marker data to the existing timeline
    syncMarkerDataToTimeline(markerTimes) {
        console.log('Synchronizing marker data with existing timeline');
        console.log(`Marker frames: ${markerTimes.length}, Existing frames: ${this.frames.length}`);
        
        // Store a copy of the original positions for each marker
        const originalMarkers = JSON.parse(JSON.stringify(this.markers));
        
        // For each marker, resample its positions to match the current timeline
        Object.keys(this.markers).forEach(markerName => {
            const marker = this.markers[markerName];
            const original = originalMarkers[markerName];
            
            // Create new position array matching current timeline length
            const newPositions = [];
            
            // For each frame in the current timeline
            this.frames.forEach(time => {
                // Find the closest frame in the marker timeline
                const index = this.findClosestTimeIndex(markerTimes, time);
                
                // If exact match or only one frame available, use that frame's position
                if (index >= markerTimes.length || markerTimes[index] === time || markerTimes.length === 1) {
                    if (index < original.positions.length) {
                        newPositions.push({...original.positions[index]});
                    } else {
                        // Handle case where index is out of bounds
                        newPositions.push({ x: null, y: null, z: null });
                    }
                } else {
                    // Otherwise, interpolate between the two closest frames
                    const beforeIndex = index > 0 ? index - 1 : 0;
                    const afterIndex = index;
                    
                    if (beforeIndex < original.positions.length && 
                        afterIndex < original.positions.length) {
                        
                        const beforeTime = markerTimes[beforeIndex];
                        const afterTime = markerTimes[afterIndex];
                        const beforePos = original.positions[beforeIndex];
                        const afterPos = original.positions[afterIndex];
                        
                        // Only interpolate if both positions have valid data
                        if (beforePos.x !== null && beforePos.y !== null && beforePos.z !== null &&
                            afterPos.x !== null && afterPos.y !== null && afterPos.z !== null) {
                            
                            // Calculate interpolation factor (0-1)
                            const timeDiff = afterTime - beforeTime;
                            const factor = timeDiff === 0 ? 0 : (time - beforeTime) / timeDiff;
                            
                            // Linear interpolation between positions
                            newPositions.push({
                                x: beforePos.x + factor * (afterPos.x - beforePos.x),
                                y: beforePos.y + factor * (afterPos.y - beforePos.y),
                                z: beforePos.z + factor * (afterPos.z - beforePos.z)
                            });
                        } else {
                            // If either position is invalid, use the valid one, or null
                            newPositions.push({
                                x: beforePos.x !== null ? beforePos.x : (afterPos.x !== null ? afterPos.x : null),
                                y: beforePos.y !== null ? beforePos.y : (afterPos.y !== null ? afterPos.y : null),
                                z: beforePos.z !== null ? beforePos.z : (afterPos.z !== null ? afterPos.z : null)
                            });
                        }
                    } else {
                        // Handle out of bounds
                        newPositions.push({ x: null, y: null, z: null });
                    }
                }
            });
            
            // Update marker's positions array
            this.markers[markerName].positions = newPositions;
        });
        
        console.log('Marker data synchronized with timeline');
    },
    createMarkerMeshes() {
        // Remove any existing marker meshes
        this.clearMarkers();

        // Ensure we have a scene
        if (!this.scene) {
            console.log('Scene not initialized. Initializing scene for markers...');
            this.initScene();
        }

        // Double check scene initialization
        if (!this.scene) {
            console.error('Failed to initialize scene for markers');
            return;
        }

        console.log(`[createMarkerMeshes] Creating meshes for ${Object.keys(this.markers).length} markers. Current frame: ${this.frame}. Show markers: ${this.showMarkers}`);

        // Create geometry for marker spheres - shared by all markers
        const geometry = new THREE.SphereGeometry(this.markerSize, 16, 16);
        // Change material to MeshLambertMaterial for a matte effect
        const material = new THREE.MeshLambertMaterial({ 
            color: new THREE.Color(this.markerColor),
        });
        
        console.log(`Creating ${Object.keys(this.markers).length} marker meshes`);
        
        // Create mesh for each marker
        Object.entries(this.markers).forEach(([markerName, markerData]) => {
            const mesh = new THREE.Mesh(geometry, material.clone());
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            
            // Store marker name on the mesh for event handling
            mesh.userData.markerName = markerName;
            
            // Log the marker name being created
            console.log(`Creating mesh for marker: ${markerName}`);
            
            // Add double-click event handling
            mesh.userData.onDoubleClick = () => {
                this.showMarkerLabel(markerName, mesh);
            };
            
            // If we have position data for the current frame
            if (this.frame < markerData.positions.length) {
                const pos = markerData.positions[this.frame];
                
                // Only show marker if position is valid
                if (pos && pos.x !== null && pos.y !== null && pos.z !== null) {
                    mesh.position.set(
                        pos.x * this.markerScale, 
                        pos.y * this.markerScale, 
                        pos.z * this.markerScale
                    );
                    // Set visibility based on valid data (showMarkers is true by default)
                    mesh.visible = true;
                    console.log(`Marker ${markerName} positioned at:`, pos);
                } else {
                    mesh.visible = false;
                    console.log(`Marker ${markerName} has invalid position data for frame ${this.frame}`);
                }
            } else {
                mesh.visible = false;
                console.log(`Marker ${markerName} has no position data for frame ${this.frame}`);
            }
            
            // Add mesh to scene
            this.scene.add(mesh);
            
            // Store reference to mesh with the correct marker name
            this.markerMeshes[markerName] = mesh;
        });

        // Add double-click event listener to the renderer's DOM element
        if (this.renderer && this.renderer.domElement) {
            this.renderer.domElement.addEventListener('dblclick', this.handleMarkerDoubleClick);
        }

        // Force an update of marker positions and visibility
        this.updateMarkerPositions(this.frame);
        
        // Render the scene to show the markers
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },

    handleMarkerDoubleClick(event) {
        event.preventDefault();
        
        // Get mouse position
        const mouse = new THREE.Vector2();
        const rect = this.renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        // Set up raycaster
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(mouse, this.camera);

        // Find intersected objects that are marker meshes
        const intersects = raycaster.intersectObjects(Object.values(this.markerMeshes), true);
        
        if (intersects.length > 0) {
            const mesh = intersects[0].object;
            const markerName = mesh.userData.markerName;
            console.log('Double-clicked marker:', markerName); // Debug log
            if (markerName && this.markers[markerName]) {
                this.showMarkerLabel(markerName, mesh);
            }
        }
    },

    showMarkerLabel(markerName, mesh) {
        // Clear any existing label timeout
        if (this.markerLabelTimeout) {
            clearTimeout(this.markerLabelTimeout);
        }

        // Remove existing label if it's for a different marker
        if (this.activeMarkerLabel && this.activeMarkerLabel.userData.markerName !== markerName) {
            this.scene.remove(this.activeMarkerLabel);
        }

        // Create or update label
        if (!this.markerLabels[markerName]) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 64;

            // Set text style
            context.font = 'bold 32px Arial';
            context.textAlign = 'center';
            context.fillStyle = '#ffffff';
            context.strokeStyle = '#000000';
            context.lineWidth = 4;

            // Draw text with outline
            context.strokeText(markerName, canvas.width/2, canvas.height/2);
            context.fillText(markerName, canvas.width/2, canvas.height/2);

            // Create sprite
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({
                map: texture,
                transparent: true,
                opacity: 0.8
            });

            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.scale.set(1, 0.25, 1);
            sprite.userData.markerName = markerName;

            this.markerLabels[markerName] = sprite;
        }

        const label = this.markerLabels[markerName];
        
        // Position label above marker
        label.position.copy(mesh.position);
        label.position.y += 0.1; // Offset above marker

        // Add to scene if not already present
        if (!this.scene.children.includes(label)) {
            this.scene.add(label);
        }

        this.activeMarkerLabel = label;

        // Auto-hide label after 3 seconds
        this.markerLabelTimeout = setTimeout(() => {
            if (this.activeMarkerLabel === label) {
                this.scene.remove(label);
                this.activeMarkerLabel = null;
            }
        }, 3000);

        // Render scene
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    toggleMarkerVisibility() {
        // Toggle the global state
        this.showMarkers = !this.showMarkers;
        console.log(`[toggleMarkerVisibility] Set showMarkers to: ${this.showMarkers}`);

        // Update the visibility of all marker meshes (will be reapplied based on individual state in updateMarkerPositions)
        this.updateMarkerPositions(this.frame); // Re-run position/visibility update for current frame

        // Render the scene with updated visibility
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    updateMarkerColor() {
        // Update color for all marker meshes
        Object.values(this.markerMeshes).forEach(mesh => {
            if (mesh && mesh.material) {
                mesh.material.color = new THREE.Color(this.markerColor);
                mesh.material.needsUpdate = true;
            }
        });
        
        // Render the scene with updated colors
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    updateMarkerSize() {
        // Create a new sphere geometry with the updated size
        const newGeometry = new THREE.SphereGeometry(this.markerSize, 16, 16);
        
        // Update geometry for all marker meshes
        Object.values(this.markerMeshes).forEach(mesh => {
            if (mesh) {
                // Store the old position and material
                const position = mesh.position.clone();
                const material = mesh.material;
                
                // Dispose the old geometry
                if (mesh.geometry) {
                    mesh.geometry.dispose();
                }
                
                // Update with new geometry
                mesh.geometry = newGeometry;
                mesh.position.copy(position);
            }
        });
        
        // Render the scene with updated marker sizes
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },
    downloadSampleTrcFile() {
        // Create a sample TRC file with some basic markers
        console.log('Generating sample TRC file');
        
        // Generate TRC content
        let trcContent = '';
        
        // Add header information
        trcContent += 'PathFileType\t4\t(X/Y/Z)\tmarkers.trc\n';
        trcContent += 'DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n';
        trcContent += '60\t60\t100\t10\tmm\t60\t1\t100\n';
        trcContent += 'Frame#\tTime\tRHand1\t\t\tRHand2\t\t\tLHand1\t\t\tLHand2\t\t\tHead\t\t\tShoulderR\t\t\tShoulderL\t\t\tHipR\t\t\tHipL\t\t\tFootR\t\t\t\n';
        trcContent += '\t\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\tX\tY\tZ\n';
        
        // Generate sample data for 100 frames (simple oscillating pattern)
        for (let frame = 1; frame <= 100; frame++) {
            const time = (frame - 1) / 60; // 60 Hz
            
            // Start a new row with frame number and time
            let row = `${frame}\t${time.toFixed(6)}`;
            
            // Add marker positions
            // Right hand markers oscillate around (0.3, 1.5, 0)
            const handROffset1 = 0.1 * Math.sin(frame / 10);
            row += `\t${(0.3 + handROffset1).toFixed(6)}\t${(1.5 + 0.05 * Math.sin(frame / 5)).toFixed(6)}\t${(0.0 + 0.05 * Math.cos(frame / 7)).toFixed(6)}`;
            row += `\t${(0.35 + handROffset1).toFixed(6)}\t${(1.53 + 0.05 * Math.sin(frame / 5)).toFixed(6)}\t${(0.03 + 0.05 * Math.cos(frame / 7)).toFixed(6)}`;
            
            // Left hand markers oscillate around (-0.3, 1.5, 0)
            const handLOffset1 = 0.1 * Math.sin(frame / 10 + Math.PI); // Out of phase with right hand
            row += `\t${(-0.3 + handLOffset1).toFixed(6)}\t${(1.5 + 0.05 * Math.sin(frame / 5 + Math.PI)).toFixed(6)}\t${(0.0 + 0.05 * Math.cos(frame / 7 + Math.PI)).toFixed(6)}`;
            row += `\t${(-0.35 + handLOffset1).toFixed(6)}\t${(1.53 + 0.05 * Math.sin(frame / 5 + Math.PI)).toFixed(6)}\t${(0.03 + 0.05 * Math.cos(frame / 7 + Math.PI)).toFixed(6)}`;
            
            // Head marker oscillates around (0, 1.8, 0) with small movements
            row += `\t${(0.0 + 0.02 * Math.sin(frame / 12)).toFixed(6)}\t${(1.8 + 0.01 * Math.sin(frame / 8)).toFixed(6)}\t${(0.0 + 0.01 * Math.cos(frame / 9)).toFixed(6)}`;
            
            // Shoulder markers
            row += `\t${(0.2 + 0.01 * Math.sin(frame / 15)).toFixed(6)}\t${(1.6 + 0.02 * Math.sin(frame / 10)).toFixed(6)}\t${(0.0 + 0.02 * Math.cos(frame / 11)).toFixed(6)}`;
            row += `\t${(-0.2 + 0.01 * Math.sin(frame / 15 + Math.PI)).toFixed(6)}\t${(1.6 + 0.02 * Math.sin(frame / 10 + Math.PI)).toFixed(6)}\t${(0.0 + 0.02 * Math.cos(frame / 11 + Math.PI)).toFixed(6)}`;
            
            // Hip markers
            row += `\t${(0.15 + 0.01 * Math.sin(frame / 20)).toFixed(6)}\t${(1.0 + 0.01 * Math.sin(frame / 18)).toFixed(6)}\t${(0.0 + 0.01 * Math.cos(frame / 19)).toFixed(6)}`;
            row += `\t${(-0.15 + 0.01 * Math.sin(frame / 20 + Math.PI)).toFixed(6)}\t${(1.0 + 0.01 * Math.sin(frame / 18 + Math.PI)).toFixed(6)}\t${(0.0 + 0.01 * Math.cos(frame / 19 + Math.PI)).toFixed(6)}`;
            
            // Right foot marker (more movement to simulate walking)
            const footPhase = frame / 5;
            const footX = 0.15 + 0.1 * Math.sin(footPhase);
            const footY = 0.1 + 0.05 * Math.abs(Math.sin(footPhase)); // Y is height off ground
            const footZ = -0.3 - 0.2 * Math.cos(footPhase); // Z is forward/backward
            row += `\t${footX.toFixed(6)}\t${footY.toFixed(6)}\t${footZ.toFixed(6)}`;
            
            // Add the row to the TRC content
            trcContent += row + '\n';
        }
        
        // Create a blob and download the file
        const blob = new Blob([trcContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        document.body.appendChild(a);
        a.style = 'display: none';
        a.href = url;
        a.download = 'sample_markers.trc';
        a.click();
        window.URL.revokeObjectURL(url);
    },
    updateMarkerScale() {
        console.log(`Updating marker scale factor to: ${this.markerScale}`);
        
        // Get current frame
        const frame = this.frame;
        
        // Update each marker position with the new scale factor
        Object.keys(this.markers).forEach(markerName => {
            const marker = this.markers[markerName];
            const mesh = this.markerMeshes[markerName];
            
            if (mesh && frame < marker.positions.length) {
                const pos = marker.positions[frame];
                
                // Only update position if we have valid data for this frame
                if (pos && pos.x !== null && pos.y !== null && pos.z !== null) {
                    // Apply scale factor
                    mesh.position.set(
                        pos.x * this.markerScale,
                        pos.y * this.markerScale,
                        pos.z * this.markerScale
                    );
                }
            }
        });
        
        // Render the scene with updated positions
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
      },
    syncMarkersWithAnimations() {
        // Check if we have both marker data and animations
        if (!this.markerTimeData || Object.keys(this.markers).length === 0) {
            alert('No marker data to synchronize');
            return;
        }
        
        if (this.animations.length === 0) {
            alert('No animations to synchronize with');
            return;
        }
        
        console.log('Syncing markers with animation timeline');
        
        // Use the existing sync mechanism
        this.syncMarkerDataToTimeline(this.markerTimeData.times);
        
        // Update the view to reflect changes
        this.animateOneFrame();
        
        // Show a success message
        this.$nextTick(() => {
            // Use a toast or some other non-blocking notification
            console.log('Markers synchronized with animation timeline');
        });
    },
    // Video handling methods
    handleVideoUpload(event) {
      const file = event.target.files[0];
      if (file && (file.type === 'video/mp4' || file.type === 'video/webm')) {
        // Clean up previous video URL if it exists
        if (this.videoUrl) {
          URL.revokeObjectURL(this.videoUrl);
        }
        
        this.videoFile = file;
        this.videoUrl = URL.createObjectURL(file);
        this.videoMinimized = false; // Ensure video starts in full size
        
        console.log('Video file loaded:', file.name);
        
        // Reset the input to allow reselecting the same file
        event.target.value = '';
        
        // Force a redraw
        this.$nextTick(() => {
          console.log('Video container should be visible now');
        });
      }
    },
    
    handleVideoMetadata() {
      if (this.$refs.videoPreview) {
        this.videoDuration = this.$refs.videoPreview.duration;
        console.log('Video duration:', this.videoDuration);
        
        // Set initial video position based on current frame
        if (this.frames.length > 0) {
          const totalFrames = this.frames.length - 1;
          const videoTimePosition = (this.frame / totalFrames) * this.videoDuration;
          this.$refs.videoPreview.currentTime = videoTimePosition;
        }
      }
    },
    
    toggleVideoPreview() {
      this.videoMinimized = !this.videoMinimized;
      
      // Adjust width based on minimized state
      if (this.videoMinimized) {
        this.videoSize.width = 200;
                    } else {
        this.videoSize.width = 300;
      }
    },
    
    closeVideo() {
      if (this.videoUrl) {
        URL.revokeObjectURL(this.videoUrl);
      }
      this.videoFile = null;
      this.videoUrl = null;
      this.videoDuration = 0;
      console.log('Video closed');
    
      // Reset position and size for next time
      this.videoPosition = { x: 20, y: 20 };
      this.videoSize = { width: 300, height: 'auto' };
    },
    
    handleVideoError(event) {
      console.error('Video error:', event);
      const video = event.target;
      console.log('Video element state:', {
        error: video.error,
        networkState: video.networkState,
        readyState: video.readyState,
        src: video.src,
        currentSrc: video.currentSrc
      });
    },
    
    startDrag(event) {
      // Handle both mouse and touch events
      const clientX = event.clientX || (event.touches && event.touches[0].clientX);
      const clientY = event.clientY || (event.touches && event.touches[0].clientY);
      
      if (!clientX || !clientY) return;
      
      this.isDragging = true;
      this.dragOffset = {
        x: clientX - this.videoPosition.x,
        y: clientY - this.videoPosition.y
      };
      
      // Add move and end event listeners
      if (event.type === 'mousedown') {
        window.addEventListener('mousemove', this.doDrag);
        window.addEventListener('mouseup', this.stopDrag);
      } else {
        window.addEventListener('touchmove', this.doDrag);
        window.addEventListener('touchend', this.stopDrag);
      }
      
      // Prevent default to avoid text selection
      event.preventDefault();
    },
    
    doDrag(event) {
      if (!this.isDragging) return;
      
      const clientX = event.clientX || (event.touches && event.touches[0].clientX);
      const clientY = event.clientY || (event.touches && event.touches[0].clientY);
      
      if (!clientX || !clientY) return;
      
      // Calculate new position
      this.videoPosition = {
        x: clientX - this.dragOffset.x,
        y: clientY - this.dragOffset.y
      };
      
      // Ensure the video stays within the viewport
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight
      };
      
      // Prevent dragging too far off-screen
      if (this.videoPosition.x < -this.videoSize.width + 100) {
        this.videoPosition.x = -this.videoSize.width + 100;
      }
      if (this.videoPosition.x > viewport.width - 100) {
        this.videoPosition.x = viewport.width - 100;
      }
      if (this.videoPosition.y < 0) {
        this.videoPosition.y = 0;
      }
      if (this.videoPosition.y > viewport.height - 50) {
        this.videoPosition.y = viewport.height - 50;
      }
      
      event.preventDefault();
    },
    
    stopDrag() {
      this.isDragging = false;
      
      // Remove event listeners
      window.removeEventListener('mousemove', this.doDrag);
      window.removeEventListener('mouseup', this.stopDrag);
      window.removeEventListener('touchmove', this.doDrag);
      window.removeEventListener('touchend', this.stopDrag);
    },
    
    startResize(event) {
      // Handle both mouse and touch events
      const clientX = event.clientX || (event.touches && event.touches[0].clientX);
      const clientY = event.clientY || (event.touches && event.touches[0].clientY);
      
      if (!clientX || !clientY) return;
      
      this.isResizing = true;
      this.resizeStartPosition = { x: clientX, y: clientY };
      this.resizeStartSize = { ...this.videoSize };
      
      // Add move and end event listeners
      if (event.type === 'mousedown') {
        window.addEventListener('mousemove', this.doResize);
        window.addEventListener('mouseup', this.stopResize);
      } else {
        window.addEventListener('touchmove', this.doResize);
        window.addEventListener('touchend', this.stopResize);
      }
      
      // Prevent default to avoid text selection
      event.preventDefault();
    },
    
    doResize(event) {
      if (!this.isResizing) return;
      
      const clientX = event.clientX || (event.touches && event.touches[0].clientX);
      const clientY = event.clientY || (event.touches && event.touches[0].clientY);
      
      if (!clientX || !clientY) return;
      
      // Calculate width change
      const widthChange = clientX - this.resizeStartPosition.x;
      const heightChange = clientY - this.resizeStartPosition.y;
      
      // Update width with minimum size constraints
      const newWidth = Math.max(200, this.resizeStartSize.width + widthChange);
      this.videoSize.width = newWidth;
      
      event.preventDefault();
    },
    
    stopResize() {
      this.isResizing = false;
      
      // Remove event listeners
      window.removeEventListener('mousemove', this.doResize);
      window.removeEventListener('mouseup', this.stopResize);
      window.removeEventListener('touchmove', this.doResize);
      window.removeEventListener('touchend', this.stopResize);
    },
    async openEyedropper(index) {
      if (!window.EyeDropper) {
        alert("Your browser doesn't support the Eyedropper API.");
        return;
      }

      const eyedropper = new window.EyeDropper(); // Use window.EyeDropper
      try {
        const result = await eyedropper.open();
        // result.sRGBHex contains the selected color
        console.log(`Eyedropper selected color: ${result.sRGBHex} for subject ${index}`);
        this.updateSubjectColor(index, result.sRGBHex);
      } catch (e) {
        console.log('Eyedropper cancelled or failed:', e);
        // Handle cancellation or error (e.g., user presses Esc)
      }
    },
    async openBackgroundEyedropper() {
      if (!window.EyeDropper) {
        alert("Your browser doesn't support the Eyedropper API.");
        return;
      }

      const eyedropper = new window.EyeDropper();
      try {
        const result = await eyedropper.open();
        // result.sRGBHex contains the selected color
        console.log(`Eyedropper selected color for background: ${result.sRGBHex}`);
        this.updateBackgroundColor(result.sRGBHex);
      } catch (e) {
        console.log('Eyedropper cancelled or failed:', e);
      }
    },
    async openGroundEyedropper() {
      if (!this.showGround) return;
      
      if (!window.EyeDropper) {
        alert("Your browser doesn't support the Eyedropper API.");
        return;
      }

      const eyedropper = new window.EyeDropper();
      try {
        const result = await eyedropper.open();
        // result.sRGBHex contains the selected color
        console.log(`Eyedropper selected color for ground: ${result.sRGBHex}`);
        this.updateGroundColor(result.sRGBHex);
      } catch (e) {
        console.log('Eyedropper cancelled or failed:', e);
      }
    },
    updateGlobalLightIntensity(value) {
      this.globalLightIntensity = value; // Update the component's data property
      if (this.lights.hemisphere) {
        this.lights.hemisphere.intensity = 0.1 * value; // Use base intensity 0.1
      }
      this.lights.directionals.forEach(light => {
        light.intensity = 0.5 * value; // Use base intensity 0.5
      });
      // Re-render the scene with updated light intensity
      this.saveSettings(); // Save light intensity setting
      if (this.renderer) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    openMeshDialog(index) {
      // Use $set to ensure reactivity when adding/modifying the property
      this.$set(this.meshDialogs, index, true);
    },
    // Add method to handle incoming messages from parent window
    handleIframeMessage(event) {
      // Optional: Check origin for security
      // const trustedOrigin = 'YOUR_PARENT_DOMAIN_HERE'; // e.g., 'http://localhost:8080'
      // if (event.origin !== trustedOrigin) {
      //   console.warn('Message received from untrusted origin:', event.origin);
      //   return;
      // }

      // Check if data is a command object (play/pause)
      if (typeof event.data === 'object' && event.data !== null && event.data.type) {
        if (event.data.type === 'play') {
          if (!this.playing) { // Only play if not already playing
            this.togglePlay(true);
          }
        } else if (event.data.type === 'pause') {
          if (this.playing) { // Only pause if not already paused
            this.togglePlay(false);
          }
        } else if (event.data.type === 'loadJson') {
          // Handle JSON data loading
          if (event.data.jsonData) {
            this.loadJsonData(event.data.jsonData);
          }
        }
      }
      // Check if data is a number (video time)
      else if (typeof event.data === 'number' && isFinite(event.data)) {
        const receivedTime = event.data;
        
        // Check if animation is loaded
        if (!this.trial || this.frames.length === 0) {
          return; // Cannot sync if no animation is loaded
        }

        // Calculate target frame (clamp within bounds)
        let targetFrame = Math.round(receivedTime * this.frameRate);
        targetFrame = Math.max(0, Math.min(targetFrame, this.frames.length - 1));

        // Only update if the frame is different from the current one
        if (targetFrame !== this.frame) {
          // Use onNavigate to update frame, time, and render
          this.onNavigate(targetFrame);
        }
      }
    },
    toggleLooping() {
      this.isLooping = !this.isLooping;
      // Watcher handles saving
    },
    handleKeyDown(event) {
      // Ignore keyboard events if we're in an input field
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
      }

      // Ignore if we don't have any frames loaded
      if (!this.frames || this.frames.length === 0) {
            return;
        }
        
      switch (event.code) {
        case 'Space': {
          // Toggle play/pause
          event.preventDefault(); // Prevent page scroll
          this.togglePlay(!this.playing);
          break;
        }

        case 'ArrowLeft': {
          // Previous frame
          event.preventDefault();
          this.playing = false; // Stop playback
          const prevFrame = Math.max(0, this.frame - 1);
          this.onNavigate(prevFrame);
          break;
        }

        case 'ArrowRight': {
          // Next frame
          event.preventDefault();
          this.playing = false; // Stop playback
          const nextFrame = Math.min(this.frames.length - 1, this.frame + 1);
          this.onNavigate(nextFrame);
          break;
        }

        case 'ArrowUp': {
          // Increase playback speed
          event.preventDefault();
          this.playSpeed = Math.min(4, this.playSpeed + 0.25);
          break;
        }

        case 'ArrowDown': {
          // Decrease playback speed
          event.preventDefault();
          this.playSpeed = Math.max(0.25, this.playSpeed - 0.25);
          break;
        }
      }
    },
    // Method to load settings from localStorage
    loadSettings() {
      const savedSettings = localStorage.getItem('opencapVisualizerSettings');
      console.log('Loading settings from localStorage:', savedSettings);
      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings);
          console.log('Loading settings from localStorage:', settings);
          
          // Apply settings to data properties
          if (settings.backgroundColor) this.backgroundColor = settings.backgroundColor;
          if (settings.groundColor) this.groundColor = settings.groundColor;
          if (settings.showGround !== undefined) this.showGround = settings.showGround;
          if (settings.useGroundTexture !== undefined) this.useGroundTexture = settings.useGroundTexture;
          if (settings.useCheckerboard !== undefined) this.useCheckerboard = settings.useCheckerboard;
          if (settings.globalLightIntensity !== undefined) this.globalLightIntensity = settings.globalLightIntensity;
          if (settings.playSpeed !== undefined) this.playSpeed = settings.playSpeed;
          if (settings.recordingFormat) this.recordingFormat = settings.recordingFormat;
          if (settings.videoBitrate) this.videoBitrate = settings.videoBitrate;
          if (settings.loopCount !== undefined) this.loopCount = settings.loopCount;
          if (settings.isLooping !== undefined) this.isLooping = settings.isLooping;
          if (settings.captureMode) this.captureMode = settings.captureMode;
          if (settings.markerColor) this.markerColor = settings.markerColor;
          if (settings.markerSize) this.markerSize = settings.markerSize;
          if (settings.markerScale) this.markerScale = settings.markerScale;
          if (settings.showMarkers !== undefined) this.showMarkers = settings.showMarkers;
          if (settings.showSidebar !== undefined) this.showSidebar = settings.showSidebar;
          if (settings.videoPosition) this.videoPosition = settings.videoPosition;
          if (settings.videoSize) this.videoSize = settings.videoSize;
          if (settings.videoMinimized !== undefined) this.videoMinimized = settings.videoMinimized;
          if (settings.timelapseMode !== undefined) this.timelapseMode = settings.timelapseMode;
          if (settings.timelapseInterval) this.timelapseInterval = settings.timelapseInterval;
          if (settings.timelapseOpacity !== undefined) this.timelapseOpacity = settings.timelapseOpacity;
          if (settings.recentSubjectColors) this.recentSubjectColors = settings.recentSubjectColors;

        } catch (e) {
          console.error('Error parsing settings from localStorage:', e);
          localStorage.removeItem('opencapVisualizerSettings'); // Clear corrupted data
        }
                    } else {
        console.log('No saved settings found in localStorage.');
      }
    },

    // Method to save settings to localStorage
    saveSettings() {
      console.log('Saving settings to localStorage...');
      const settings = {
        backgroundColor: this.backgroundColor,
        groundColor: this.groundColor,
        showGround: this.showGround,
        useGroundTexture: this.useGroundTexture,
        useCheckerboard: this.useCheckerboard,
        globalLightIntensity: this.globalLightIntensity,
        playSpeed: this.playSpeed,
        recordingFormat: this.recordingFormat,
        videoBitrate: this.videoBitrate,
        loopCount: this.loopCount,
        isLooping: this.isLooping,
        captureMode: this.captureMode,
        markerColor: this.markerColor,
        markerSize: this.markerSize,
        markerScale: this.markerScale,
        showMarkers: this.showMarkers,
        showSidebar: this.showSidebar,
        videoPosition: this.videoPosition,
        videoSize: this.videoSize,
        videoMinimized: this.videoMinimized,
        timelapseMode: this.timelapseMode,
        timelapseInterval: this.timelapseInterval,
        timelapseOpacity: this.timelapseOpacity,
        recentSubjectColors: this.recentSubjectColors, // Save recent colors
      };
      try {
        localStorage.setItem('opencapVisualizerSettings', JSON.stringify(settings));
        console.log('Settings saved successfully:', settings);
      } catch (e) {
        console.error('Error saving settings to localStorage:', e);
      }
    },

    // Apply scene-related settings after scene initialization
    applyLoadedSceneSettings() {
      console.log('[applyLoadedSceneSettings] Applying settings to the scene...');
      console.log('[applyLoadedSceneSettings] Scene exists:', !!this.scene, 'Renderer exists:', !!this.renderer);
      if (!this.scene || !this.renderer) return;

      console.log(`[applyLoadedSceneSettings] Applying Background: ${this.backgroundColor}, Ground: ${this.groundColor}, ShowGround: ${this.showGround}, UseTexture: ${this.useGroundTexture}, UseChecker: ${this.useCheckerboard}, Light: ${this.globalLightIntensity}`);
      // Background color
      this.updateBackgroundColor(this.backgroundColor);

      // Ground settings
      if (this.groundMesh) {
          this.groundMesh.visible = this.showGround;
          this.updateGroundColor(this.groundColor); // Update color first
          
          // Apply texture settings
          const oldMaterial = this.groundMesh.material;
          if (this.useGroundTexture) {
              const textureToUse = this.useCheckerboard ? this.groundTexture : this.gridTexture;
              if (!textureToUse && !this.useCheckerboard) {
                // Ensure grid texture is loaded if needed
                this.loadGridTexture(); 
              }
              this.groundMesh.material = new THREE.MeshPhongMaterial({
                  map: this.useCheckerboard ? this.groundTexture : this.gridTexture,
                  side: THREE.DoubleSide,
                  color: new THREE.Color(this.groundColor)
                            });
                        } else {
              this.groundMesh.material = new THREE.MeshPhongMaterial({
                  color: new THREE.Color(this.groundColor),
                  side: THREE.DoubleSide
              });
          }
          if (oldMaterial && oldMaterial !== this.groundMesh.material) {
            oldMaterial.dispose();
          }
                    } else {
          console.warn('[applyLoadedSceneSettings] Ground mesh not ready when applying settings.');
          console.warn('[applyLoadedSceneSettings] Ground mesh not ready.');
      }

      // Light intensity
      this.updateGlobalLightIntensity(this.globalLightIntensity);

      // Marker settings that affect meshes
      this.updateMarkerColor(); // Update material color
      this.updateMarkerSize(); // Update geometry size
      this.updateMarkerScale(); // Update positions based on scale
      this.toggleMarkerVisibility(); // Set visibility

      // Re-render to apply all changes
      this.renderer.render(this.scene, this.camera);
    },
    loadGridTexture() {
        if (this.gridTexture) return; // Already loaded

        // Create grid texture if it doesn't exist
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 512;
        canvas.height = 512;
        
        // Fill with background color (slightly off-white for better visibility)
        context.fillStyle = '#f0f0f0'; 
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid lines
        context.strokeStyle = '#888888'; // Darker grey lines
        context.lineWidth = 1;
        
        const gridSize = 32; // Size of grid cells
        
        // Draw vertical lines
        for (let x = 0; x <= canvas.width; x += gridSize) {
            context.beginPath();
            context.moveTo(x + 0.5, 0); // Offset by 0.5 for sharper lines
            context.lineTo(x + 0.5, canvas.height);
            context.stroke();
        }
        
        // Draw horizontal lines
        for (let y = 0; y <= canvas.height; y += gridSize) {
            context.beginPath();
            context.moveTo(0, y + 0.5); // Offset by 0.5 for sharper lines
            context.lineTo(canvas.width, y + 0.5);
            context.stroke();
        }
        
        // Create texture from canvas
        this.gridTexture = new THREE.CanvasTexture(canvas);
        this.gridTexture.wrapS = THREE.RepeatWrapping;
        this.gridTexture.wrapT = THREE.RepeatWrapping;
        this.gridTexture.magFilter = THREE.LinearFilter; // Use linear filter for smoother look
        this.gridTexture.minFilter = THREE.LinearMipmapLinearFilter;
        this.gridTexture.anisotropy = this.renderer ? this.renderer.capabilities.getMaxAnisotropy() : 1;
        this.gridTexture.needsUpdate = true; 

        // Adjust repeat based on plane size
        const repeats = 20; // Match planeSize
        this.gridTexture.repeat.set(repeats, repeats); 
        console.log('Grid texture created and assigned.');
    },
    // Add this new method
    loadJsonData(jsonData) {
        // Create a "virtual" File object with the JSON data
        const jsonBlob = new Blob([JSON.stringify(jsonData)], { type: 'application/json' });
        const jsonFile = new File([jsonBlob], 'data.json', { type: 'application/json' });
        
        // Use our existing file handler with a fake event
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(jsonFile);
        
        const fakeEvent = {
            target: {
                files: dataTransfer.files,
                value: ''
            }
        };
        
        // Process the JSON using our existing handler
        this.handleFileUpload(fakeEvent);
    },
    // New method to delete a marker file entry
    deleteMarkerFile(index) {
        // Remove the specific file entry
        this.loadedMarkerFiles.splice(index, 1);
        
        // If no marker files are left, clear all marker data and meshes
        if (this.loadedMarkerFiles.length === 0) {
            console.log('Last marker file removed, clearing all marker data.');
            this.clearMarkers(); // Remove meshes
            this.markers = {}; // Clear parsed data
            this.markerTimeData = null; // Clear time data
            this.showMarkers = false; // Ensure markers are hidden if panel disappears
        } else {
            console.log(`Removed marker file at index ${index}. ${this.loadedMarkerFiles.length} remaining.`);
            // Optional: If needed, re-sync remaining markers or update UI?
            // For now, just removing the reference. Assumes marker data (`this.markers`) might be shared if multiple TRCs were loaded?
            // If each TRC load replaces `this.markers`, then removing the last file is correct.
            // If TRC loads *add* to `this.markers`, this logic needs refinement.
            // Based on current `parseTrcFile`, it seems to replace `this.markers`, so this is likely okay.
        }
        
        // Re-render the scene
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    toggleSingleMarkerVisibility(markerName) {
        if (this.markers[markerName]) {
            // Toggle the visibility state for the specific marker
            this.markers[markerName].visible = !this.markers[markerName].visible;
            console.log(`[toggleSingleMarkerVisibility] Set ${markerName} visibility to: ${this.markers[markerName].visible}`);

            // Find the corresponding mesh and update its visibility immediately
            const mesh = this.markerMeshes[markerName];
            if (mesh) {
                // We also need to check data validity for the *current* frame here
                let dataIsValid = false;
                const markerData = this.markers[markerName];
                if (markerData && this.frame < markerData.positions.length) {
                    const pos = markerData.positions[this.frame];
                    dataIsValid = pos && pos.x !== null && pos.y !== null && pos.z !== null;
                }
                // Mesh is visible if global toggle is on, this marker is set to visible, AND current frame data is valid
                mesh.visible = this.showMarkers && this.markers[markerName].visible && dataIsValid;
            }
            
            // Re-render the scene
            if (this.renderer) {
                this.renderer.render(this.scene, this.camera);
            }
            // Use $forceUpdate if reactivity is an issue with the dialog list
            this.$forceUpdate();
        }
    },
    updateMarkerOpacity(value) {
        // Update the opacity value
        this.markerOpacity = value;
        
        // Update all marker meshes
        Object.values(this.markerMeshes).forEach(mesh => {
            if (mesh && mesh.material) {
                mesh.material.transparent = value < 1.0;
                mesh.material.opacity = value;
                mesh.material.needsUpdate = true;
            }
        });
        
        // Render the scene with updated transparency
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    clearMarkers() {
        // Clear existing marker labels
        Object.values(this.markerLabels).forEach(label => {
            if (label && label.parent) {
                label.parent.remove(label);
                if (label.material.map) {
                    label.material.map.dispose();
                }
                label.material.dispose();
            }
        });
        this.markerLabels = {};
        this.activeMarkerLabel = null;
        if (this.markerLabelTimeout) {
            clearTimeout(this.markerLabelTimeout);
        }

        // Log marker clearing operation
        console.log('Clearing marker meshes:', Object.keys(this.markerMeshes).length);
        
        // Remove all marker meshes from scene
        Object.entries(this.markerMeshes).forEach(([name, mesh]) => {
            if (mesh) {
                // Safely remove from scene
                if (mesh.parent) {
                    mesh.parent.remove(mesh);
                }
                
                // Dispose geometry and material
                if (mesh.geometry) {
                    mesh.geometry.dispose();
                }
                if (mesh.material) {
                    if (Array.isArray(mesh.material)) {
                        mesh.material.forEach(material => material.dispose());
                    } else {
                        mesh.material.dispose();
                    }
                }
                console.log(`Removed marker mesh: ${name}`);
            }
        });
        
        // Clear marker mesh references
        this.markerMeshes = {};
        
        // Remove double-click event listener
        if (this.renderer && this.renderer.domElement) {
            this.renderer.domElement.removeEventListener('dblclick', this.handleMarkerDoubleClick);
        }
        
        // Render the scene to reflect changes
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    },
  }
}
</script>

<style lang="scss">
.viewer-container {
  height: 100vh;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  
  * {
    font-family: inherit;
  }

  .viewer {
    height: 100%;
    transition: margin-right 0.3s ease;
  
    &:not(.sidebar-hidden):not(.is-embedded) {
      margin-right: 360px; // Reduced from 400px
    }
  
    #mocap {
      width: 100%;
      height: calc(100% - 60px);
      position: relative;
      overflow: visible;
    }
  }
  
  .right {
    flex: 0 0 360px; // Reduced from 450px
    width: 360px; // Reduced from 450px
    height: 100%;
    padding: 15px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    position: fixed;
    right: 0;
    top: 0;
    background: #1E1E1E;
    transition: transform 0.3s ease;
    z-index: 100;

    &.hidden {
      transform: translateX(100%);
      // Add display: none or visibility: hidden if transform is not enough
      // Or ensure position: fixed keeps it out of flow
    }

    &::-webkit-scrollbar {
      width: 4px;
    }

    // Adjust spacing for compact view
    .mb-4 {
      margin-bottom: 8px !important;
    }

    .scene-controls {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 4px;
      padding: 10px;  // Increased from 5px
    }

    .format-selector {
      margin-top: 8px !important;  // Add top margin to Format and Bitrate selectors
    }

    .color-preview {
      width: 20px !important;
      min-width: 20px !important;
      height: 20px !important;
      border-radius: 4px !important;
      border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    .legend {
      flex: 1;
      overflow-y: auto;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 4px;
      padding: 5px;

      .legend-item {
        display: flex;
        flex-direction: column;
        padding: 3px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);

        &:last-child {
          border-bottom: none;
        }

        .color-box {
          width: 20px;
          height: 20px;
          border-radius: 4px;
          display: inline-block;
          flex-shrink: 0; // Prevent color box from shrinking
        }

        .file-name {
          font-size: 10px;
          color: rgba(255, 255, 255, 0.5);
          text-align: left; // Align text to the left
          margin-top: 2px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .v-btn {
          margin: 2px !important;
          min-width: 20px !important;
          width: 20px !important;
          height: 20px !important;
          padding: 0 !important;
        }

        // Style for the Meshes button
        .v-btn.v-btn--text {
          min-width: 80px !important;
          width: auto !important;
          height: 24px !important;
          padding: 0 8px !important;
        }
      }
    }
  }

  .sidebar-toggle {
    position: fixed !important;
    top: 50%;
    transform: translateY(-50%);
    z-index: 101;
    transition: right 0.3s ease;
    background: rgba(30, 30, 30, 0.8) !important;
    
    &:hover {
      background: rgba(50, 50, 50, 0.9) !important;
    }
  }

  .controls-container {
    height: 60px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    margin: 5px;
    padding: 8px;
    display: flex;
    align-items: center;
  }
}

.trial-name-input {
  .v-input__slot {
    margin-bottom: 0 !important;
  }
  input {
    font-weight: 500 !important;
    font-size: 14px !important;
    min-width: 0 !important;
    font-family: inherit !important;
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

.video-preview-container {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 9999;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  max-width: 30%;
  min-width: 200px; // Add minimum width
  background-color: #000;
  border: 1px solid rgba(255, 255, 255, 0.2); // Add border to make it visible
}

.video-preview-container video {
  width: 100%;
  display: block;
  background-color: #000;
  min-height: 150px; // Increase minimum height
}

.video-controls {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 10000; // Increase z-index to be above video
  display: flex;
  gap: 4px; // Add gap between buttons
  background-color: rgba(0, 0, 0, 0.7); // Make background more visible
  border-radius: 4px;
  padding: 4px;
}

.video-minimized {
  width: 200px;
}

.mesh-controls {
  .v-expansion-panels {
    max-width: 200px;
    background: transparent !important;
    
    .v-expansion-panel {
      background: transparent !important;
      
      &::before {
        box-shadow: none !important;
      }
      
      .v-expansion-panel-header {
        padding: 0 8px;
        min-height: 32px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
        
        .v-expansion-panel-header__icon {
          margin-left: 4px;
          
          .v-icon {
            font-size: 18px;
          }
        }
      }
      
      .v-expansion-panel-content {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 4px;
        margin-top: 4px;
        
        .v-expansion-panel-content__wrap {
          padding: 4px;
        }
      }
    }
  }
  
  .mesh-groups {
    .group-header {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
      margin-bottom: 4px;
      font-size: 14px;
      font-family: inherit;
    }
    
    .mesh-item {
      border-radius: 4px;
      transition: background-color 0.2s;
      font-size: 13px;
      font-family: inherit;
      
      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }
    }
  }
}

// ... existing code ...

.fps-info {
  font-size: 10px;
  margin-top: 1px;
  text-align: left; // Align text to the left
  font-family: inherit;
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

.custom-btn {
  border-radius: 8px !important;
  font-weight: 500 !important;
  letter-spacing: 0.025em !important;
  text-transform: none !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.2s ease !important;
  font-family: inherit !important;

  &:hover {
    filter: brightness(0.95);
    transform: scale(1.02);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15) !important;
  }

  &:active {
    transform: scale(0.98);
  }

  .v-icon {
    margin-right: 6px !important;
  }
}
</style>
  
  