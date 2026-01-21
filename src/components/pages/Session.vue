<template>
    <div class="viewer-container d-flex">
      <!-- Top-level video container - hide when video plane is visible (but keep in DOM with v-show so video element remains accessible) -->
      <VideoOverlay
        v-if="videoFile"
        ref="videoOverlayComponent"
        :video-file="videoFile"
        :video-url="videoUrl"
        :video-position="videoPosition"
        :video-size="videoSize"
        :video-plane-settings="videoPlaneSettings"
        :is-dragging="isDragging"
        :is-resizing="isResizing"
        :video-minimized="videoMinimized"
        :video-overlay-mode="videoOverlayMode"
        :video-overlay-opacity="videoOverlayOpacity"
        :is-looping="isLooping"
        @start-drag="startDrag"
        @start-resize="startResize"
        @toggle-video-overlay="toggleVideoOverlay"
        @toggle-video-preview="toggleVideoPreview"
        @close-video="closeVideo"
        @video-loadedmetadata="handleVideoMetadata"
        @video-timeupdate="handleVideoTimeUpdate"
      />
  
      <!-- Left Sidebar -->
      <div class="left d-flex flex-column" :class="{ 'hidden': !showLeftSidebar }" v-if="$route.query.embed !== 'true'">
        <!-- Empty left sidebar - will be populated later -->
        <div class="left-content flex-grow-1">
          <div class="pa-4">
            <h2 class="text-h6 white--text mb-4">Files</h2>
  
            <!-- Conversion Status Indicator -->
            <div v-if="converting" class="conversion-status mb-4">
              <v-card class="pa-3" color="rgba(79, 70, 229, 0.2)" outlined>
                <div class="d-flex align-center">
                  <v-progress-circular
                    indeterminate
                    color="indigo"
                    size="20"
                    width="2"
                    class="mr-3"
                  />
                  <div>
                    <div class="text-subtitle-2 white--text">Converting OpenSim Files</div>
                    <div class="text-caption grey--text">Processing .osim and .mot files...</div>
                  </div>
                </div>
              </v-card>
            </div>
  
            <!-- Shared Session Loading Status Indicator -->
            <div v-if="loadingSharedSession" class="conversion-status mb-4">
              <v-card class="pa-3" color="rgba(79, 70, 229, 0.2)" outlined>
                <div class="d-flex align-center">
                  <v-progress-circular
                    indeterminate
                    color="indigo"
                    size="20"
                    width="2"
                    class="mr-3"
                  />
                  <div>
                    <div class="text-subtitle-2 white--text">Loading Shared Visualization</div>
                    <div class="text-caption grey--text">Loading visualization data...</div>
                  </div>
                </div>
              </v-card>
            </div>
  
            <!-- Add Import Button Here -->
            <v-btn color="#4B5563" class="mb-4 white--text custom-btn" block @click="openImportDialog" :disabled="converting">
              <v-icon left>mdi-import</v-icon>
              Import
            </v-btn>

            <!-- Clear Scene Button -->
            <v-btn color="#4B5563" class="mb-4 white--text custom-btn" block @click="clearScene" :disabled="animations.length === 0 && smplSequences.length === 0 && customObjects.length === 0 && Object.keys(markersDatasets).length === 0">
              <v-icon left>mdi-delete-sweep</v-icon>
              Clear Scene
            </v-btn>

            <v-card v-if="videoFile" class="mb-4 video-info-card" dark outlined>
              <v-card-title class="py-2 px-3 d-flex align-center" style="cursor: pointer;" @click="showVideoDetails = !showVideoDetails">
                <v-icon small left class="mr-2">mdi-video</v-icon>
                <span class="subtitle-2 text-truncate">{{ videoFile.name }}</span>
                <v-spacer></v-spacer>
                <v-icon small>{{ showVideoDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </v-card-title>
              <v-expand-transition>
                <v-card-text v-show="showVideoDetails" class="py-2 px-3">
                <div class="text-caption grey--text mb-1">
                  Duration: {{ formattedVideoDuration }}
                </div>
                <div class="text-caption grey--text mb-1">
                  Video FPS: {{ videoFrameRate }}
                </div>
                <div class="text-caption grey--text mb-2">
                  Sequence FPS: {{ frameRateDisplay }}
                </div>
                <v-divider class="my-3" dark></v-divider>
                <div class="text-caption grey--text mb-2">
                  Scene Placement
                </div>
                <v-switch
                  dense
                  hide-details
                  color="cyan lighten-2"
                  class="mt-0"
                  v-model="videoPlaneSettings.visible"
                  label="Show video plane"
                ></v-switch>
                <div v-show="videoPlaneSettings.visible">
                  <v-switch
                    dense
                    hide-details
                    color="cyan lighten-2"
                    class="mt-1"
                    v-model="videoPlaneSettings.followCamera"
                    label="Follow camera"
                  ></v-switch>
                  <div class="text-caption grey--text mt-2 mb-1">
                    Plane Distance (m): {{ videoPlaneSettings.distance.toFixed(2) }}
                  </div>
                  <v-slider
                    dense
                    hide-details
                    v-model="videoPlaneSettings.distance"
                    :min="0.5"
                    :max="50"
                    :step="0.1"
                    color="cyan lighten-2"
                  ></v-slider>
                  <div class="text-caption grey--text mt-2 mb-1">
                    Plane Width (m): {{ videoPlaneSettings.width.toFixed(2) }}
                  </div>
                  <v-slider
                    dense
                    hide-details
                    v-model="videoPlaneSettings.width"
                    :min="1"
                    :max="100"
                    :step="0.1"
                    color="cyan lighten-2"
                  ></v-slider>
                  <div class="text-caption grey--text mt-2 mb-1">
                    Plane Opacity: {{ Math.round(videoPlaneSettings.opacity * 100) }}%
                  </div>
                  <v-slider
                    dense
                    hide-details
                    :value="Math.round(videoPlaneSettings.opacity * 100)"
                    @input="onVideoPlaneOpacityInput"
                    :min="10"
                    :max="100"
                    :step="5"
                    color="cyan lighten-2"
                  ></v-slider>
                </div>
                </v-card-text>
              </v-expand-transition>
            </v-card>

            <!-- Live IK Stream controls -->
            <v-card class="mb-4" dark outlined>
              <v-card-title class="py-2 px-3 d-flex align-center" style="cursor: pointer;" @click="showLiveStreamDetails = !showLiveStreamDetails">
                <v-icon small left class="mr-2">mdi-wifi</v-icon>
                <span class="subtitle-2">Live IK Stream</span>
                <v-spacer></v-spacer>
                <v-icon small>{{ showLiveStreamDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </v-card-title>
              <v-expand-transition>
                <v-card-text v-show="showLiveStreamDetails" class="py-2 px-3">
                  <v-text-field
                    v-model="liveUrl"
                    dense
                    hide-details
                    label="WebSocket URL"
                  ></v-text-field>
                  <div class="d-flex align-center mt-2">
                    <v-btn
                      small
                      color="indigo"
                      class="mr-2"
                      :disabled="liveStatus === 'connecting'"
                      @click="connectLiveStream"
                      v-if="liveStatus !== 'connected'"
                    >
                      <v-icon left small>mdi-play-circle</v-icon>
                      Connect
                    </v-btn>
                    <v-btn
                      small
                      color="red darken-1"
                      class="mr-2"
                      v-else
                      @click="disconnectLiveStream"
                    >
                      <v-icon left small>mdi-stop-circle</v-icon>
                      Disconnect
                    </v-btn>
                    <span class="text-caption grey--text">
                      Status: {{ liveStatus }}
                    </span>
                  </div>
                </v-card-text>
              </v-expand-transition>
            </v-card>

            <v-card class="mb-4" dark outlined>
              <v-card-title class="py-2 px-3 d-flex align-center" style="cursor: pointer;" @click="showSyncDetails = !showSyncDetails">
                <v-icon small left class="mr-2">mdi-timeline-clock</v-icon>
                <span class="subtitle-2">Sync</span>
                <v-spacer></v-spacer>
                <v-icon small>{{ showSyncDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </v-card-title>
              <v-expand-transition>
                <v-card-text v-show="showSyncDetails" class="py-2 px-3">
                  <v-select
                    dense
                    hide-details
                    outlined
                    v-model="syncMode"
                    :items="syncModeOptions"
                    label="Sync mode"
                  ></v-select>
                  <div v-if="syncMode === 'time'" class="mt-2">
                    <v-alert text dense color="indigo darken-2">
                      <span class="text-caption">Align all datasets so their time starts at zero.</span>
                    </v-alert>
                  </div>
                  <div v-if="syncMode === 'frame'" class="mt-3">
                    <div class="text-caption grey--text mb-1">
                      Reference Frame: {{ syncReferenceFrame }}
                    </div>
                    <v-slider
                      dense
                      hide-details
                      v-model="syncReferenceFrame"
                      :min="0"
                      :max="maxFrameIndex"
                      :step="1"
                      :disabled="maxFrameIndex === 0"
                      color="indigo lighten-2"
                    ></v-slider>
                    <v-alert text dense color="indigo darken-2" class="mt-2">
                      <span class="text-caption">Shift all datasets so this frame becomes time zero.</span>
                    </v-alert>
                  </div>
                </v-card-text>
              </v-expand-transition>
            </v-card>

  
  
            <!-- Getting Started Section (shown when no files are loaded) -->
            <div v-if="animations.length === 0 && smplSequences.length === 0 && !converting && Object.keys(markersDatasets).length === 0" class="getting-started-section mb-4">
              <v-card dark class="pa-4" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                <div class="d-flex align-center mb-3">
                  <v-icon color="primary" class="mr-2">mdi-information-outline</v-icon>
                  <h3 class="text-subtitle-1">Getting Started</h3>
                </div>
  
                <div class="text-caption mb-3">
                  <strong>Import Methods:</strong>
                </div>
  
                <div class="mb-3">
                  <v-btn
                    color="primary"
                    small
                    outlined
                    block
                    @click="showSampleSelectionDialog = true"
                    class="mb-2"
                  >
                    <v-icon left small>mdi-play-circle</v-icon>
                    Try Sample Data
                  </v-btn>
                  <div class="text-caption grey--text mb-3">
                    Explore with pre-loaded motion capture data
                  </div>
  
                </div>
  
                <v-divider class="my-3" style="opacity: 0.3;"></v-divider>
  
                <div class="text-caption mb-2">
                  <strong>Workflow Options:</strong>
                </div>
  
                <div class="workflow-steps text-caption">
                  <div class="step-item mb-2">
                    <div class="d-flex align-center">
                      <v-icon x-small color="orange" class="mr-2">mdi-numeric-1-circle</v-icon>
                      <span class="font-weight-medium">OpenSim Files</span>
                    </div>
                    <div class="ml-5 grey--text">
                      Upload .osim model + .mot motion files
                    </div>
                  </div>
  
                  <div class="step-item mb-2">
                    <div class="d-flex align-center">
                      <v-icon x-small color="indigo" class="mr-2">mdi-numeric-2-circle</v-icon>
                      <span class="font-weight-medium">Motion Data</span>
                    </div>
                    <div class="ml-5 grey--text">
                      Load .json files or .trc marker files
                    </div>
                  </div>
  
                  <div class="step-item mb-2">
                    <div class="d-flex align-center">
                      <v-icon x-small color="green" class="mr-2">mdi-numeric-3-circle</v-icon>
                      <span class="font-weight-medium">Enhance</span>
                    </div>
                    <div class="ml-5 grey--text">
                      Add forces (.mot), video, or 3D models
                    </div>
                  </div>
                </div>
  
                <v-divider class="my-3" style="opacity: 0.3;"></v-divider>
  
                <div class="text-caption mb-2">
                  <strong>Tips:</strong>
                </div>
                <ul class="text-caption grey--text pl-4 mb-0">
                  <li class="mb-1">Drag & drop files directly into the viewer (.json, .trc, .osim, .mot)</li>
                  <li class="mb-1">Use Import button for batch uploads</li>
                  <li class="mb-1">Multiple subjects can be loaded together</li>
                  <li class="mb-1">.trc files can be loaded independently</li>
                  <li class="mb-1">.mot force files are automatically detected and positioned at feet</li>
                </ul>
              </v-card>
            </div>
  
            <!-- Legend -->
            <div class="legend flex-grow-1 mb-4">
              <!-- Add animation control buttons -->
              <div class="d-flex align-center mb-4" v-if="animations.length > 0 || smplSequences.length > 0" style="cursor: pointer;" @click="showAnimationsDetails = !showAnimationsDetails">
                <div class="text-subtitle-2 mr-2">Animations</div>
                <v-spacer></v-spacer>
                <v-icon small>{{ showAnimationsDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </div>
              <div class="d-flex align-center mb-4" v-if="animations.length > 0 || smplSequences.length > 0" style="cursor: pointer;" @click="showAnimationsDetails = !showAnimationsDetails">
                <v-spacer></v-spacer>
                <v-btn x-small text color="primary" @click.stop="setAllAnimationsPlayable(true)" class="mr-1">
                  <v-icon x-small left>mdi-play-circle</v-icon>
                  All
                </v-btn>
                <v-btn x-small text color="grey" @click.stop="setAllAnimationsPlayable(false)">
                  <v-icon x-small left>mdi-pause-circle</v-icon>
                  None
                </v-btn>
              </div>
              <v-expand-transition>
                <div v-show="showAnimationsDetails">
  
              <!-- Animation Files List -->
              <div v-for="(animation, index) in animations" :key="`animation-${index}`" class="legend-item mb-4">
                <div class="d-flex mb-2">
                  <div class="color-box" :style="{ backgroundColor: formatColor(colors[index]) }"></div>
                  <div class="ml-2" style="flex-grow: 1; min-width: 0;">
                    <div class="d-flex align-center">
                      <v-text-field v-model="animation.trialName" dense hide-details class="trial-name-input" style="flex: 1;" />
                      <v-icon small class="ml-2" style="cursor: pointer;" @click="toggleAnimationDetails(index)">{{ getAnimationDetailsExpanded(index) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                    </div>
                    <v-expand-transition>
                      <div v-show="getAnimationDetailsExpanded(index)">
                        <div class="file-name text-caption" style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal; line-height: 1.2;">{{ animation.fileName }}</div>
                        <div class="fps-info text-caption grey--text">
                          {{ animation.calculatedFps ? animation.calculatedFps.toFixed(2) + ' fps' : '' }}
                        </div>
                        <!-- Forces section -->
                        <div v-if="forcesDatasets[index]" class="ml-8 mb-2">
                          <div class="d-flex align-center">
                            <v-icon small color="green" class="mr-2">mdi-arrow-up</v-icon>
                            <span class="text-caption">Forces</span>
                            <v-spacer></v-spacer>
                            <v-btn icon x-small @click="toggleForceVisibility(index)">
                              <v-icon x-small>{{ forcesVisible[String(index)] ? 'mdi-eye' : 'mdi-eye-off' }}</v-icon>
                            </v-btn>
                          </div>
                        </div>
  
                        <!-- Markers section -->
                        <div v-if="markersDatasets[index]" class="ml-8 mb-2">
                          <div class="d-flex align-center">
                            <v-icon small color="blue" class="mr-2">mdi-record-circle</v-icon>
                            <span class="text-caption">Markers</span>
                            <v-spacer></v-spacer>
                            <v-btn icon x-small @click="toggleMarkerVisibility(index)">
                              <v-icon x-small>{{ markersVisible[index] ? 'mdi-eye' : 'mdi-eye-off' }}</v-icon>
                            </v-btn>
                          </div>
                        </div>
                      </div>
                    </v-expand-transition>
  
                  </div>
                </div>
  
                <!-- Buttons row - add checkbox here -->
                <v-expand-transition>
                  <div v-show="getAnimationDetailsExpanded(index)">
                <div class="d-flex align-center ml-8" style="flex-wrap: wrap; gap: 4px;">
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <div v-bind="attrs" v-on="on">
                        <v-checkbox
                          v-model="animation.playable"
                          hide-details
                          dense
                          color="primary"
                          class="mt-0 mr-2 playable-checkbox"
                        ></v-checkbox>
                      </div>
                    </template>
                    <span>{{ animation.playable ? 'Animation enabled' : 'Static display (visible but not animating)' }}</span>
                  </v-tooltip>
  
                  <v-menu offset-y :close-on-content-click="false">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-palette</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="color-picker pa-2">
  
                        <div class="d-flex align-center">
                          <v-color-picker
                            v-model="displayColors[index]"
                            :modes="['hex', 'rgba']"
                            show-swatches
                            :swatches="Array.isArray(availableColors) ? availableColors : []"
                            @input="updateSubjectColor(index, $event)"
                            class="flex-grow-1"
                            >
                          </v-color-picker>
                          <v-btn icon small @click="openEyeDropper('subject', index)" title="Pick color from screen" class="ml-2">
                            <v-icon>mdi-eyedropper-variant</v-icon>
                          </v-btn>
                        </div>
                    </v-card>
                  </v-menu>
                  <v-btn icon small class="mr-2" @click="deleteSubject(index)">
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                  <v-btn icon small class="mr-2" @click="toggleSubjectVisibility(index)">
                    <v-icon small :color="animations[index].visible ? 'white' : 'grey'">
                      {{ animations[index].visible ? 'mdi-eye' : 'mdi-eye-off' }}
                    </v-icon>
                  </v-btn>
                  <v-tooltip bottom v-if="convertedJsonDataMap[animation.fileName]">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="downloadConvertedJson(index)"
                      >
                        <v-icon small>mdi-download</v-icon>
                      </v-btn>
                    </template>
                    <span>Download converted JSON file</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="centerCameraOnAnimation(index)"
                      >
                        <v-icon small>mdi-target</v-icon>
                      </v-btn>
                    </template>
                    <span>Center camera on this animation</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="centerModelToOrigin(index)"
                      >
                        <v-icon small>mdi-axis-arrow</v-icon>
                      </v-btn>
                    </template>
                    <span>Center model to origin</span>
                  </v-tooltip>
                  <v-menu offset-y>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2" @click="prepareTransparencyMenu(index)">
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
                    icon
                    small
                    class="mr-2"
                    v-if="animations[index].visible"
                    @click="openMeshDialog(index)"
                  >
                    <v-icon small>mdi-cube-outline</v-icon>
                  </v-btn>
                </div>
  
                <!-- Offset controls -->
                <div class="offset-controls mt-2" style="margin-left: 44px;">
                  <div class="d-flex align-center" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Position</div>
                  </div>
                  <div class="d-flex align-center mb-2" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2" style="width: 12px;">X</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      v-model.number="animation.offset.x"
                      dense
                      @input="debouncedUpdateOffset(index, 'x', animation.offset.x)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">Y</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      v-model.number="animation.offset.y"
                      dense
                      @input="debouncedUpdateOffset(index, 'y', animation.offset.y)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">Z</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      v-model.number="animation.offset.z"
                      dense
                      @input="debouncedUpdateOffset(index, 'z', animation.offset.z)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                  </div>
                  
                  <!-- Rotation controls -->
                  <div class="d-flex align-center" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Rotation (°)</div>
                    <v-btn
                      icon
                      x-small
                      @click="openRotationDialog(index)"
                      class="ml-1"
                    >
                      <v-icon x-small>mdi-rotate-3d-variant</v-icon>
                    </v-btn>
                  </div>
                  <div class="d-flex align-center">
                    <div class="text-caption grey--text mr-2" style="width: 12px;">Y</div>
                    <v-text-field
                      type="number"
                      :step="5"
                      :value="animation.rotation ? Math.round(animation.rotation.y * 180 / Math.PI) : 0"
                      dense
                      @input="debouncedUpdateAnimationRotation(index, 'y', $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">X</div>
                    <v-text-field
                      type="number"
                      :step="5"
                      :value="animation.rotation ? Math.round(animation.rotation.x * 180 / Math.PI) : 0"
                      dense
                      @input="debouncedUpdateAnimationRotation(index, 'x', $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">Z</div>
                    <v-text-field
                      type="number"
                      :step="5"
                      :value="animation.rotation ? Math.round(animation.rotation.z * 180 / Math.PI) : 0"
                      dense
                      @input="debouncedUpdateAnimationRotation(index, 'z', $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                  </div>
                  
                  <!-- FPS Control -->
                  <div class="d-flex align-center mt-2" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Playback Speed</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      :min="0.1"
                      :max="5"
                      v-model.number="animation.speedMultiplier"
                      dense
                      @input="updateAnimationSpeed(index)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <span class="text-caption grey--text ml-2">×</span>
                  </div>
                </div>
                  </div>
                </v-expand-transition>
  
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
  
                <!-- Rotation dialog -->
                <v-dialog
                  v-model="rotationDialogs[index]"
                  max-width="500"
                >
                  <v-card>
                    <v-card-title class="text-subtitle-1">
                      Rotation Controls - {{ animation.trialName }}
                      <v-spacer></v-spacer>
                      <v-btn icon small @click="rotationDialogs[index] = false">
                        <v-icon small>mdi-close</v-icon>
                      </v-btn>
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text class="pa-4">
                      <!-- Y Axis Rotation (most common - vertical axis) -->
                      <div class="mb-4">
                        <div class="d-flex align-center mb-2">
                          <div class="text-subtitle-2 mr-2" style="min-width: 100px;">Y Axis (°):</div>
                          <v-text-field
                            type="number"
                            :step="1"
                            :value="animation.rotation ? Math.round(animation.rotation.y * 180 / Math.PI) : 0"
                            dense
                            @input="debouncedUpdateAnimationRotation(index, 'y', $event)"
                            style="width: 80px"
                            hide-details
                            outlined
                          />
                        </div>
                        <v-slider
                          :value="animation.rotation ? Math.round(animation.rotation.y * 180 / Math.PI) : 0"
                          @input="debouncedUpdateAnimationRotation(index, 'y', $event)"
                          :min="-180"
                          :max="180"
                          :step="1"
                          thumb-label
                          hide-details
                          class="mt-2"
                        ></v-slider>
                      </div>
  
                      <!-- X Axis Rotation -->
                      <div class="mb-4">
                        <div class="d-flex align-center mb-2">
                          <div class="text-subtitle-2 mr-2" style="min-width: 100px;">X Axis (°):</div>
                          <v-text-field
                            type="number"
                            :step="1"
                            :value="animation.rotation ? Math.round(animation.rotation.x * 180 / Math.PI) : 0"
                            dense
                            @input="debouncedUpdateAnimationRotation(index, 'x', $event)"
                            style="width: 80px"
                            hide-details
                            outlined
                          />
                        </div>
                        <v-slider
                          :value="animation.rotation ? Math.round(animation.rotation.x * 180 / Math.PI) : 0"
                          @input="debouncedUpdateAnimationRotation(index, 'x', $event)"
                          :min="-180"
                          :max="180"
                          :step="1"
                          thumb-label
                          hide-details
                          class="mt-2"
                        ></v-slider>
                      </div>
  
                      <!-- Z Axis Rotation -->
                      <div class="mb-2">
                        <div class="d-flex align-center mb-2">
                          <div class="text-subtitle-2 mr-2" style="min-width: 100px;">Z Axis (°):</div>
                          <v-text-field
                            type="number"
                            :step="1"
                            :value="animation.rotation ? Math.round(animation.rotation.z * 180 / Math.PI) : 0"
                            dense
                            @input="debouncedUpdateAnimationRotation(index, 'z', $event)"
                            style="width: 80px"
                            hide-details
                            outlined
                          />
                        </div>
                        <v-slider
                          :value="animation.rotation ? Math.round(animation.rotation.z * 180 / Math.PI) : 0"
                          @input="debouncedUpdateAnimationRotation(index, 'z', $event)"
                          :min="-180"
                          :max="180"
                          :step="1"
                          thumb-label
                          hide-details
                          class="mt-2"
                        ></v-slider>
                      </div>
  
                      <!-- Reset button -->
                      <div class="mt-4 text-center">
                        <v-btn
                          small
                          outlined
                          @click="resetAnimationRotation(index)"
                        >
                          <v-icon small left>mdi-refresh</v-icon>
                          Reset Rotation
                        </v-btn>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-dialog>
              </div>
                </div>
              </v-expand-transition>
  
              <!-- SMPL Sequences -->
              <div
                v-for="sequence in smplSequences"
                :key="`smpl-${sequence.id}`"
                :class="['legend-item', 'mb-4', { 'active-subject': isActiveSubject('smpl', sequence.id) }]"
              >
                <div class="d-flex mb-2 align-start">
                  <div
                    class="color-box selectable"
                    :style="{ backgroundColor: formatColor(sequence.color) }"
                    @click="setActiveSubject('smpl', sequence.id)"
                  ></div>
                  <div class="ml-2" style="flex-grow: 1; min-width: 0; padding-right: 8px; overflow: hidden;">
                    <div class="d-flex align-center">
                      <div class="text-subtitle-2" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;">{{ sequence.name }}</div>
                      <v-icon small class="ml-2" style="cursor: pointer; flex-shrink: 0;" @click="toggleSmplDetails(sequence.id)">{{ getSmplDetailsExpanded(sequence.id) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                    </div>
                    <v-expand-transition>
                      <div v-show="getSmplDetailsExpanded(sequence.id)">
                        <div class="text-caption grey--text">
                          {{ sequence.frameCount }} frames @ {{ sequence.fps ? sequence.fps.toFixed(2) : frameRate.toFixed(2) }} fps
                        </div>
                        <div class="text-caption grey--text">
                          {{ sequence.vertexCount }} vertices, {{ sequence.jointCount }} joints
                        </div>
                      </div>
                    </v-expand-transition>
                  </div>
                  <v-expand-transition>
                    <div v-show="getSmplDetailsExpanded(sequence.id)" class="d-flex align-start" style="flex-shrink: 0;">
                  <v-btn
                    icon
                    small
                    class="mr-2"
                    @click="toggleSmplSequenceVisibility(sequence.id)"
                  >
                    <v-icon small :color="sequence.visible ? 'white' : 'grey'">
                      {{ sequence.visible ? 'mdi-eye' : 'mdi-eye-off' }}
                    </v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    small
                    class="mr-2"
                    v-if="sequence.skeleton"
                    @click="toggleSmplSkeleton(sequence.id)"
                  >
                    <v-icon small>
                      {{ sequence.showSkeleton ? 'mdi-bone' : 'mdi-bone-off' }}
                    </v-icon>
                  </v-btn>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="centerSmplModelToOrigin(sequence.id)"
                      >
                        <v-icon small>mdi-axis-arrow</v-icon>
                      </v-btn>
                    </template>
                    <span>Center model to origin</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="setActiveSubject('smpl', sequence.id)"
                      >
                        <v-icon small :color="isActiveSubject('smpl', sequence.id) ? 'cyan lighten-2' : 'grey'">
                          {{ isActiveSubject('smpl', sequence.id) ? 'mdi-crosshairs-gps' : 'mdi-crosshairs' }}
                        </v-icon>
                      </v-btn>
                    </template>
                    <span>Select as active subject</span>
                  </v-tooltip>
                  <v-btn icon small color="error" @click="removeSmplSequence(sequence.id)">
                    <v-icon small>mdi-delete</v-icon>
                  </v-btn>
                    </div>
                  </v-expand-transition>
                </div>
  
                <v-expand-transition>
                  <div v-show="getSmplDetailsExpanded(sequence.id)">
                <div class="d-flex align-center ml-8" style="flex-wrap: wrap; gap: 4px;">
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <div v-bind="attrs" v-on="on">
                        <v-checkbox
                          :input-value="sequence.playable"
                          hide-details
                          dense
                          color="primary"
                          class="mt-0 mr-2 playable-checkbox"
                          @change="setSmplSequencePlayable(sequence.id, $event)"
                        ></v-checkbox>
                      </div>
                    </template>
                    <span>{{ sequence.playable ? 'Sequence enabled' : 'Static pose (visible but not animating)' }}</span>
                  </v-tooltip>
  
                  <v-menu offset-y :close-on-content-click="false">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-palette</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="color-picker pa-2">
                      <div class="d-flex align-center">
                        <v-color-picker
                          v-model="sequence.displayColor"
                          :modes="['hex', 'rgba']"
                          show-swatches
                          :swatches="Array.isArray(availableColors) ? availableColors : []"
                          @input="updateSmplSequenceColor(sequence.id, $event)"
                          class="flex-grow-1"
                        >
                        </v-color-picker>
                        <v-btn icon small @click="openEyeDropper('smpl', sequence.id)" title="Pick color from screen" class="ml-2">
                          <v-icon>mdi-eyedropper-variant</v-icon>
                        </v-btn>
                      </div>
                    </v-card>
                  </v-menu>
  
                  <v-menu offset-y>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-opacity</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="transparency-picker pa-3" width="250">
                      <div class="text-subtitle-2 mb-2">
                        Transparency
                        <span class="text-caption ml-2">
                          ({{ Math.round((1 - (sequence.opacity || 1)) * 100) }}%)
                        </span>
                      </div>
                      <v-slider
                        :value="(1 - (sequence.opacity || 1)) * 100"
                        @input="value => updateSmplOpacity(sequence.id, 1 - value / 100)"
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
  
                  <div class="text-caption grey--text ml-2">
                    Gender: {{ sequence.gender }}
                  </div>
                </div>
  
                <!-- Offset controls for SMPL -->
                <div class="offset-controls mt-2" style="margin-left: 44px;">
                  <div class="d-flex align-center" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Position</div>
                  </div>
                  <div class="d-flex align-center mb-2" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2" style="width: 12px;">X</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      v-model.number="sequence.offset.x"
                      dense
                      @input="debouncedUpdateSmplOffset(sequence.id, 'x', sequence.offset.x)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">Y</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      v-model.number="sequence.offset.y"
                      dense
                      @input="debouncedUpdateSmplOffset(sequence.id, 'y', sequence.offset.y)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">Z</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      v-model.number="sequence.offset.z"
                      dense
                      @input="debouncedUpdateSmplOffset(sequence.id, 'z', sequence.offset.z)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                  </div>
                  
                  <!-- Rotation controls for SMPL -->
                  <div class="d-flex align-center" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Rotation (°)</div>
                    <v-btn
                      icon
                      x-small
                      @click="openSmplRotationDialog(sequence.id)"
                      class="ml-1"
                    >
                      <v-icon x-small>mdi-rotate-3d-variant</v-icon>
                    </v-btn>
                  </div>
                  <div class="d-flex align-center">
                    <div class="text-caption grey--text mr-2" style="width: 12px;">Y</div>
                    <v-text-field
                      type="number"
                      :step="5"
                      :value="sequence.rotation ? Math.round(sequence.rotation.y * 180 / Math.PI) : 0"
                      dense
                      @input="debouncedUpdateSmplRotation(sequence.id, 'y', $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">X</div>
                    <v-text-field
                      type="number"
                      :step="5"
                      :value="sequence.rotation ? Math.round(sequence.rotation.x * 180 / Math.PI) : 0"
                      dense
                      @input="debouncedUpdateSmplRotation(sequence.id, 'x', $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                    <div class="text-caption grey--text mx-2" style="width: 12px;">Z</div>
                    <v-text-field
                      type="number"
                      :step="5"
                      :value="sequence.rotation ? Math.round(sequence.rotation.z * 180 / Math.PI) : 0"
                      dense
                      @input="debouncedUpdateSmplRotation(sequence.id, 'z', $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                  </div>
                </div>
                  </div>
                </v-expand-transition>
  
                <!-- Rotation dialog for SMPL -->
                <v-dialog
                  v-model="smplRotationDialogs[sequence.id]"
                  max-width="500"
                >
                  <v-card>
                    <v-card-title class="text-subtitle-1">
                      Rotation Controls - {{ sequence.name }}
                      <v-spacer></v-spacer>
                      <v-btn icon small @click="smplRotationDialogs[sequence.id] = false">
                        <v-icon small>mdi-close</v-icon>
                      </v-btn>
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text class="pa-4">
                      <!-- Y Axis Rotation -->
                      <div class="mb-4">
                        <div class="d-flex align-center mb-2">
                          <div class="text-subtitle-2 mr-2" style="min-width: 100px;">Y Axis (°):</div>
                          <v-text-field
                            type="number"
                            :step="1"
                            :value="sequence.rotation ? Math.round(sequence.rotation.y * 180 / Math.PI) : 0"
                            dense
                            @input="debouncedUpdateSmplRotation(sequence.id, 'y', $event)"
                            style="width: 80px"
                            hide-details
                            outlined
                          />
                        </div>
                        <v-slider
                          :value="sequence.rotation ? Math.round(sequence.rotation.y * 180 / Math.PI) : 0"
                          @input="debouncedUpdateSmplRotation(sequence.id, 'y', $event)"
                          :min="-180"
                          :max="180"
                          :step="1"
                          thumb-label
                          hide-details
                          class="mt-2"
                        ></v-slider>
                      </div>
  
                      <!-- X Axis Rotation -->
                      <div class="mb-4">
                        <div class="d-flex align-center mb-2">
                          <div class="text-subtitle-2 mr-2" style="min-width: 100px;">X Axis (°):</div>
                          <v-text-field
                            type="number"
                            :step="1"
                            :value="sequence.rotation ? Math.round(sequence.rotation.x * 180 / Math.PI) : 0"
                            dense
                            @input="debouncedUpdateSmplRotation(sequence.id, 'x', $event)"
                            style="width: 80px"
                            hide-details
                            outlined
                          />
                        </div>
                        <v-slider
                          :value="sequence.rotation ? Math.round(sequence.rotation.x * 180 / Math.PI) : 0"
                          @input="debouncedUpdateSmplRotation(sequence.id, 'x', $event)"
                          :min="-180"
                          :max="180"
                          :step="1"
                          thumb-label
                          hide-details
                          class="mt-2"
                        ></v-slider>
                      </div>
  
                      <!-- Z Axis Rotation -->
                      <div class="mb-2">
                        <div class="d-flex align-center mb-2">
                          <div class="text-subtitle-2 mr-2" style="min-width: 100px;">Z Axis (°):</div>
                          <v-text-field
                            type="number"
                            :step="1"
                            :value="sequence.rotation ? Math.round(sequence.rotation.z * 180 / Math.PI) : 0"
                            dense
                            @input="debouncedUpdateSmplRotation(sequence.id, 'z', $event)"
                            style="width: 80px"
                            hide-details
                            outlined
                          />
                        </div>
                        <v-slider
                          :value="sequence.rotation ? Math.round(sequence.rotation.z * 180 / Math.PI) : 0"
                          @input="debouncedUpdateSmplRotation(sequence.id, 'z', $event)"
                          :min="-180"
                          :max="180"
                          :step="1"
                          thumb-label
                          hide-details
                          class="mt-2"
                        ></v-slider>
                      </div>
  
                      <!-- Reset button -->
                      <div class="mt-4 text-center">
                        <v-btn
                          small
                          outlined
                          @click="resetSmplRotation(sequence.id)"
                        >
                          <v-icon small left>mdi-refresh</v-icon>
                          Reset Rotation
                        </v-btn>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-dialog>
                
                <!-- FPS Control for SMPL -->
                <div class="d-flex align-center mt-2" style="margin-left: 44px; border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                  <div class="text-caption grey--text mr-2">Playback Speed</div>
                  <v-text-field
                    type="number"
                    :step="0.1"
                    :min="0.1"
                    :max="5"
                    v-model.number="sequence.speedMultiplier"
                    dense
                    @input="updateSmplSpeed(sequence.id)"
                    style="width: 70px"
                    class="grey--text text--darken-1"
                    hide-details
                  />
                  <span class="text-caption grey--text ml-2">×</span>
                </div>
              </div>
  
              <!-- Forces Visualization Section -->
              <div v-if="Object.keys(forcesDatasets).length > 0" class="d-flex align-center mb-4" style="cursor: pointer;" @click="showForcesDetails = !showForcesDetails">
                <div class="text-subtitle-2 mr-2">Forces</div>
                <v-spacer></v-spacer>
                <v-icon small>{{ showForcesDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </div>
              <v-expand-transition>
                <div v-show="showForcesDetails">
              <div v-for="(forcesData, animationIndex) in forcesDatasets" :key="`forces-${animationIndex}`" class="legend-item mb-4">
                <div class="d-flex mb-2">
                  <div class="color-box" :style="{ backgroundColor: getForceColor(animationIndex) }"></div>
                  <div class="flex-grow-1 ml-2" style="min-width: 0;">
                    <div class="text-subtitle-2">Ground Reaction Forces</div>
                    <div class="file-name text-caption" style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal; line-height: 1.2;">{{ forcesData.fileName }}</div>
                    <div class="fps-info text-caption grey--text">
                      Associated with {{ animations[animationIndex]?.trialName || 'Subject ' + (parseInt(animationIndex) + 1) }}
                    </div>
                    <div class="fps-info text-caption grey--text">
                      {{ getForceArrowCount(animationIndex) }} Force Platforms
                    </div>
  
                    <!-- Current Force Values Display -->
                    <div v-if="showForces && getCurrentForceValues(animationIndex)" class="force-values mt-2 pa-2" :style="{ background: 'rgba(0, 0, 0, 0.2)', borderRadius: '4px', borderLeft: `3px solid ${getForceColor(animationIndex)}` }">
                      <div class="text-caption font-weight-bold mb-1" :style="{ color: getForceColor(animationIndex) }">Current Forces (N)</div>
                      <div v-for="(platform, platformName) in getCurrentForceValues(animationIndex)" :key="platformName" class="platform-forces mb-1">
                        <div class="text-caption font-weight-medium" style="color: #cccccc;">{{ platformName === 'R' ? 'Right Foot' : 'Left Foot' }}:</div>
                        <div class="d-flex justify-space-between text-caption" style="font-family: monospace;">
                          <span>X: {{ platform.fx.toFixed(0) }}</span>
                          <span>Y: {{ platform.fy.toFixed(0) }}</span>
                          <span>Z: {{ platform.fz.toFixed(0) }}</span>
                        </div>
                        <div class="text-caption grey--text" style="font-family: monospace;">
                          Mag: {{ platform.magnitude.toFixed(0) }}N
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
  
                <div class="mt-3 d-flex align-center ml-8">
                  <v-btn icon small class="mr-2" @click="showForces = !showForces">
                    <v-icon small :color="showForces ? 'white' : 'grey'">
                      {{ showForces ? 'mdi-eye' : 'mdi-eye-off' }}
                    </v-icon>
                  </v-btn>
  
                  <v-menu offset-y :close-on-content-click="false">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-palette</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="color-picker pa-2">
                      <div class="d-flex align-center">
                        <v-color-picker
                          :value="getForceDisplayColor(animationIndex)"
                          :modes="['hex', 'rgba']"
                          show-swatches
                          :swatches="Array.isArray(availableColors) ? availableColors : []"
                          @input="(color) => updateForceColor(color, animationIndex)"
                          class="flex-grow-1"
                        ></v-color-picker>
                        <v-btn icon small @click="openEyeDropper('force', animationIndex)" title="Pick color from screen" class="ml-2">
                          <v-icon>mdi-eyedropper-variant</v-icon>
                        </v-btn>
                      </div>
                    </v-card>
                  </v-menu>
  
                  <v-menu offset-y :close-on-content-click="false">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-arrow-expand-all</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="scale-picker pa-3" width="250">
                      <div class="text-subtitle-2 mb-2">
                        Arrow Scale
                        <span class="text-caption ml-2">
                          ({{ forceScale }})
                        </span>
                      </div>
                      <v-slider
                        v-model="forceScale"
                        :min="0.001"
                        :max="0.005"
                        step="0.001"
                        hide-details
                        :thumb-label="true"
                        thumb-size="24"
                        @input="updateForceScale"
                      >
                        <template v-slot:thumb-label="{ value }">
                          {{ (value * 1000).toFixed(0) }}
                        </template>
                        <template v-slot:prepend>
                          <div class="text-caption grey--text">Small</div>
                        </template>
                        <template v-slot:append>
                          <div class="text-caption grey--text">Large</div>
                        </template>
                      </v-slider>
                    </v-card>
                  </v-menu>
  
                  <v-menu offset-y :close-on-content-click="false">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-filter</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="scale-picker pa-3" width="250">
                      <div class="text-subtitle-2 mb-2">
                        Minimum Force Threshold
                        <span class="text-caption ml-2">
                          ({{ forceMinMagnitude }}N)
                        </span>
                      </div>
                      <v-slider
                        v-model="forceMinMagnitude"
                        :min="0"
                        :max="100"
                        step="1"
                        hide-details
                        :thumb-label="true"
                        thumb-size="24"
                        @input="updateForceMinMagnitude"
                      >
                        <template v-slot:thumb-label="{ value }">
                          {{ value }}N
                        </template>
                        <template v-slot:prepend>
                          <div class="text-caption grey--text">0N</div>
                        </template>
                        <template v-slot:append>
                          <div class="text-caption grey--text">100N</div>
                        </template>
                      </v-slider>
                    </v-card>
                  </v-menu>
  
                  <v-btn icon small class="mr-2" @click="clearForceArrowsForAnimation(animationIndex)">
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                </div>
  
                <!-- Divider -->
                <v-divider class="mt-4" style="opacity: 0.2"></v-divider>
              </div>
                </div>
              </v-expand-transition>
  
              <!-- Custom Objects List -->
              <div v-if="customObjects.length > 0" class="d-flex align-center mb-4" style="cursor: pointer;" @click="showCustomObjectsDetails = !showCustomObjectsDetails">
                <div class="text-subtitle-2 mr-2">Custom Objects</div>
                <v-spacer></v-spacer>
                <v-icon small>{{ showCustomObjectsDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </div>
              <v-expand-transition>
                <div v-show="showCustomObjectsDetails">
              <div v-for="obj in customObjects" :key="obj.id" class="legend-item mb-4">
                <div class="d-flex mb-2">
                  <div class="color-box" :style="{ backgroundColor: obj.color }"></div>
                  <div class="ml-2" style="flex-grow: 1;">
                    <v-text-field v-model="obj.name" dense hide-details class="trial-name-input" />
                    <div class="file-name text-caption">{{ obj.name }}</div>
                  </div>
                </div>
  
                <!-- Buttons row -->
                <div class="d-flex align-center ml-8" style="flex-wrap: wrap; gap: 4px;">
                  <v-menu offset-y :close-on-content-click="false">
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                        <v-icon small>mdi-palette</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="color-picker pa-2">
                      <div class="d-flex align-center">
                        <v-color-picker
                          v-model="objColor"
                          :modes="['hex', 'rgba']"
                          show-swatches
                          :swatches="Array.isArray(availableColors) ? availableColors : []"
                          @input="value => updateObjectColor(obj.id, '#' + value.hex)"
                          class="flex-grow-1"
                        ></v-color-picker>
                        <v-btn icon small @click="openEyeDropper('object', obj.id)" title="Pick color from screen" class="ml-2">
                          <v-icon>mdi-eyedropper-variant</v-icon>
                        </v-btn>
                      </div>
                    </v-card>
                  </v-menu>
                  <v-btn icon small class="mr-2" @click="removeCustomObject(obj.id)">
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                  <v-btn icon small class="mr-2" @click="toggleObjectVisibility(obj.id)">
                    <v-icon small :color="isObjectVisible(obj.id) ? 'white' : 'grey'">
                      {{ isObjectVisible(obj.id) ? 'mdi-eye' : 'mdi-eye-off' }}
                    </v-icon>
                  </v-btn>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="centerCameraOnObject(obj.id)"
                      >
                        <v-icon small>mdi-target</v-icon>
                      </v-btn>
                    </template>
                    <span>Center camera on this object</span>
                  </v-tooltip>
                  <v-menu offset-y>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn icon small v-bind="attrs" v-on="on" class="mr-2" @click="prepareTransparencyMenu(index)">
                        <v-icon small>mdi-opacity</v-icon>
                      </v-btn>
                    </template>
                    <v-card class="transparency-picker pa-3" width="250">
                      <div class="text-subtitle-2 mb-2">
                        Transparency
                        <span class="text-caption ml-2">
                          ({{ Math.round((1 - obj.opacity) * 100) }}%)
                        </span>
                      </div>
                      <v-slider
                        :value="(1 - (obj.opacity || 1)) * 100"
                        @input="value => updateObjectOpacity(obj.id, 1 - value / 100)"
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
                </div>
  
                <!-- Position controls -->
                <div class="offset-controls mt-2" style="margin-left: 44px;">
                  <div class="d-flex align-center mb-2" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Position</div>
                    <div class="d-flex align-center">
                      <div class="text-caption grey--text mr-2" style="width: 12px;">X</div>
                      <v-text-field
                        type="number"
                        :step="0.1"
                        v-model.number="obj.position.x"
                        dense
                        @input="debouncedUpdateObjectPosition(obj.id, 'x', obj.position.x)"
                        style="width: 70px"
                        class="grey--text text--darken-1"
                        hide-details
                      />
                      <div class="text-caption grey--text mx-2" style="width: 12px;">Y</div>
                      <v-text-field
                        type="number"
                        :step="0.1"
                        v-model.number="obj.position.y"
                        dense
                        @input="debouncedUpdateObjectPosition(obj.id, 'y', obj.position.y)"
                        style="width: 70px"
                        class="grey--text text--darken-1"
                        hide-details
                      />
                      <div class="text-caption grey--text mx-2" style="width: 12px;">Z</div>
                      <v-text-field
                        type="number"
                        :step="0.1"
                        v-model.number="obj.position.z"
                        dense
                        @input="debouncedUpdateObjectPosition(obj.id, 'z', obj.position.z)"
                        style="width: 70px"
                        class="grey--text text--darken-1"
                        hide-details
                      />
                    </div>
                  </div>
  
                  <!-- Rotation controls -->
                  <div class="d-flex align-center mb-2" style="border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                    <div class="text-caption grey--text mr-2">Rotation</div>
                    <div class="d-flex align-center">
                      <div class="text-caption grey--text mr-2" style="width: 12px;">X</div>
                      <v-text-field
                        type="number"
                        :step="5"
                        :value="obj.rotation ? obj.rotation.x : 0"
                        dense
                        @input="debouncedUpdateObjectRotation(obj.id, 'x', $event)"
                        style="width: 70px"
                        class="grey--text text--darken-1"
                        hide-details
                      />
                      <div class="text-caption grey--text mx-2" style="width: 12px;">Y</div>
                      <v-text-field
                        type="number"
                        :step="5"
                        :value="obj.rotation ? obj.rotation.y : 0"
                        dense
                        @input="debouncedUpdateObjectRotation(obj.id, 'y', $event)"
                        style="width: 70px"
                        class="grey--text text--darken-1"
                        hide-details
                      />
                      <div class="text-caption grey--text mx-2" style="width: 12px;">Z</div>
                      <v-text-field
                        type="number"
                        :step="5"
                        :value="obj.rotation ? obj.rotation.z : 0"
                        dense
                        @input="debouncedUpdateObjectRotation(obj.id, 'z', $event)"
                        style="width: 70px"
                        class="grey--text text--darken-1"
                        hide-details
                      />
                    </div>
                  </div>
  
                  <!-- Scale control -->
                  <div class="d-flex align-center">
                    <div class="text-caption grey--text mr-2">Scale</div>
                    <v-text-field
                      type="number"
                      :step="0.1"
                      :min="0.1"
                      :value="obj.scale"
                      dense
                      @input="debouncedUpdateObjectScale(obj.id, $event)"
                      style="width: 70px"
                      class="grey--text text--darken-1"
                      hide-details
                    />
                  </div>
                </div>
              </div>
                </div>
              </v-expand-transition>
            </div>
  
            <!-- Standalone Marker Visualization Section (when no animations exist) -->
            <div v-if="animations.length === 0 && smplSequences.length === 0 && Object.keys(markersDatasets).length > 0" class="d-flex align-center mb-4" style="cursor: pointer;" @click="showMarkersDetails = !showMarkersDetails">
              <div class="text-subtitle-2 mr-2">Markers</div>
              <v-spacer></v-spacer>
              <v-icon small>{{ showMarkersDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            </div>
            <v-expand-transition>
              <div v-show="showMarkersDetails" v-if="animations.length === 0 && smplSequences.length === 0 && Object.keys(markersDatasets).length > 0">
            <template v-if="animations.length === 0 && smplSequences.length === 0 && Object.keys(markersDatasets).length > 0">
              <div v-for="(markersData, animationIndex) in markersDatasets" :key="`standalone-markers-${animationIndex}`" class="legend-item mb-4">
              <div class="d-flex mb-2">
                <div class="color-box" :style="{ backgroundColor: getMarkerColor(animationIndex) }"></div>
                <div class="flex-grow-1 ml-2" style="min-width: 0;">
                  <div class="text-subtitle-2">{{ markersData.fileName || 'Motion Capture Markers' }}</div>
                  <div class="file-name text-caption grey--text" style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal; line-height: 1.2;">Standalone Markers</div>
                  <div class="fps-info text-caption grey--text">
                    {{ markersData.markers.length }} Markers
                  </div>
  
                  <!-- Current Marker Values Display for standalone -->
                  <div v-if="showMarkers && selectedMarker" class="marker-values mt-2 pa-2" style="background: rgba(255, 0, 0, 0.1); border-radius: 4px; border-left: 3px solid #ff0000;">
                    <div class="text-caption font-weight-bold mb-1" style="color: #ff0000;">Selected Marker</div>
                    <div class="text-caption font-weight-medium" style="color: #cccccc;">{{ selectedMarker.name }}</div>
                    <div class="d-flex justify-space-between text-caption" style="font-family: monospace;">
                      <span>X: {{ selectedMarker.position.x.toFixed(3) }}</span>
                      <span>Y: {{ selectedMarker.position.y.toFixed(3) }}</span>
                      <span>Z: {{ selectedMarker.position.z.toFixed(3) }}</span>
                    </div>
                    <div class="text-caption grey--text" style="font-family: monospace;">
                      Position (meters)
                    </div>
                  </div>
  
                  <!-- Distance Measurement Display for standalone -->
                  <div v-if="measurementMode && measurementMarkers.length > 0" class="measurement-display mt-2 pa-2" style="background: rgba(0, 255, 0, 0.1); border-radius: 4px; border-left: 3px solid #00ff00;">
                    <div class="text-caption font-weight-bold mb-1" style="color: #00ff00;">Distance Measurement</div>
                    <div v-if="measurementMarkers.length === 1" class="text-caption" style="color: #cccccc;">
                      Selected: {{ measurementMarkers[0].name }}
                      <br><span class="grey--text">Hold Cmd/Shift + Click another marker</span>
                    </div>
                    <div v-else-if="measurementMarkers.length === 2" class="text-caption" style="color: #cccccc;">
                      <div class="font-weight-medium">{{ measurementMarkers[0].name }} ↔ {{ measurementMarkers[1].name }}</div>
                      <div class="text-h6 mt-1" style="color: #00ff00; font-family: monospace;">{{ currentDistance.toFixed(3) }} m</div>
                      <div class="grey--text">Distance (meters)</div>
                    </div>
                  </div>
                </div>
              </div>
  
              <div class="mt-3 d-flex align-center ml-8">
                <v-btn icon small class="mr-2" @click="toggleMarkerVisibility(animationIndex)">
                  <v-icon small :color="getMarkerVisibility(animationIndex) ? 'white' : 'grey'">
                    {{ getMarkerVisibility(animationIndex) ? 'mdi-eye' : 'mdi-eye-off' }}
                  </v-icon>
                </v-btn>
  
                <v-menu offset-y :close-on-content-click="false">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                      <v-icon small>mdi-palette</v-icon>
                    </v-btn>
                  </template>
                  <v-card class="color-picker pa-2">
                    <div class="d-flex align-center">
                      <v-color-picker
                        :value="getMarkerDisplayColor(animationIndex)"
                        :modes="['hex', 'rgba']"
                        show-swatches
                        :swatches="Array.isArray(availableColors) ? availableColors : []"
                        @input="(color) => updateMarkerColor(color, animationIndex)"
                        class="flex-grow-1"
                      ></v-color-picker>
                      <v-btn icon small @click="openEyeDropper('marker', animationIndex)" title="Pick color from screen" class="ml-2">
                        <v-icon>mdi-eyedropper-variant</v-icon>
                      </v-btn>
                    </div>
                  </v-card>
                </v-menu>
  
                <v-menu offset-y :close-on-content-click="false">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                      <v-icon small>mdi-resize</v-icon>
                    </v-btn>
                  </template>
                  <v-card class="size-picker pa-3" width="250">
                    <div class="text-subtitle-2 mb-2">
                      Marker Size
                      <span class="text-caption ml-2">
                        ({{ markerSize }})
                      </span>
                    </div>
                    <v-slider
                      v-model="markerSize"
                      :min="1"
                      :max="20"
                      step="0.5"
                      hide-details
                      :thumb-label="true"
                      thumb-size="24"
                      @input="updateMarkerSize"
                    >
                      <template v-slot:thumb-label="{ value }">
                        {{ value }}
                      </template>
                      <template v-slot:prepend>
                        <div class="text-caption grey--text">Small</div>
                      </template>
                      <template v-slot:append>
                        <div class="text-caption grey--text">Large</div>
                      </template>
                    </v-slider>
                  </v-card>
                </v-menu>
  
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small class="mr-2" @click="toggleMeasurementMode" :color="measurementMode ? 'success' : 'grey'" v-bind="attrs" v-on="on">
                      <v-icon small>mdi-ruler</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ measurementMode ? 'Disable distance measurement' : 'Enable distance measurement' }}</span>
                </v-tooltip>
  
                <v-btn icon small class="mr-2" @click="clearMarkersForAnimation(animationIndex)">
                  <v-icon small color="error">mdi-delete</v-icon>
                </v-btn>
              </div>
  
              <!-- Divider -->
              <v-divider class="mt-4" style="opacity: 0.2"></v-divider>
              </div>
            </template>
              </div>
            </v-expand-transition>
  
            <!-- Clear All Markers Button (only show when there are multiple marker files) -->
            <div v-if="animations.length === 0 && smplSequences.length === 0 && Object.keys(markersDatasets).length > 1" class="mb-4">
              <v-btn
                color="error"
                small
                outlined
                block
                @click="clearAllMarkers"
              >
                <v-icon left small>mdi-delete-sweep</v-icon>
                Clear All Marker Files
              </v-btn>
            </div>
  
            <!-- Marker Visualization Section (only when animations exist) -->
            <div v-if="(animations.length > 0 || smplSequences.length > 0) && Object.keys(markersDatasets).length > 0" class="d-flex align-center mb-4" style="cursor: pointer;" @click="showMarkersDetails = !showMarkersDetails">
              <div class="text-subtitle-2 mr-2">Markers</div>
              <v-spacer></v-spacer>
              <v-icon small>{{ showMarkersDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            </div>
            <v-expand-transition>
              <div v-show="showMarkersDetails">
            <template v-if="animations.length > 0 || smplSequences.length > 0">
            <div v-for="(markersData, animationIndex) in markersDatasets" :key="`markers-${animationIndex}`" class="legend-item mb-4">
              <div class="d-flex mb-2">
                <div class="color-box" :style="{ backgroundColor: getMarkerColor(animationIndex) }"></div>
                <div class="flex-grow-1 ml-2" style="min-width: 0;">
                  <div class="text-subtitle-2">{{ markersData.fileName || 'Motion Capture Markers' }}</div>
                  <div class="file-name text-caption grey--text" style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal; line-height: 1.2;">Motion Capture Markers</div>
                  <div class="fps-info text-caption grey--text">
                    Associated with {{ animations[animationIndex]?.trialName || 'Subject ' + (parseInt(animationIndex) + 1) }}
                  </div>
                  <div class="fps-info text-caption grey--text">
                    {{ markersData.markers.length }} Markers
                  </div>
  
                  <!-- Current Marker Values Display -->
                  <div v-if="showMarkers && selectedMarker && selectedMarker.animationIndex == animationIndex" class="marker-values mt-2 pa-2" style="background: rgba(255, 0, 0, 0.1); border-radius: 4px; border-left: 3px solid #ff0000;">
                    <div class="text-caption font-weight-bold mb-1" style="color: #ff0000;">Selected Marker</div>
                    <div class="text-caption font-weight-medium" style="color: #cccccc;">{{ selectedMarker.name }}</div>
                    <div class="d-flex justify-space-between text-caption" style="font-family: monospace;">
                      <span>X: {{ selectedMarker.position.x.toFixed(3) }}</span>
                      <span>Y: {{ selectedMarker.position.y.toFixed(3) }}</span>
                      <span>Z: {{ selectedMarker.position.z.toFixed(3) }}</span>
                    </div>
                    <div class="text-caption grey--text" style="font-family: monospace;">
                      Position (meters)
                    </div>
                  </div>
  
                  <!-- Distance Measurement Display for animations -->
                  <div v-if="measurementMode && measurementMarkers.length > 0" class="measurement-display mt-2 pa-2" style="background: rgba(0, 255, 0, 0.1); border-radius: 4px; border-left: 3px solid #00ff00;">
                    <div class="text-caption font-weight-bold mb-1" style="color: #00ff00;">Distance Measurement</div>
                    <div v-if="measurementMarkers.length === 1" class="text-caption" style="color: #cccccc;">
                      Selected: {{ measurementMarkers[0].name }}
                      <br><span class="grey--text">Hold Cmd/Shift + Click another marker</span>
                    </div>
                    <div v-else-if="measurementMarkers.length === 2" class="text-caption" style="color: #cccccc;">
                      <div class="font-weight-medium">{{ measurementMarkers[0].name }} ↔ {{ measurementMarkers[1].name }}</div>
                      <div class="text-h6 mt-1" style="color: #00ff00; font-family: monospace;">{{ currentDistance.toFixed(3) }} m</div>
                      <div class="grey--text">Distance (meters)</div>
                    </div>
                  </div>
                </div>
              </div>
  
              <div class="mt-3 d-flex align-center ml-8">
                <v-btn icon small class="mr-2" @click="showMarkers = !showMarkers">
                  <v-icon small :color="showMarkers ? 'white' : 'grey'">
                    {{ showMarkers ? 'mdi-eye' : 'mdi-eye-off' }}
                  </v-icon>
                </v-btn>
  
                <v-menu offset-y :close-on-content-click="false">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                      <v-icon small>mdi-palette</v-icon>
                    </v-btn>
                  </template>
                  <v-card class="color-picker pa-2">
                    <div class="d-flex align-center">
                      <v-color-picker
                        :value="getMarkerDisplayColor(animationIndex)"
                        :modes="['hex', 'rgba']"
                        show-swatches
                        :swatches="Array.isArray(availableColors) ? availableColors : []"
                        @input="(color) => updateMarkerColor(color, animationIndex)"
                        class="flex-grow-1"
                      ></v-color-picker>
                      <v-btn icon small @click="openEyeDropper('marker', animationIndex)" title="Pick color from screen" class="ml-2">
                        <v-icon>mdi-eyedropper-variant</v-icon>
                      </v-btn>
                    </div>
                  </v-card>
                </v-menu>
  
                <v-menu offset-y :close-on-content-click="false">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small v-bind="attrs" v-on="on" class="mr-2">
                      <v-icon small>mdi-resize</v-icon>
                    </v-btn>
                  </template>
                  <v-card class="size-picker pa-3" width="250">
                    <div class="text-subtitle-2 mb-2">
                      Marker Size
                      <span class="text-caption ml-2">
                        ({{ markerSize }})
                      </span>
                    </div>
                    <v-slider
                      v-model="markerSize"
                      :min="1"
                      :max="20"
                      step="0.5"
                      hide-details
                      :thumb-label="true"
                      thumb-size="24"
                      @input="updateMarkerSize"
                    >
                      <template v-slot:thumb-label="{ value }">
                        {{ value }}
                      </template>
                      <template v-slot:prepend>
                        <div class="text-caption grey--text">Small</div>
                      </template>
                      <template v-slot:append>
                        <div class="text-caption grey--text">Large</div>
                      </template>
                    </v-slider>
                  </v-card>
                </v-menu>
  
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small class="mr-2" @click="toggleMeasurementMode" :color="measurementMode ? 'success' : 'grey'" v-bind="attrs" v-on="on">
                      <v-icon small>mdi-ruler</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ measurementMode ? 'Disable distance measurement' : 'Enable distance measurement' }}</span>
                </v-tooltip>
  
                <v-btn icon small class="mr-2" @click="clearMarkersForAnimation(animationIndex)">
                  <v-icon small color="error">mdi-delete</v-icon>
                </v-btn>
              </div>
  
              <!-- Divider -->
              <v-divider class="mt-4" style="opacity: 0.2"></v-divider>
            </div>
            </template>
              </div>
            </v-expand-transition>
  
  
          </div>
        </div>
      </div>
  
      <!-- c -->
      <v-btn
        icon
        dark
        class="left-sidebar-toggle"
        :class="{ 'sidebar-open': showLeftSidebar }"
        @click="showLeftSidebar = !showLeftSidebar"
        v-if="$route.query.embed !== 'true'"
      >
        <v-icon>{{ showLeftSidebar ? 'mdi-chevron-left' : 'mdi-chevron-right' }}</v-icon>
      </v-btn>
  
      <div class="viewer flex-grow-1" :class="{ 'sidebar-hidden': !showSidebar, 'left-sidebar-shown': showLeftSidebar, 'is-embedded': $route.query.embed === 'true' }" @dragover.prevent @drop.prevent="handleDrop">
        <!-- Camera Controls - Always show when renderer exists -->
        <div class="camera-controls-wrapper" v-if="renderer">
          <camera-controls
            v-if="showCameraControls"
            @setView="setCameraView"
            @resetCamera="resetCameraView"
          />
        </div>
  
        <!-- Main Content -->
        <div v-if="trial || (markerSpheres.length > 0) || (animations.length > 0) || (smplSequences.length > 0) || trialLoading || converting || conversionError || loadingMarkers || loadingSharedSession || scene || sceneInitializing" class="d-flex flex-column h-100">
          <div id="mocap" ref="mocap" class="flex-grow-1 position-relative">
            <!-- Conversion loading overlay on top of scene -->
            <div v-if="converting" class="conversion-overlay-scene">
              <div class="conversion-content">
                <v-progress-circular indeterminate color="indigo" size="64" width="6" />
                <div class="mt-4 text-h6 text-center white--text">
                  Converting OpenSim Files<br>
                  <span class="text-subtitle-1">This may take a moment...</span>
                </div>
              </div>
            </div>
            <!-- Shared session loading overlay on top of scene -->
            <div v-if="loadingSharedSession" class="conversion-overlay-scene">
              <div class="conversion-content">
                <v-progress-circular indeterminate color="indigo" size="64" width="6" />
                <div class="mt-4 text-h6 text-center white--text">
                  Loading Shared Visualization<br>
                  <span class="text-subtitle-1">This may take a moment...</span>
                </div>
              </div>
            </div>
          </div>
          <div class="controls-container" style="display: flex; align-items: center; padding: 0 10px;" v-if="$route.query.embed !== 'true'">
            <!-- Video controls on the left -->
            <VideoNavigation
              :playing="playing"
              :value="frame"
              :maxFrame="frames.length - 1"
              :disabled="videoControlsDisabled || liveMode"
              @play="togglePlay(true)"
              @pause="togglePlay(false)"
              @input="onNavigate"
              class="mr-3"
            />
            <!-- Add Loop button here -->
            <v-btn icon dark @click="toggleLooping" :disabled="videoControlsDisabled" class="mr-2">
              <v-icon :color="isLooping ? 'cyan lighten-2' : 'grey'">{{ isLooping ? 'mdi-repeat' : 'mdi-repeat-off' }}</v-icon>
            </v-btn>
            <!-- Playback speed control -->
            <div class="mr-3">
              <SpeedControl v-model="playSpeed" />
            </div>
            <!-- Time and slider on the right -->
            <div style="flex: 1; display: flex; flex-wrap: wrap; align-items: center;">
              <div style="flex: 0.1; min-width: 10px; margin-right: 5px; display: flex; align-items: center;">
                <v-text-field
                  type="number"
                  :step="0.01"
                  :value="formattedTime"
                  dark
                  style="flex: 1;"
                  @input="onChangeTime"
                  :disabled="liveMode"
                />
                <span class="ml-1 white--text">(s)</span>
              </div>
              <!-- Hide timeline slider in live mode -->
              <v-slider
                v-if="!liveMode"
                :value="frame"
                :min="0"
                :max="frames.length - 1"
                @input="onNavigate"
                hide-details
                class="mb-2"
                style="flex: 1;"
              />
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
  
          <!-- Shared session loading overlay -->
          <div v-if="loadingSharedSession" class="conversion-overlay">
            <v-progress-circular indeterminate color="indigo" size="64" width="6" />
            <div class="mt-4 text-h6 text-center">
              Loading Shared Visualization<br>
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
  
          <div class="text-center drop-zone" :class="{ 'opacity-reduced': converting }" @click="openFileBrowser">
            <!-- Welcome Documentation Section -->
            <div v-if="!converting && !conversionError" class="welcome-section pa-4 text-center" style="width: 100%; max-width: 100%; box-sizing: border-box;">
              <div class="mb-4">
                <v-icon size="40" color="primary" class="mb-2">mdi-human-handsup</v-icon>
                <h1 class="text-h5 white--text mb-1">Welcome to OpenCap Visualizer</h1>
                <p class="text-body-2 grey--text">
                  Visualize and analyze human motion capture data in 3D
                </p>
              </div>
  
              <v-row class="mb-3" dense justify="center">
                <v-col cols="12" sm="6" md="4">
                  <v-card dark class="pa-3 h-100 text-center d-flex flex-column" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="24" color="indigo" class="mb-2 mx-auto">mdi-file-document-outline</v-icon>
                    <h3 class="text-subtitle-2 mb-2">Supported File Types</h3>
                    <div class="text-center">
                      <div class="mb-1">
                        <v-chip x-small color="indigo" dark class="mr-1">JSON</v-chip>
                        <span class="text-caption">Pre-processed motion data</span>
                      </div>
                      <div class="mb-1">
                        <v-chip x-small color="orange" dark class="mr-1">OSIM + MOT</v-chip>
                        <span class="text-caption">OpenSim models & motion</span>
                      </div>
                      <div class="mb-1">
                        <v-chip x-small color="red" dark class="mr-1">Forces</v-chip>
                        <span class="text-caption">Ground reaction forces (.mot)</span>
                      </div>
                      <div class="mb-1">
                        <v-chip x-small color="purple" dark class="mr-1">TRC</v-chip>
                        <span class="text-caption">Motion capture marker files</span>
                      </div>
                      <div class="mb-1">
                        <v-chip x-small color="cyan" dark class="mr-1">MP4/WebM</v-chip>
                        <span class="text-caption">Video files for sync</span>
                      </div>
                    </div>
                  </v-card>
                </v-col>
  
                <v-col cols="12" sm="6" md="4">
                  <v-card dark class="pa-3 h-100 text-center d-flex flex-column" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="24" color="green" class="mb-2 mx-auto">mdi-play-circle-outline</v-icon>
                    <h3 class="text-subtitle-2 mb-2">Quick Start</h3>
                    <div class="text-center">
                      <ol class="text-caption" style="margin: 0; padding-left: 0; list-style-position: inside;">
                        <li class="mb-1">Click "Try with Sample Files" to explore</li>
                        <li class="mb-1">Or drag & drop multiple files at once</li>
                        <li class="mb-1">Use the Import button for specific types</li>
                        <li class="mb-1">Control playback with the timeline</li>
                        <li class="mb-1">Record videos or capture screenshots</li>
                      </ol>
                    </div>
                  </v-card>
                </v-col>
              </v-row>
              
              <!-- Sample Data Button -->
              <div class="mt-4 mb-2">
                <v-btn
                  large
                  outlined
                  color="white"
                  @click.stop="showSampleSelectionDialog = true"
                  class="px-6"
                >
                  <v-icon left>mdi-play-circle</v-icon>
                  Try with Sample Files
                </v-btn>
              </div>
            </div>
  
            <div class="text-center">
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
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Toggle button for sidebar -->
      <v-btn
        icon
        dark
        class="sidebar-toggle"
        :class="{ 'sidebar-open': showSidebar }"
        @click="showSidebar = !showSidebar"
        v-if="$route.query.embed !== 'true'"
      >
        <v-icon>{{ showSidebar ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
      </v-btn>

      <!-- GitHub Repository Link -->
      <v-tooltip right>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            icon
            class="github-link-btn"
            @click.stop="openGitHubRepo"
            v-bind="attrs"
            v-on="on"
            v-if="$route.query.embed !== 'true'"
          >
            <v-icon>mdi-help-circle</v-icon>
          </v-btn>
        </template>
        <span>View on GitHub</span>
      </v-tooltip>

      <!-- GitHub Info Dialog -->
      <GithubInfoDialog
        v-model="showGitHubDialog"
        @open-github-repo="openGitHubRepository"
        @open-github-issues="openGitHubIssues"
      />

      <!-- Right Panel: Controls, Legend, etc. -->
      <div class="right d-flex flex-column" :class="{ 'hidden': !showSidebar }" v-if="$route.query.embed !== 'true'">
        <!-- Recording controls -->
        <div class="recording-controls mb-4">
          <!-- Video Recording Section -->
        <div class="recording-section mb-6 pa-3" style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
            <div class="section-title mb-3" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">Video Recording</div>
          <!-- Record button row with settings button -->
            <div class="d-flex align-center mb-3">
              <v-btn v-if="!isRecording" color="#EF4444" dark @click="startRecording" :disabled="isRecording" class="custom-btn" style="flex: 1;">
                <v-icon left>mdi-record</v-icon>
                Record
              </v-btn>
            <v-btn v-else color="#E53E3E" dark @click="stopRecording" class="custom-btn pulse-recording" style="flex: 1;">
                <v-icon left>mdi-stop</v-icon>
              <span class="font-weight-bold">RECORDING</span>
                <span v-if="loopCount !== Infinity" class="caption ml-1">({{ currentLoop }}/{{ loopCount }})</span>
              </v-btn>
  
            <v-btn
              small
              outlined
              color="white"
              class="ml-2 settings-text-btn"
              @click="openRecordingSettings($event)"
              :disabled="isRecording"
            >
              Settings
            </v-btn>
            </div>
  
          <!-- Recording settings summary -->
          <div class="d-flex align-center recording-summary">
            <div class="text-caption text-center" style="flex: 1;">
              <span class="font-weight-bold">Format:</span> {{ recordingFormat === 'webm' ? 'WebM' : 'MP4' }}
            </div>
            <div class="text-caption text-center" style="flex: 1;">
              <span class="font-weight-bold">Bitrate:</span> {{ (videoBitrate / 1000000).toFixed(0) }} Mbps
            </div>
            <div class="text-caption text-center" style="flex: 1;">
              <span class="font-weight-bold">Loops:</span> {{ loopCount === Infinity ? '∞' : loopCount }}
            </div>
          </div>
  
          <!-- Recording settings dialog -->
          <v-dialog
            v-model="showRecordingSettings"
            max-width="500"
          >
            <v-card class="recording-settings-dialog">
              <v-card-title>Recording Settings</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12">
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
                      label="Number of Loops"
                      outlined
                dense
                dark
                      hide-details="auto"
                      class="mb-4"
              ></v-select>
                  </v-col>
  
                  <v-col cols="12">
              <v-select
                v-model="recordingFormat"
                      :items="[
                        {text: 'WebM (Recommended)', value: 'webm'},
                        {text: 'MP4 (May be limited)', value: 'mp4'}
                      ]"
                      label="Video Format"
                      outlined
                dense
                dark
                      hide-details="auto"
                      class="mb-4"
              ></v-select>
                  </v-col>
  
                  <v-col cols="12">
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
                      label="Video Bitrate"
                      outlined
                dense
                dark
                      hide-details="auto"
                      class="mb-4"
              ></v-select>
                  </v-col>
  
                  <v-col cols="12">
                    <div class="info-box pa-3 mt-2">
                      <div class="d-flex align-center mb-2">
                        <v-icon small color="info" class="mr-2">mdi-information-outline</v-icon>
                        <span class="subtitle-2">Recording Tips</span>
                      </div>
                      <ul class="pl-4 mb-0 text-caption">
                        <li class="mb-1">Maximize your browser window for best quality</li>
                        <li class="mb-1">Use WebM format for better compatibility</li>
                        <li>Higher bitrates produce larger files but better quality</li>
                  </ul>
                </div>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" text @click="showRecordingSettings = false">Close</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          </div>
  
          <!-- Image Capture Section -->
        <div class="capture-section pa-3" style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
            <div class="section-title mb-3" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">Image Capture</div>
          <!-- Capture button row with settings button -->
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
  
            <v-btn
              small
              outlined
              color="white"
              class="ml-2 settings-text-btn"
              @click="openCaptureSettings($event)"
            >
              Settings
            </v-btn>
            </div>
  
          <!-- Capture settings summary -->
          <div class="d-flex align-center recording-summary">
            <div class="text-caption text-center" style="flex: 1;">
              <span class="font-weight-bold">Background:</span>
              {{ captureMode === 'both' ? 'Both Types' :
                 captureMode === 'normal' ? 'Normal' : 'Transparent' }}
            </div>
          </div>
  
          <!-- Image capture settings dialog -->
          <v-dialog
            v-model="showCaptureSettings"
            max-width="500"
          >
            <v-card class="recording-settings-dialog">
              <v-card-title>Image Capture Settings</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12">
              <v-select
                v-model="captureMode"
                :items="[
                  {text: 'Both Types', value: 'both'},
                  {text: 'Normal', value: 'normal'},
                  {text: 'Transparent', value: 'transparent'}
                ]"
                      label="Background Type"
                      outlined
                dense
                dark
                      hide-details="auto"
                      class="mb-4"
              ></v-select>
                  </v-col>
  
                  <v-col cols="12">
                    <div class="info-box pa-3 mt-2">
                      <div class="d-flex align-center mb-2">
                        <v-icon small color="info" class="mr-2">mdi-information-outline</v-icon>
                        <span class="subtitle-2">Capture Tips</span>
            </div>
                      <ul class="pl-4 mb-0 text-caption">
                        <li class="mb-1"><b>Both Types:</b> Saves both normal and transparent versions</li>
                        <li class="mb-1"><b>Normal:</b> Standard PNG with background</li>
                        <li><b>Transparent:</b> PNG with transparent background (useful for overlays)</li>
                      </ul>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" text @click="showCaptureSettings = false">Close</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          </div>
        </div>
  
        <!-- File controls -->
        <div class="file-controls mb-4 position-relative">
          <!-- Make controls slightly transparent when loading -->
          <div :class="{ 'opacity-reduced': converting }">
            <!-- Add Share Button Here -->
            <v-btn color="#2563EB" class="mb-4 white--text custom-btn" block @click="openShareDialog" :disabled="!trial || (animations.length === 0 && smplSequences.length === 0)">
              <v-icon left>mdi-share-variant</v-icon>
              Share Visualization
            </v-btn>
  
            <v-btn color="#4B5563" class="mb-4 white--text custom-btn" block @click="showPlottingDialog = true" :disabled="!trial && animations.length === 0 && smplSequences.length === 0">
              <v-icon left>mdi-chart-line</v-icon>
              Real-time Plots
            </v-btn>
  
            <!-- Keep all the file inputs but hide them -->
            <input type="file" ref="fileInput" accept=".json" style="display: none" @change="handleFileUpload" multiple />
  
            <input type="file" ref="osimMotFileInput" accept=".osim,.mot" style="display: none" @change="handleOpenSimFiles" multiple />
            <input type="file" ref="videoFileInput" accept="video/mp4,video/webm" style="display: none" @change="handleVideoUpload" />
            <input
              type="file"
              ref="objFileInput"
              accept=".obj,.gltf,.glb,.fbx,.stl,.dae"
              style="display: none"
              @change="handleModelFileSelect"
            />
            <input
              type="file"
              ref="forcesFileInput"
              accept=".mot"
              style="display: none"
              @change="handleForcesFileSelectFromImport"
            />
            <input
              type="file"
              ref="markersFileInput"
              accept=".trc"
              style="display: none"
              @change="handleMarkersFileSelectFromImport"
            />
          </div>
        </div>
  
  
        <!-- Add Import Dialog -->
        <ImportDialog
          v-model="showImportDialog"
          @select-file-type="selectFileType"
          @open-forces-dialog="openForcesDialogFromImport"
          @open-markers-dialog="openMarkersDialogFromImport"
        />
  
        <!-- Add Forces Dialog -->
        <v-dialog v-model="showForcesDialog" max-width="500" content-class="forces-dialog">
          <v-card class="forces-dialog-card">
            <v-card-title class="headline">Import Ground Reaction Forces</v-card-title>
            <v-card-text>
              <div class="text-body-1 mb-4">
                Select a .mot forces file to visualize ground reaction forces at the subject's feet.
                Forces will be automatically positioned at the foot segments of the selected animation.
                <br><br>
                <strong>Supported formats:</strong>
                <ul class="mt-2">
                  <li>• Standard OpenSim format: <code>R_ground_force_vx</code>, <code>L_ground_force_vx</code></li>
                  <li>• Alternative format: <code>ground_force_right_vx</code>, <code>ground_force_left_vx</code></li>
                  <li>• Files with "force" in the filename are automatically detected</li>
                </ul>
              </div>
  
              <v-alert v-if="animations.length === 0 && smplSequences.length === 0" type="warning" text dense class="mb-4">
                Please load an animation first before importing forces.
              </v-alert>
  
              <v-alert v-if="forcesDatasets[selectedAnimationForForces]" type="warning" text dense class="mb-4">
                This animation already has forces loaded. Loading new forces will replace the existing ones.
              </v-alert>
  
              <v-alert v-if="Object.keys(forcesDatasets).length > 0" type="info" text dense class="mb-4">
                Currently loaded forces for: {{ Object.keys(forcesDatasets).map(idx => animations[idx]?.trialName || `Subject ${parseInt(idx) + 1}`).join(', ') }}
              </v-alert>
  
              <div v-if="animations.length > 0" class="mb-4">
                <v-select
                  v-model="selectedAnimationForForces"
                  :items="animationOptions"
                  item-text="text"
                  item-value="value"
                  label="Associate with Animation"
                  outlined
                  dense
                ></v-select>
              </div>
  
              <v-file-input
                v-model="forcesFile"
                label="Forces File (.mot)"
                accept=".mot"
                prepend-icon="mdi-vector-line"
                outlined
                show-size
                clearable
                :disabled="animations.length === 0"
                @change="handleForcesFileSelect"
              ></v-file-input>
  
              <div v-if="forcesFile" class="mt-4">
                <div class="text-subtitle-2 mb-2">Force Visualization Settings</div>
  
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="forceScale"
                      label="Force Scale"
                      type="number"
                      step="0.001"
                      min="0.001"
                      max="0.01"
                      dense
                      outlined
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6">
                    <div class="text-subtitle-2 mb-2">Arrow Color</div>
                    <v-menu offset-y :close-on-content-click="false">
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: getForceColor(selectedAnimationForForces || 0) }" block outlined>
                          <v-icon left>mdi-palette</v-icon>
                          Color
                        </v-btn>
                      </template>
                      <v-card class="color-picker pa-2">
                        <div class="d-flex align-center">
                          <v-color-picker
                            :value="getForceDisplayColor(selectedAnimationForForces || 0)"
                            :modes="['hex', 'rgba']"
                            show-swatches
                            :swatches="Array.isArray(availableColors) ? availableColors : []"
                            @input="(color) => updateForceColor(color, selectedAnimationForForces || 0)"
                            class="flex-grow-1"
                          ></v-color-picker>
                          <v-btn icon small @click="openEyeDropper('force', selectedAnimationForForces || 0)" title="Pick color from screen" class="ml-2">
                            <v-icon>mdi-eyedropper-variant</v-icon>
                          </v-btn>
                        </div>
                      </v-card>
                    </v-menu>
                  </v-col>
                </v-row>
  
                <v-switch
                  v-model="showForces"
                  label="Show Forces"
                  color="success"
                ></v-switch>
              </div>
            </v-card-text>
  
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey darken-1" text @click="closeForcesDialog">
                Cancel
              </v-btn>
              <v-btn
                color="success"
                text
                @click="loadForcesFile"
                :disabled="!forcesFile || loadingForces"
                :loading="loadingForces"
              >
                Load Forces
              </v-btn>
            </v-card-actions>
                      </v-card>
        </v-dialog>
  
        <!-- Add Markers Dialog -->
        <v-dialog v-model="showMarkersDialog" max-width="500" content-class="markers-dialog">
          <v-card class="markers-dialog-card">
            <v-card-title class="headline">Import Motion Capture Markers</v-card-title>
            <v-card-text>
              <div class="text-body-1 mb-4">
                Select a .trc file to visualize motion capture markers as spheres in the 3D scene.
                Markers will be positioned according to the data in the file.
              </div>
  
              <v-alert v-if="animations.length === 0 && smplSequences.length === 0" type="info" text dense class="mb-4">
                No animations loaded. A standalone marker visualization will be created.
              </v-alert>
  
              <v-alert v-if="animations.length > 0 && markersDatasets[selectedAnimationForMarkers]" type="warning" text dense class="mb-4">
                This animation already has markers loaded. Loading new markers will replace the existing ones.
              </v-alert>
  
              <v-alert v-if="Object.keys(markersDatasets).length > 0 && animations.length > 0" type="info" text dense class="mb-4">
                Currently loaded markers for: {{ Object.keys(markersDatasets).map(idx => animations[idx]?.trialName || `Subject ${parseInt(idx) + 1}`).join(', ') }}
              </v-alert>
  
              <div v-if="animations.length > 0" class="mb-4">
                <v-select
                  v-model="selectedAnimationForMarkers"
                  :items="animationOptions"
                  item-text="text"
                  item-value="value"
                  label="Associate with Animation"
                  outlined
                  dense
                ></v-select>
              </div>
  
              <v-file-input
                v-model="markersFile"
                label="Markers File (.trc)"
                accept=".trc"
                prepend-icon="mdi-record-circle-outline"
                outlined
                show-size
                clearable
                @change="handleMarkersFileSelect"
              ></v-file-input>
  
              <div v-if="markersFile" class="mt-4">
                <div class="text-subtitle-2 mb-2">Marker Visualization Settings</div>
  
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="markerSize"
                      label="Marker Size"
                      type="number"
                      step="1"
                      min="1"
                      max="20"
                      dense
                      outlined
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6">
                    <div class="text-subtitle-2 mb-2">Marker Color</div>
                    <v-menu offset-y :close-on-content-click="false">
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: getMarkerColor(selectedAnimationForMarkers || 0) }" block outlined>
                          <v-icon left>mdi-palette</v-icon>
                          Color
                        </v-btn>
                      </template>
                      <v-card class="color-picker pa-2">
                        <div class="d-flex align-center">
                          <v-color-picker
                            :value="getMarkerDisplayColor(selectedAnimationForMarkers || 0)"
                            :modes="['hex', 'rgba']"
                            show-swatches
                            :swatches="Array.isArray(availableColors) ? availableColors : []"
                            @input="(color) => updateMarkerColor(color, selectedAnimationForMarkers || 0)"
                            class="flex-grow-1"
                          ></v-color-picker>
                          <v-btn icon small @click="openEyeDropper('marker', selectedAnimationForMarkers || 0)" title="Pick color from screen" class="ml-2">
                            <v-icon>mdi-eyedropper-variant</v-icon>
                          </v-btn>
                        </div>
                      </v-card>
                    </v-menu>
                  </v-col>
                </v-row>
  
                <v-switch
                  v-model="showMarkers"
                  label="Show Markers"
                  color="success"
                ></v-switch>
              </div>
            </v-card-text>
  
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey darken-1" text @click="closeMarkersDialog">
                Cancel
              </v-btn>
              <v-btn
                color="success"
                text
                @click="loadMarkersFile"
                :disabled="!markersFile || loadingMarkers"
                :loading="loadingMarkers"
              >
                Load Markers
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
  
        <!-- Sample Selection Dialog -->
        <SampleSelectionDialog
          v-model="showSampleSelectionDialog"
          :available-sample-sets="availableSampleSets"
          @select-sample="selectSampleSet"
        />
  
        <!-- Share Dialog -->
        <ShareDialog
          v-model="showShareDialog"
          :share-url="shareUrl"
          :share-file-name.sync="shareFileName"
          :share-settings.sync="shareSettings"
          :loading-initial-share="loadingInitialShare"
          :generating-share-url="generatingShareUrl"
          @copy-to-clipboard="copyToClipboard"
          @open-in-new-tab="openInNewTab"
          @download-share-file="downloadShareFile"
          @generate-share-url="generateShareUrl"
        />
  
        <!-- Real-time Plotting Dialog -->
        <v-dialog
          v-model="showPlottingDialog"
          max-width="1200"
          persistent
          content-class="plotting-dialog"
          :overlay="false"
        >
          <v-card
            class="plotting-dialog-card"
            :style="{
              position: 'fixed',
              top: plottingDialogPosition.y + 'px',
              left: plottingDialogPosition.x + 'px',
              width: plottingDialogSize.width + 'px',
              height: plottingDialogSize.height + 'px',
              maxWidth: 'none',
              maxHeight: 'none',
              zIndex: 1000,
              resize: 'both',
              overflow: 'hidden'
            }"
          >
            <!-- Header with drag handle -->
            <v-card-title
              class="plotting-header d-flex align-center pa-3"
              style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); cursor: move; user-select: none;"
              @mousedown="startDragPlotDialog"
              @touchstart="startDragPlotDialog"
            >
              <v-icon color="white" class="mr-3">mdi-chart-line</v-icon>
              <span class="white--text font-weight-bold text-h6">Real-time Data Plots</span>
              <v-spacer></v-spacer>
  
              <!-- Plot Controls -->
              <v-btn icon small @click="togglePlotUpdates" class="mr-2">
                <v-icon color="white">{{ plotUpdatesEnabled ? 'mdi-pause' : 'mdi-play' }}</v-icon>
              </v-btn>
  
              <v-btn icon small @click="exportPlot" class="mr-2">
                <v-icon color="white">mdi-download</v-icon>
              </v-btn>
  
              <v-btn icon small @click="showPlottingDialog = false">
                <v-icon color="white">mdi-close</v-icon>
              </v-btn>
            </v-card-title>
  
            <!-- Plot Content -->
            <v-card-text class="pa-0" style="height: calc(100% - 64px); overflow: hidden;">
              <div class="d-flex" style="height: 100%;">
                <!-- Left Panel - Plot Controls -->
                <div class="plot-controls-panel pa-3" style="width: 280px; background: rgba(0, 0, 0, 0.05); border-right: 1px solid rgba(0, 0, 0, 0.1); overflow-y: auto;">
                  <div class="text-subtitle-2 mb-3 font-weight-bold">Plot Configuration</div>
  
                  <!-- Plot Type Selection -->
                  <div class="mb-4">
                    <div class="text-caption font-weight-bold mb-2">Plot Type:</div>
                    <v-select
                      v-model="selectedPlotType"
                      :items="plotTypes"
                      item-text="label"
                      item-value="value"
                      outlined
                      dense
                      @change="updatePlotType"
                    ></v-select>
                  </div>
  
                  <!-- Variable Selection -->
                  <div class="mb-4" v-if="availableVariables.length > 0">
                    <div class="text-caption font-weight-bold mb-2">Variables:</div>
                    <v-select
                      v-model="selectedVariables"
                      :items="availableVariables"
                      item-text="label"
                      item-value="value"
                      outlined
                      dense
                      multiple
                      chips
                      small-chips
                      @change="updateSelectedVariables"
                    ></v-select>
                  </div>
  
                  <!-- Marker Selection for marker-related plots -->
                  <div class="mb-4" v-if="selectedPlotType === 'marker_position' || selectedPlotType === 'marker_distance'">
                    <div class="text-caption font-weight-bold mb-2">Markers:</div>
                    <v-select
                      v-model="selectedMarkers"
                      :items="availableMarkers"
                      item-text="label"
                      item-value="value"
                      outlined
                      dense
                      multiple
                      chips
                      small-chips
                      @change="updateSelectedMarkers"
                    ></v-select>
                  </div>
  
                  <!-- Animation Selection -->
                  <div class="mb-4" v-if="animations.length > 1">
                    <div class="text-caption font-weight-bold mb-2">Animation:</div>
                    <v-select
                      v-model="selectedPlotAnimation"
                      :items="animationOptions"
                      item-text="text"
                      item-value="value"
                      outlined
                      dense
                      @change="updatePlotAnimation"
                    ></v-select>
                  </div>
  
                  <!-- Plot Appearance -->
                  <div class="mb-4">
                    <div class="text-caption font-weight-bold mb-2">Appearance:</div>
                    <v-checkbox
                      v-model="plotSettings.showGrid"
                      label="Show Grid"
                      dense
                      hide-details
                      class="mb-1"
                    ></v-checkbox>
                    <v-checkbox
                      v-model="plotSettings.showLegend"
                      label="Show Legend"
                      dense
                      hide-details
                      class="mb-1"
                    ></v-checkbox>
                    <v-checkbox
                      v-model="plotSettings.showCurrentTime"
                      label="Show Current Time"
                      dense
                      hide-details
                    ></v-checkbox>
                  </div>
  
                  <!-- Time Range -->
                  <div class="mb-4">
                    <div class="text-caption font-weight-bold mb-2">Time Range (s):</div>
                    <v-range-slider
                      v-model="plotTimeRange"
                      :min="0"
                      :max="maxTime"
                      :step="0.1"
                      dense
                      hide-details
                      class="mb-2"
                    ></v-range-slider>
                    <div class="text-caption text-center">
                      {{ plotTimeRange[0].toFixed(1) }}s - {{ plotTimeRange[1].toFixed(1) }}s
                    </div>
                  </div>
                </div>
  
                <!-- Right Panel - Plot Display -->
                <div class="plot-display-panel" style="flex: 1; position: relative;">
                  <div v-if="!selectedPlotType || selectedVariables.length === 0" class="d-flex align-center justify-center" style="height: 100%;">
                    <div class="text-center text--disabled">
                      <v-icon size="64" color="grey">mdi-chart-line</v-icon>
                      <div class="text-h6 mt-2">Select plot type and variables to begin</div>
                    </div>
                  </div>
  
                  <!-- Chart Container -->
                  <div v-else style="width: 100%; height: 100%; position: relative;">
                    <canvas id="plotChart" ref="plotChart" style="width: 100%; height: 100%;"></canvas>
                  </div>
                </div>
              </div>
            </v-card-text>
  
            <!-- Resize Handle -->
            <div
              class="resize-handle"
              style="position: absolute; bottom: 0; right: 0; width: 20px; height: 20px; cursor: nw-resize; background: linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.3) 50%);"
              @mousedown="startResizePlotDialog"
              @touchstart="startResizePlotDialog"
            ></div>
          </v-card>
        </v-dialog>
  
        <!-- Scene Controls Card -->
        <SceneControls
          :background-color.sync="backgroundColor"
          :background-colors="backgroundColors"
          :ground-color.sync="groundColor"
          :ground-colors="groundColors"
          :show-ground="showGround"
          :ground-opacity="groundOpacity"
          :ground-position-y.sync="groundPositionY"
          :use-ground-texture="useGroundTexture"
          :use-checkerboard="useCheckerboard"
          :show-axes="showAxes"
          :show-camera-controls="showCameraControls"
          :enable-lights="enableLights"
          @toggle-ground-visibility="toggleGroundVisibility"
          @toggle-ground-texture="toggleGroundTexture"
          @toggle-checkerboard="toggleCheckerboard"
          @update-ground-opacity="updateGroundOpacity"
          @update-ground-position="updateGroundPosition"
          @toggle-axes="toggleAxes"
          @toggle-camera-controls="toggleCameraControls"
          @toggle-lights="toggleLights"
          @open-eyedropper="openEyeDropper"
        />
  
      <div class="mt-6"></div> <!-- Added vertical spacing -->
  
        <!-- Timelapse Controls -->
        <TimelapseControls
          :timelapse-mode.sync="timelapseMode"
          :timelapse-interval.sync="timelapseInterval"
          :timelapse-opacity.sync="timelapseOpacity"
          :timelapse-groups="timelapseGroups"
          :animations="animations"
          :get-mesh-id-for-frame="getMeshIdForFrame"
          @toggle-timelapse-mode="toggleTimelapseMode"
          @update-timelapse="updateTimelapse"
          @update-timelapse-opacity="updateTimelapseOpacity"
          @clear-timelapse="clearTimelapse"
          @delete-timelapse-group="deleteTimelapseGroup"
          @delete-timelapse-frame="(animIndex, frame) => deleteTimelapseFrame(animIndex, frame)"
        />
  
        <!-- Credits -->
        <div class="credits mt-auto pt-2 text-center">
          <div class="text-caption grey--text text--lighten-1">
            Developed by <a href="https://www.linkedin.com/in/selim-gilon/" target="_blank" class="text-decoration-none">Selim Gilon</a><br>
            Based on OpenCap<br>
            <span class="text-caption grey--text text--darken-1">© 2025 PhD Research</span>
                </div>
              </div>
  
        <!-- Load Object Dialog -->
        <v-dialog v-model="showLoadObjectDialog" max-width="500">
          <v-card>
            <v-card-title>Load 3D Object</v-card-title>
            <v-card-text>
              <v-file-input
                v-model="objFile"
                label="Select OBJ file"
                accept=".obj"
                prepend-icon="mdi-cube-outline"
                outlined
                dense
                show-size
              ></v-file-input>
  
              <div class="mt-4">
                <div class="text-subtitle-1 mb-2">Position</div>
                <div class="d-flex">
                  <v-text-field
                    v-model="objPosition.x"
                    label="X"
                    type="number"
                    step="0.1"
                    class="mr-2"
                    dense
                  ></v-text-field>
                  <v-text-field
                    v-model="objPosition.y"
                    label="Y"
                    type="number"
                    step="0.1"
                    class="mr-2"
                    dense
                  ></v-text-field>
                  <v-text-field
                    v-model="objPosition.z"
                    label="Z"
                    type="number"
                    step="0.1"
                    dense
                  ></v-text-field>
                    </div>
                      </div>
  
              <div class="mt-4">
                <div class="text-subtitle-1 mb-2">Scale</div>
                      <v-slider
                  v-model="objScale"
                  label="Scale"
                  min="0.1"
                  max="5"
                  step="0.1"
                  thumb-label
                      ></v-slider>
                      </div>
  
              <div class="mt-4">
                <div class="text-subtitle-1 mb-2">Color</div>
                <div class="d-flex flex-wrap">
                <v-btn
                    v-for="color in availableColors.filter(c => c !== 'original')"
                    :key="color"
                  small
                    icon
                    class="ma-1"
                    @click="objColor = color"
                  >
                    <div
                      class="color-sample"
                      :style="{
                        backgroundColor: color,
                        border: objColor === color ? '2px solid white' : 'none'
                      }"
                    ></div>
                </v-btn>
                    </div>
                  </div>
                </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text @click="showLoadObjectDialog = false">Cancel</v-btn>
              <v-btn color="indigo" text @click="loadCustomObject">Load</v-btn>
            </v-card-actions>
              </v-card>
            </v-dialog>
  
        <!-- Custom Objects Manager Dialog -->
        <v-dialog v-model="showCustomObjectsManager" max-width="500">
          <v-card>
            <v-card-title>Custom 3D Objects</v-card-title>
            <v-card-text>
              <div v-if="customObjects.length === 0" class="text-center grey--text pa-4">
                No custom objects loaded
                      </div>
              <v-list dense v-else>
                <v-list-item v-for="obj in customObjects" :key="obj.id">
                  <v-list-item-content>
                    <v-list-item-title>{{ obj.name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      Position: ({{ obj.position.x }}, {{ obj.position.y }}, {{ obj.position.z }})
                      | Scale: {{ obj.scale }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    <div class="d-flex">
                      <v-btn
                        icon
                        small
                        @click="toggleObjectVisibility(obj.id)"
                        class="mr-1"
                      >
                        <v-icon small :color="isObjectVisible(obj.id) ? 'white' : 'grey'">
                          {{ isObjectVisible(obj.id) ? 'mdi-eye' : 'mdi-eye-off' }}
                          </v-icon>
                      </v-btn>
                      <v-btn
                        icon
                          small
                        @click="removeCustomObject(obj.id)"
                        color="error"
                      >
                        <v-icon small>mdi-delete</v-icon>
                      </v-btn>
                  </div>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
                </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text @click="showCustomObjectsManager = false">Close</v-btn>
            </v-card-actions>
            </v-card>
        </v-dialog>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import * as THREE from 'three'
  import * as THREE_OC from '@/orbitControls'
  import VideoNavigation from '@/components/ui/VideoNavigation'
  import SpeedControl from '@/components/ui/SpeedControl'
  import CameraControls from '@/components/ui/CameraControls' // Added import
  // Session child components
  import {
    GithubInfoDialog,
    ImportDialog,
    SampleSelectionDialog,
    SceneControls,
    ShareDialog,
    TimelapseControls,
    VideoOverlay
  } from '@/components/pages/session'
  import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
  import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js'
  import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
  import { ColladaLoader } from 'three/examples/jsm/loaders/ColladaLoader.js'
  import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
  import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js'
  import { LineGeometry } from 'three/examples/jsm/lines/LineGeometry.js'
  import { Line2 } from 'three/examples/jsm/lines/Line2.js'
  import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
  import { apiError } from '@/util/ErrorMessage.js';
  
  // Create a new axios instance for SMPL service
  // In production, use the deployed service; in development, use the proxy
  const smplServiceUrl = process.env.NODE_ENV === 'production' 
    ? 'https://opencap-visualizer-smpl-service.onrender.com'
    : ''; // Empty string uses the proxy in development (configured in vue.config.js)
  
  const axiosInstance = axios.create({
    baseURL: smplServiceUrl
  });
  
  // Initialize loaders
  const objLoader = new OBJLoader();
  const gltfLoader = new GLTFLoader();
  const fbxLoader = new FBXLoader();
  const stlLoader = new STLLoader();
  const colladaLoader = new ColladaLoader();
  
  // Optional: Setup DRACO compression support for GLTF
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
  gltfLoader.setDRACOLoader(dracoLoader);
  
  // SMPL kinematic tree edges (child-parent pairs) for skeleton rendering
  const SMPL_SKELETON_EDGES = [
      [0, 1],
      [1, 2],
      [2, 3],
      [0, 4],
      [4, 5],
      [5, 6],
      [0, 7],
      [7, 8],
      [8, 9],
      [9, 10],
      [8, 11],
      [11, 12],
      [12, 13],
      [8, 14],
      [14, 15],
      [15, 16],
      [0, 17],
      [17, 18],
      [18, 19],
      [19, 20],
      [20, 21],
      [21, 22],
      [19, 23],
  ];
  
  export default {
      name: 'Session',
      components: {
          VideoNavigation,
          SpeedControl,
          CameraControls, // Register component
          GithubInfoDialog,
          ImportDialog,
          SampleSelectionDialog,
          SceneControls,
          ShareDialog,
          TimelapseControls,
          VideoOverlay
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
              smplSequences: [], // SMPL sequence animations
              nextSmplSequenceId: 1,
            frameRate: 60,
            lastFrameTime: 0,
            frameAccumulator: 0,
              playSpeed: 1, // Playback speed multiplier
          showRecordingSettings: false, // Controls recording settings dialog
          showCaptureSettings: false, // Controls image capture settings dialog
              animateLoopStarted: false,
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
              backgroundColor: '#FFFFFF',
              groundColor: '#cccccc',
              groundOpacity: 1.0,
              groundPositionY: 0,
              useGroundTexture: true,
              groundMesh: null,
              groundTexture: null,
              useCheckerboard: true,
              gridTexture: null,
              showGround: true,
              alphaValues: [], // Array to store alpha values for each animation
              lights: { hemisphere: null, directionals: [] }, // Store light references
              enableLights: true, // Toggle for lighting (disabled = uniform color for screenshots)
              osimFile: null,
              motFile: null,
              converting: false,
              loadingSharedSession: false,
              // apiUrl: 'http://localhost:8000/convert-opensim-to-visualizer-json',
              apiUrl: 'https://opensim-to-visualizer-api.onrender.com/convert-opensim-to-visualizer-json',
              convertedJsonDataMap: {}, // Map to store converted JSON data keyed by filename
              showRgbPicker: false,
              rgbValues: [],
              // Add new timelapse properties
              timelapseMode: false,
              timelapseInterval: 5,
              timelapseMeshes: {}, // Store timelapse meshes
              timelapseFrameCount: 0, // Track number of frames in timelapse
              timelapseOpacity: 0.3, // Default opacity for timelapse models
              showTimelapseManager: false,
            showTimelapseSettings: false, // Controls timelapse settings dialog
              timelapseGroups: {}, // Organized by animation index and frame numbers
              timelapseCounter: null, // Use sequential counter for mesh IDs
              captureMode: 'both', // Options: 'both', 'normal', 'transparent'
              videoBitrate: 5000000, // Video recording bitrate in bits per second (5 Mbps default)
              conversionError: null, // Add this line to store API error message
              sceneInitializing: false, // Flag to track scene initialization
              syncMode: 'none',
              syncReferenceFrame: 0,

              // Video preview props
              videoFile: null,
              videoUrl: null,
              videoMinimized: false,
              videoDuration: 0,
              videoFrameRate: 30, // Default estimate
              videoOverlayMode: true,
              videoOverlayOpacity: 0.65,
              videoPosition: { x: 20, y: 20 }, // Default position
              videoSize: { width: 300, height: 'auto' }, // Default size
              isDragging: false,
              isResizing: false,
              dragOffset: { x: 0, y: 0 },
              resizeStartPosition: { x: 0, y: 0 },
              resizeStartSize: { width: 0, height: 0 },
              showSidebar: false, // Add this line to control sidebar visibility
              meshDialogs: {}, // Add this line to store mesh dialog states
              recentSubjectColors: [], // Store recent colors used for subjects
              maxRecentColors: 8, // Maximum number of recent colors to store
              activeSubject: null,
              cameraIntrinsics: null,
              cameraDistortion: null,
              cameraImageSize: null,
              videoPlane: null,
              videoTexture: null,
              cameraExtrinsicsMap: {}, // Store camera extrinsics per sequence for video plane positioning
              videoPlaneExtrinsicsKey: null, // Track which extrinsics key has been applied to prevent recalculation
              videoPlaneFrameCache: null, // Cache of the most recent computed video plane frame for reuse
              videoPlaneBaseWidth: null, // Store base width derived from intrinsics to support scaling
              videoPlaneWidthLockedByUser: false, // Track if the user has overridden automatic width sizing
              suppressVideoPlaneWidthWatcher: false, // Prevent recursive watcher triggers when updating width programmatically
              videoPlaneDistanceLockedByUser: false, // Track if distance slider has been manually overridden
              suppressVideoPlaneDistanceWatcher: false, // Prevent recursive distance watcher feedback
              videoPlaneSettings: {
                visible: false,
                followCamera: true,
                width: 3,
                distance: 3,
                opacity: 0.95
              },
              videoChromaKey: {
                enabled: false,
                color: '#00ff00',
                similarity: 0.45,
                smoothness: 0.1,
                spill: 0.1
              },
  
              displayColors: [], // For v-color-picker visual representation
              showLoadObjectDialog: false, // Add this line to control the load object dialog
              objFile: null,
              objPosition: { x: 0, y: 0, z: 0 },
              objScale: 1,
              objColor: '#ffffff',
              customObjects: [], // Track loaded custom objects
              showCustomObjectsManager: false, // Dialog to manage custom objects
            showLeftSidebar: false, // Add this line to control left sidebar visibility
              showImportDialog: false, // Add this line to control the import dialog
  
              showAxes: false, // Add this line to control axes visibility
              axesGroup: null, // Add this line to store the axes group
              showCameraControls: false, // Add this line to control camera controls visibility
              animationDurationInSeconds: 0, // Duration for headless recording
              // Share functionality
              showShareDialog: false,
              shareUrl: '',
              shareId: null, // Add this to store the generated shareId
              shareUrlSize: 0,
              shareMethod: 0, // 0 for URL, 1 for file
              shareFileName: 'visualization-share',
              shareSettings: {
                  includeCamera: true,
                  includeColors: true,
                  includeSettings: true,
                  includeCurrentFrame: true
              },
              generatingShareUrl: false,
              loadingInitialShare: false,
              // Debounce timers for offset updates
              offsetUpdateTimers: {},
              rotationUpdateTimers: {},
              objectUpdateTimers: {},
              rotationDialogs: {},
              smplRotationDialogs: {},
  
              // Real-time plotting properties
              showPlottingDialog: false,
              plotChart: null,
              plotUpdatesEnabled: true,
              plottingDialogPosition: { x: 100, y: 100 },
              plottingDialogSize: { width: 1000, height: 600 },
              isDraggingPlotDialog: false,
              isResizingPlotDialog: false,
              plotDragOffset: { x: 0, y: 0 },
              plotResizeStartPosition: { x: 0, y: 0 },
              plotResizeStartSize: { width: 0, height: 0 },
              
              // GitHub dialog
              showGitHubDialog: false,
  
              // Plot configuration
              selectedPlotType: null,
              selectedVariables: [],
              selectedMarkers: [],
              selectedPlotAnimation: 0,
              plotTimeRange: [0, 10],
              plotSettings: {
                showGrid: true,
                showLegend: true,
                showCurrentTime: true
              },
  
              // Plot data
              plotData: {
                labels: [],
                datasets: []
              },
              // Live IK streaming over WebSocket
              liveMode: false,
              liveUrl: 'ws://localhost:8765',
              liveSocket: null,
              liveStatus: 'disconnected', // 'connecting' | 'connected' | 'error'
              liveAnimationIndex: null,
              showLiveStreamDetails: false, // Toggle for Live IK Stream section
              showSyncDetails: false, // Toggle for Sync section
              showAnimationsDetails: true, // Toggle for Animations section (default true since it's the main content)
              showForcesDetails: true, // Toggle for Forces section (default true)
              showVideoDetails: false, // Toggle for Video section (default false - collapsed)
              showMarkersDetails: true, // Toggle for Markers section (default true)
              showCustomObjectsDetails: true, // Toggle for Custom Objects section (default true)
              showSceneSettingsDetails: false, // Toggle for Scene Settings section
              showTimelapseDetails: false, // Toggle for Timelapse Mode section
              animationDetailsExpanded: {}, // Track expanded state for each animation item
              smplDetailsExpanded: {}, // Track expanded state for each SMPL sequence
              // Forces visualization properties
              showForcesDialog: false,
              forcesFile: null,
              forcesDatasets: {}, // Object to store multiple force datasets by animation index
              forceArrows: [], // Array to store force arrow objects
              showForces: true,
              forceScale: 0.001, // Scale factor for force arrows
              forceMinMagnitude: 50, // Minimum force magnitude threshold in Newtons
                    forceColors: {}, // Object to store colors per animation index
      forceDisplayColors: {}, // Object to store display colors for v-color-picker by animation index
              loadingForces: false,
              selectedAnimationForForces: 0,
              // Sample selection dialog
              showSampleSelectionDialog: false,
              availableSampleSets: [
                { id: 'STS', name: 'Sit-to-Stand', description: 'Sit-to-stand on chair' },
                { id: 'squat', name: 'Squats', description: 'Squat exercise movements' },
                { id: 'walk', name: 'Walking 1', description: 'Normal walking' },
                { id: 'walk_ts', name: 'Walking 2', description: 'Walking with disability' },
              ],
              // Marker visualization properties
              showMarkersDialog: false,
              markersFile: null,
              markersDatasets: {}, // Object to store multiple marker datasets by animation index
              markerSpheres: [], // Array to store marker sphere objects
              showMarkers: true,
              markerSize: 10, // Size of marker spheres
              markerColors: {}, // Object to store marker colors by animation index
              markerDisplayColors: {}, // Object to store display colors for v-color-picker by animation index
              loadingMarkers: false,
              selectedAnimationForMarkers: 0,
              selectedMarker: null, // Currently selected marker for sidebar display
              markerLabels: {}, // Store marker label sprites
              markerTimeData: null, // Store marker time data for syncing
              // Distance measurement properties
              measurementMode: false, // Whether measurement mode is active
              measurementMarkers: [], // Array to store selected markers for measurement (max 2)
              measurementLine: null, // Line object connecting the two markers
              currentDistance: 0, // Current distance between markers
              forcesVisible: {}, // Per-animation force visibility
              markersVisible: {}, // Per-animation marker visibility
          }
      },
              computed: {
        // Access video element through the VideoOverlay component
        videoPreviewElement() {
          const videoOverlay = this.$refs.videoOverlayComponent;
          return videoOverlay ? videoOverlay.getVideoPreview() : null;
        },
        // Access video projection canvas through the VideoOverlay component
        videoProjectionCanvasElement() {
          const videoOverlay = this.$refs.videoOverlayComponent;
          return videoOverlay ? videoOverlay.getVideoProjectionCanvas() : null;
        },
        videoControlsDisabled() {
          return (!this.trial && this.markerSpheres.length === 0) || this.frames.length === 0
        },
        formattedTime() {
          // Round time to 2 decimal places for display
          return parseFloat(this.time).toFixed(2);
        },
        frameRateDisplay() {
          return Number.isFinite(this.frameRate) ? this.frameRate.toFixed(2) : '—';
        },
        formattedVideoDuration() {
          if (!Number.isFinite(this.videoDuration) || this.videoDuration <= 0) {
            return '0:00';
          }
          const totalSeconds = Math.max(0, this.videoDuration);
          const minutes = Math.floor(totalSeconds / 60);
          const seconds = Math.floor(totalSeconds % 60);
          return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        },
        syncModeOptions() {
          return [
            { text: 'No Sync', value: 'none' },
            { text: 'Align by Time', value: 'time' },
            { text: 'Align by Reference Frame', value: 'frame' }
          ];
        },
        maxFrameIndex() {
          return (Array.isArray(this.frames) && this.frames.length > 0)
            ? this.frames.length - 1
            : 0;
        },
  
        animationOptions() {
          // Create options for animation selection in forces dialog
          return this.animations.map((animation, index) => {
            const hasForces = this.forcesDatasets[index];
            const baseText = animation.trialName || animation.fileName || `Animation ${index + 1}`;
            return {
              text: hasForces ? `${baseText} (Forces loaded)` : baseText,
              value: index
            };
          });
        },
  
        // Plotting computed properties
        plotTypes() {
          return [
            { label: 'Marker Positions', value: 'marker_position' },
            { label: 'Force Magnitudes', value: 'force_magnitude' },
            { label: 'Force Components', value: 'force_components' },
            { label: 'Marker Distances', value: 'marker_distance' },
            { label: 'Joint Angles', value: 'joint_angles' },
            { label: 'Pelvis Translations', value: 'pelvis_translations' }
          ];
        },
  
        availableVariables() {
          if (!this.selectedPlotType) return [];
  
          switch (this.selectedPlotType) {
            case 'marker_position':
              return [
                { label: 'X Position', value: 'x' },
                { label: 'Y Position', value: 'y' },
                { label: 'Z Position', value: 'z' }
              ];
            case 'force_magnitude':
              return [
                { label: 'Left Foot Force', value: 'left_magnitude' },
                { label: 'Right Foot Force', value: 'right_magnitude' },
                { label: 'Total Force', value: 'total_magnitude' }
              ];
            case 'force_components':
              return [
                { label: 'Left Fx', value: 'left_fx' },
                { label: 'Left Fy', value: 'left_fy' },
                { label: 'Left Fz', value: 'left_fz' },
                { label: 'Right Fx', value: 'right_fx' },
                { label: 'Right Fy', value: 'right_fy' },
                { label: 'Right Fz', value: 'right_fz' }
              ];
            case 'marker_distance':
              return [
                { label: 'Distance', value: 'distance' }
              ];
            case 'joint_angles':
              return this.getAvailableJointAngles();
            case 'pelvis_translations':
              return [
                { label: 'Pelvis TX', value: 'pelvis_tx' },
                { label: 'Pelvis TY', value: 'pelvis_ty' },
                { label: 'Pelvis TZ', value: 'pelvis_tz' }
              ];
            default:
              return [];
          }
        },
  
        availableMarkers() {
          const animation = this.animations[this.selectedPlotAnimation];
          const markersData = this.markersDatasets[this.selectedPlotAnimation];
  
          if (markersData && markersData.markers) {
            return markersData.markers.map(marker => ({
              label: marker,
              value: marker
            }));
          }
  
          return [];
        },
  
        maxTime() {
          const animation = this.animations[this.selectedPlotAnimation];
          if (animation && animation.data && animation.data.time) {
            return Math.max(...animation.data.time);
          }
          return 10;
        }
      },
    async   mounted() {
        console.log('Session component mounted');
        console.log('Current route:', this.$route.path);
        console.log('Query params:', this.$route.query);
  
        // Load settings from localStorage first
        this.loadSettings();
  
        // Initialize displayColors from THREE.Color objects
        this.initializeDisplayColors();
  
        // Expose component instance globally for headless operation
        window.sessionComponent = this;
  
        // Expose debug functions globally for manual debugging
        window.setBackgroundWhite = () => { this.backgroundColor = '#FFFFFF'; this.updateBackgroundColor(); };
        window.setBackgroundBlack = () => { this.backgroundColor = '#000000'; this.updateBackgroundColor(); };
        window.clearSettings = () => { localStorage.removeItem('opencapVisualizerSettings'); console.log('Cleared localStorage settings'); };
        window.toggleFog = () => {
          if (this.scene.fog) {
            this.scene.fog = null;
            console.log('Fog disabled');
          } else {
            this.scene.fog = new THREE.FogExp2(this.backgroundColor, 0.025);
            console.log('Fog enabled');
          }
          this.renderer.render(this.scene, this.camera);
        };
        window.alignCameraWithCapture = (behindPlane = true, distance = null) => { this.alignCameraWithCapture(behindPlane, distance); };
        console.log('🔧 Debug functions available: window.setBackgroundWhite(), window.setBackgroundBlack(), window.clearSettings(), window.toggleFog(), window.alignCameraWithCapture(behindPlane=true, distance=null)');
  
        // Add global click handler to help with UI debugging
        document.addEventListener('click', this.handleGlobalClick, true);
  
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
  
        // Initialize the scene first (after DOM is ready)
        this.sceneInitializing = true;
        this.$nextTick(() => {
        this.initScene(); // initScene will now call applyLoadedSceneSettings
        });
  
        // Check for shared visualization first
        if (this.$route.query.share || this.$route.query.shareId) {
            console.log('Found shared visualization in URL');
            this.loadingSharedSession = true;
            try {
                let shareData;
                if (this.$route.query.shareId) {
                    // Load from cloud storage using shareId
                    shareData = await this.loadShareData(this.$route.query.shareId);
                } else {
                    // Load from compressed URL data
                    shareData = this.decompressShareData(this.$route.query.share);
                }
  
                // Load shared visualization instead of default samples
                setTimeout(() => {
                    this.loadSharedVisualization(shareData);
                }, 100);
                return; // Skip normal loading
            } catch (error) {
                console.error('Failed to load shared visualization:', error);
                this.$toasted.error('Invalid or expired share URL');
                this.loadingSharedSession = false;
            }
        }
  
        // Determine if we need to load samples and which set
        let sampleSetToLoad = null;
        if (this.$route.query.sample_set && ['squat', 'walk', 'STS', 'rmasb', 'walk_ts'].includes(this.$route.query.sample_set)) {
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
            // Check for subjects filter from URL (e.g., subjects=mocap,mono)
            const subjectsFilter = this.$route.query.subjects || null;
            if (subjectsFilter) {
                console.log(`Subjects filter from URL: ${subjectsFilter}`);
            }
            // Check for video parameter from URL (e.g., video=true)
            const loadVideo = this.$route.query.video === 'true';
            if (loadVideo) {
                console.log('Video loading enabled from URL parameter');
            }
            // Add a small delay to ensure scene is fully initialized
            setTimeout(() => {
                this.loadSampleFiles(sampleSetToLoad, subjectsFilter, loadVideo);
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
      this.disposeVideoPlane();

      if (this.resizeObserver) {
        this.resizeObserver.unobserve(this.$refs.mocap)
      }
  
      // Remove global click handler
      document.removeEventListener('click', this.handleGlobalClick, true);
  
      // Clear all debounce timers
      Object.values(this.offsetUpdateTimers).forEach(timer => clearTimeout(timer));
              // Marker timer cleanup removed
      Object.values(this.objectUpdateTimers).forEach(timer => clearTimeout(timer));
  
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
  
      // Remove marker click event listener
      if (this.renderer && this.renderer.domElement && this.handleMarkerClick) {
          this.renderer.domElement.removeEventListener('click', this.handleMarkerClick);
      }
  
      // Clean up marker spheres
      this.clearMarkerSpheres();
  
      // Remove message listener
      window.removeEventListener('message', this.handleIframeMessage);
  
      // Remove keyboard event listener
      window.removeEventListener('keydown', this.handleKeyDown);
  
      // Clean up force arrows
      this.clearForceArrows();
    },
    watch: {
      activeSubject: {
        handler() {
          this.$nextTick(() => this.drawProjectedSkeleton());
        },
        deep: false
      },
      smplSequences: {
        handler(newValue) {
          if (this.activeSubject && this.activeSubject.type === 'smpl') {
            const exists = Array.isArray(newValue) && newValue.some(seq => seq.id === this.activeSubject.id);
            if (!exists) {
              if (newValue && newValue.length > 0) {
                this.setActiveSubject('smpl', newValue[newValue.length - 1].id);
              } else {
                this.activeSubject = null;
                this.clearProjectionCanvas();
              }
            }
          } else if (Array.isArray(newValue) && newValue.length > 0) {
            this.setActiveSubject('smpl', newValue[newValue.length - 1].id);
          }
        },
        deep: false
      },
      videoOverlayMode(val) {
        this.saveSettings();
        if (!this.videoFile) {
          this.clearProjectionCanvas();
          return;
        }
        if (val) {
          this.$nextTick(() => this.drawProjectedSkeleton());
        } else {
          this.clearProjectionCanvas();
        }
      },
      videoOverlayOpacity() {
        this.saveSettings();
        if (this.videoOverlayMode && this.videoFile) {
          this.drawProjectedSkeleton();
        }
      },
      videoFile(newFile) {
        if (!newFile) {
          this.clearProjectionCanvas();
          this.disposeVideoPlane();
        } else if (this.videoOverlayMode) {
          this.$nextTick(() => this.drawProjectedSkeleton());
        }
        if (newFile && this.videoPlaneSettings.visible) {
          this.$nextTick(() => this.ensureVideoPlane());
        }
      },
      syncMode() {
        this.saveSettings();
        this.$nextTick(() => this.applySyncMode());
      },
      syncReferenceFrame(newValue) {
        const clamped = Math.max(0, Math.min(this.maxFrameIndex, Math.round(newValue)));
        if (clamped !== newValue) {
          this.syncReferenceFrame = clamped;
          return;
        }
        this.saveSettings();
        if (this.syncMode === 'frame') {
          this.$nextTick(() => this.applySyncMode());
        }
      },
      frames() {
        if (this.syncMode === 'frame') {
          const max = this.maxFrameIndex;
          if (this.syncReferenceFrame > max) {
            this.syncReferenceFrame = max;
          }
        }
      },
      'videoPlaneSettings.visible'(val) {
        this.saveSettings();
        if (!val) {
          this.disposeVideoPlane();
          return;
        }
        if (this.videoFile) {
          this.$nextTick(() => this.ensureVideoPlane());
        }
      },
      'videoPlaneSettings.followCamera'() {
        this.saveSettings();
        this.updateVideoPlaneTransform();
      },
      'videoPlaneSettings.distance'(newVal, oldVal) {
        this.saveSettings();
        if (!this.suppressVideoPlaneDistanceWatcher && newVal !== oldVal) {
          this.videoPlaneDistanceLockedByUser = true;
        }
        this.updateVideoPlaneGeometry();
        this.updateVideoPlaneTransform();
      },
      'videoPlaneSettings.width'(newVal, oldVal) {
        this.saveSettings();
        if (!this.suppressVideoPlaneWidthWatcher && newVal !== oldVal) {
          this.videoPlaneWidthLockedByUser = true;
        }
        this.updateVideoPlaneGeometry();
        this.updateVideoPlaneTransform();
      },
      'videoPlaneSettings.opacity'() {
        this.saveSettings();
        this.updateVideoPlaneMaterial();
      },
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
          // Update text sprites for all animations when any property changes
          newAnimations.forEach((animation, index) => {
            this.updateTextSprite(index);
          });
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
      showMarkers: {
        handler(newVal) {
          // Update marker visibility
          this.markerSpheres.forEach(sphere => {
            sphere.visible = newVal;
          });
  
          // Re-render the scene
          if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
          }
        }
      },
      playSpeed(newSpeed) {
        // Update video playback rate to match animation speed
        if (this.videoPreviewElement && this.videoFile) {
          const videoElement = this.videoPreviewElement;
          if (videoElement && typeof videoElement.playbackRate !== 'undefined') {
            videoElement.playbackRate = newSpeed;
            console.log(`Video playback rate updated to: ${newSpeed}x`);
          }
        }
        
        // Send playback speed updates to parent window if running in an iframe
        if (window.parent && window.parent !== window) {
          try {
            window.parent.postMessage({ type: 'playSpeedChanged', speed: newSpeed }, '*');
          } catch (error) {
            console.error('Error sending playSpeed message to parent:', error);
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
          // Get subjects filter from URL if provided
          const subjectsFilter = to.query.subjects || null;
          // Get sample set from URL if provided
          const sampleSet = to.query.sample_set || 'STS';
          // Check for video parameter from URL (e.g., video=true)
          const loadVideo = to.query.video === 'true';
          // Add a small delay to ensure scene is ready
          setTimeout(() => {
            this.loadSampleFiles(sampleSet, subjectsFilter, loadVideo);
          }, 100);
        }
      },
      shareSettings: {
        async handler() {
          if (this.showShareDialog) {
            await this.generateShareUrl();
          }
        },
        deep: true
      },
      colors: {
        handler() {
          // Update display colors when THREE.js colors change
          this.displayColors = this.colors.map(color => {
            if (color && typeof color.getHexString === 'function') {
              return '#' + color.getHexString();
            } else if (typeof color === 'string') {
              return color;
            }
            return '#FFFFFF'; // Default fallback
          });
        },
        deep: true
      },
      showForces: {
        handler(newVal) {
          // Toggle force arrow visibility
          this.forceArrows.forEach(platformGroup => {
            platformGroup.visible = newVal;
          });
  
          // Re-render the scene
          if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
          }
        }
      }
    },
    methods: {
    openGitHubRepo() {
      this.showGitHubDialog = true;
    },
    openGitHubRepository() {
      window.open('https://github.com/Seeeeeyo/opencap-visualizer', '_blank');
    },
    openGitHubIssues() {
      window.open('https://github.com/Seeeeeyo/opencap-visualizer/issues', '_blank');
    },

    // Animation details toggle methods
    toggleAnimationDetails(index) {
      this.$set(this.animationDetailsExpanded, index, !this.getAnimationDetailsExpanded(index));
    },
    getAnimationDetailsExpanded(index) {
      return this.animationDetailsExpanded[index] !== false; // Default to true (expanded)
    },
    // SMPL details toggle methods
    toggleSmplDetails(id) {
      this.$set(this.smplDetailsExpanded, id, !this.getSmplDetailsExpanded(id));
    },
    getSmplDetailsExpanded(id) {
      return this.smplDetailsExpanded[id] !== false; // Default to true (expanded)
    },

    // Forces visualization methods
    openForcesDialog() {
      this.showForcesDialog = true;
    },
  
  
    // Get current force values for display in the sidebar
    getCurrentForceValues(animationIndex) {
      if (!this.forcesDatasets[animationIndex]) {
        return null;
      }
  
      const forcesData = this.forcesDatasets[animationIndex];
      
      // Handle standalone forces (no animation frames)
      let currentTime;
      if (!this.frames || this.frames.length === 0) {
        // For standalone forces, use the force data's own time array
        if (!forcesData.time || forcesData.time.length === 0) {
          return null;
        }
        // Use the first time value for standalone forces, or create a simple time progression
        const timeIndex = Math.min(this.frame || 0, forcesData.time.length - 1);
        currentTime = forcesData.time[timeIndex];
      } else {
        // For forces associated with animations, use the animation's time
        if (this.frame >= this.frames.length) {
          return null;
        }
        currentTime = parseFloat(this.frames[this.frame]);
      }
  
      // Find the closest time index in the forces data
      let closestIndex = 0;
      let minTimeDiff = Math.abs(forcesData.time[0] - currentTime);
  
      for (let i = 1; i < forcesData.time.length; i++) {
        const timeDiff = Math.abs(forcesData.time[i] - currentTime);
        if (timeDiff < minTimeDiff) {
          minTimeDiff = timeDiff;
          closestIndex = i;
        }
      }
  
      // Debug logging for time synchronization (commented out to reduce console spam)
      // if (this.frame === 0 || this.frame % 30 === 0) {
      //   console.log('Force time sync debug:', {
      //     currentTime,
      //     forceTimeRange: [forcesData.time[0], forcesData.time[forcesData.time.length - 1]],
      //     closestIndex,
      //     minTimeDiff,
      //     frame: this.frame
      //   });
      // }
  
      // Extract force values for the current frame
      const result = {};
  
      // Check for right foot forces (try both mapped and original column names)
      const rightForceX = forcesData.data.R_ground_force_vx || forcesData.data.ground_force_right_vx;
      const rightForceY = forcesData.data.R_ground_force_vy || forcesData.data.ground_force_right_vy;
      const rightForceZ = forcesData.data.R_ground_force_vz || forcesData.data.ground_force_right_vz;
  
      // Debug logging for force data access (commented out to reduce console spam)
      // if (this.frame === 0 || this.frame % 30 === 0) {
      //   console.log('Force data access debug:', {
      //     animationIndex,
      //     hasR_ground_force_vx: !!forcesData.data.R_ground_force_vx,
      //     hasGround_force_right_vx: !!forcesData.data.ground_force_right_vx,
      //     rightForceX: !!rightForceX,
      //     rightForceY: !!rightForceY,
      //     rightForceZ: !!rightForceZ,
      //     availableKeys: Object.keys(forcesData.data).filter(key => key.includes('force'))
      //   });
      // }
  
      if (rightForceX && rightForceY && rightForceZ) {
        const fx = rightForceX[closestIndex] || 0;
        const fy = rightForceY[closestIndex] || 0;
        const fz = rightForceZ[closestIndex] || 0;
        const magnitude = Math.sqrt(fx * fx + fy * fy + fz * fz);
  
        result.R = { fx, fy, fz, magnitude };
      }
  
      // Check for left foot forces (try both mapped and original column names)
      const leftForceX = forcesData.data.L_ground_force_vx || forcesData.data.ground_force_left_vx;
      const leftForceY = forcesData.data.L_ground_force_vy || forcesData.data.ground_force_left_vy;
      const leftForceZ = forcesData.data.L_ground_force_vz || forcesData.data.ground_force_left_vz;
  
      if (leftForceX && leftForceY && leftForceZ) {
        const fx = leftForceX[closestIndex] || 0;
        const fy = leftForceY[closestIndex] || 0;
        const fz = leftForceZ[closestIndex] || 0;
        const magnitude = Math.sqrt(fx * fx + fy * fy + fz * fz);
  
        result.L = { fx, fy, fz, magnitude };
      }
  
      // Return null if no valid force data found
      return Object.keys(result).length > 0 ? result : null;
    },
  
    openForcesDialogFromImport() {
      this.showImportDialog = false;
      // Trigger the hidden file input for forces files
      this.$refs.forcesFileInput.click();
    },
  
    handleForcesFileSelectFromImport(event) {
      const file = event.target.files[0];
      if (file) {
        this.forcesFile = file;
        // Open the forces dialog with the selected file
        this.showForcesDialog = true;
      }
      // Clear the input value so the same file can be selected again if needed
      event.target.value = '';
    },
  
    closeForcesDialog() {
      this.showForcesDialog = false;
      this.forcesFile = null;
    },
  
    handleForcesFileSelect(file) {
      this.forcesFile = file;
    },
  
    async loadForcesFile() {
      if (!this.forcesFile) return;
  
      this.loadingForces = true;
      try {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.parseForcesData(e.target.result);
          this.showForcesDialog = false;
          this.$toasted.success('Forces file loaded successfully!');
        };
        reader.readAsText(this.forcesFile);
      } catch (error) {
        console.error('Error loading forces file:', error);
        this.$toasted.error('Error loading forces file');
      } finally {
        this.loadingForces = false;
      }
    },
  
    // Helper method to categorize .mot files as motion or force files
    async categorizeMotFiles(motFiles) {
      const motionFiles = [];
      const forceFiles = [];
  
      for (const file of motFiles) {
        const isForceFile = await this.isForceMotFile(file);
        if (isForceFile) {
          forceFiles.push(file);
        } else {
          motionFiles.push(file);
        }
      }
  
      return { motionFiles, forceFiles };
    },
  
    // Check if a .mot file is a force file based on filename and content
    async isForceMotFile(file) {
      const fileName = file.name.toLowerCase();
      console.log(`Checking if ${file.name} is a force file...`);
  
      // First check: filename contains "force"
      if (fileName.includes('force')) {
        console.log(`${file.name} identified as force file by filename`);
        return true;
      }
  
      // Second check: examine column headers
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target.result;
          const lines = content.split('\n');
  
          let headerEnded = false;
          let columnHeaders = [];
  
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
  
            if (line === 'endheader') {
              headerEnded = true;
              continue;
            }
  
            if (!headerEnded) continue;
  
            if (columnHeaders.length === 0) {
              // This is the column headers line
              columnHeaders = line.split(/\s+/);
              break;
            }
          }
  
          // Check for force-related column names (expanded to include more patterns)
          const forceKeywords = [
            'force', 'ground_force', 'grf',
            'force_vx', 'force_vy', 'force_vz',
            'force_px', 'force_py', 'force_pz',
            'ground_force_right', 'ground_force_left',
            'right_ground_force', 'left_ground_force',
            'moment', 'torque', 'cop'
          ];
  
          const hasForceColumns = columnHeaders.some(header =>
            forceKeywords.some(keyword =>
              header.toLowerCase().includes(keyword)
            )
          );
  
          if (hasForceColumns) {
            console.log(`${file.name} identified as force file by column headers:`, columnHeaders);
          } else {
            console.log(`${file.name} identified as motion file - no force columns found`);
          }
  
          resolve(hasForceColumns);
        };
  
        reader.onerror = () => {
          console.log(`Could not read ${file.name}, assuming motion file`);
          resolve(false);
        };
  
        reader.readAsText(file);
      });
    },
  
    // Process a force file (automatically associate with best animation)
    async processForceFile(forceFile) {
      console.log('Processing force file:', forceFile.name);
      if (this.animations.length === 0) {
        // Handle standalone force file - this is a simplified case
        this.selectedAnimationForForces = 0; // Use a default index
        this.forcesFile = forceFile;
        // Temporarily create a dummy animation if none exist
        if (!this.animations[0]) {
          this.animations[0] = { trialName: 'Standalone Forces', offset: new THREE.Vector3(), rotation: new THREE.Euler(0, 0, 0, 'XYZ'), data: { bodies: {} } };
        }
        this.$set(this.forcesVisible, '0', true);
        return new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.parseForcesData(e.target.result);
            this.$toasted.success(`Standalone forces loaded`);
            this.$nextTick(() => {
              if (this.renderer && this.scene && this.camera) {
                this.renderer.render(this.scene, this.camera);
              }
            });
            resolve();
          };
          reader.onerror = () => {
            this.$toasted.error(`Error reading force file: ${forceFile.name}`);
            resolve();
          };
          reader.readAsText(forceFile);
        });
      }
  
      // Initialize force visibility state for this animation if not set
      if (typeof this.forcesVisible === 'undefined') {
        this.forcesVisible = {};
      }
  
      // First, try to find an animation with "mono" in the fileName that doesn't have forces
      let targetAnimationIndex = -1;
      let foundMono = false;
  
      // Search for mono animation without forces
      for (let i = 0; i < this.animations.length; i++) {
        const anim = this.animations[i];
        if (anim.fileName && anim.fileName.includes('mono') && !this.forcesDatasets[i]) {
          targetAnimationIndex = i;
          foundMono = true;
          break;
        }
      }
  
      // If no mono animation found (or all mono animations have forces), use existing logic
      if (!foundMono) {
        // Find the first animation without forces, starting from the most recently added
        targetAnimationIndex = this.animations.length - 1; // Start with newest animation
        let foundAvailable = false;
        
        // Check from newest to oldest
        for (let i = this.animations.length - 1; i >= 0; i--) {
          if (!this.forcesDatasets[i]) {
            targetAnimationIndex = i;
            foundAvailable = true;
            break;
          }
        }
        
        // If all animations have forces, use the most recent one and replace
        if (!foundAvailable) {
          targetAnimationIndex = this.animations.length - 1;
          const animationName = this.animations[targetAnimationIndex].trialName || `Animation ${targetAnimationIndex + 1}`;
          this.$toasted.info(`Replacing existing forces for ${animationName}`);
        }
      }
  
      this.selectedAnimationForForces = targetAnimationIndex;
      this.forcesFile = forceFile;
  
      // Set initial visibility for this animation
      this.$set(this.forcesVisible, String(targetAnimationIndex), true);
  
      // Load the force file directly
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.parseForcesData(e.target.result);
          this.$toasted.success(`Forces loaded for ${this.animations[targetAnimationIndex].trialName || 'Animation ' + (targetAnimationIndex + 1)}`);
  
          // Ensure scene is rendered after force creation
          this.$nextTick(() => {
            if (this.renderer && this.scene && this.camera) {
              this.renderer.render(this.scene, this.camera);
            }
          });
  
          resolve();
        };
        reader.onerror = () => {
          this.$toasted.error(`Error reading force file: ${forceFile.name}`);
          resolve();
        };
        reader.readAsText(forceFile);
      });
    },
  
    parseForcesData(content) {
      const lines = content.split('\n');
      let headerEnded = false;
      let columnHeaders = [];
      const timeData = [];
      const forceData = {};
  
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
  
        if (line === 'endheader') {
          headerEnded = true;
          continue;
        }
  
        if (!headerEnded) continue;
  
        if (columnHeaders.length === 0) {
          // This is the column headers line
          columnHeaders = line.split(/\s+/);
  
          // Initialize force data arrays for each column
          columnHeaders.forEach(header => {
            if (header !== 'time') {
              forceData[header] = [];
            }
          });
          continue;
        }
  
        // Parse data lines
        if (line.length > 0) {
          const values = line.split(/\s+/).map(val => parseFloat(val));
          if (values.length === columnHeaders.length) {
            timeData.push(values[0]); // First column is time
  
            // Store force data for each column
            for (let j = 1; j < columnHeaders.length; j++) {
              forceData[columnHeaders[j]].push(values[j]);
            }
          }
        }
      }
  
      // Map column names to standard format for compatibility
      const mappedForceData = this.mapForceColumns(forceData, columnHeaders);
  
      // Store forces data for the selected animation
      const animationIndex = this.selectedAnimationForForces;
      this.forcesDatasets[animationIndex] = {
        time: timeData,
        columns: columnHeaders,
        data: mappedForceData,
        originalData: forceData, // Keep original data for reference
        associatedAnimationIndex: animationIndex,
        fileName: this.forcesFile ? this.forcesFile.name : 'Forces Data'
      };
  
      // Initialize colors for new force dataset
      if (!this.forceColors[animationIndex]) {
        this.$set(this.forceColors, animationIndex, '#00ff00'); // Default green color
        this.$set(this.forceDisplayColors, animationIndex, '#00ff00');
      }
  
      // Set initial visibility for this animation
      this.$set(this.forcesVisible, String(animationIndex), true);
  
      // For standalone forces, set up the frames array if it doesn't exist
      if (!this.frames || this.frames.length === 0) {
        this.frames = timeData;
        this.frame = 0;
        this.updateDisplayedTime(0);
        console.log('Set up frames for standalone forces:', {
          totalFrames: this.frames.length,
          timeRange: [this.frames[0], this.frames[this.frames.length - 1]]
        });
      }
  
      this.createForceArrows();
    },
  
    // New method to map different column naming conventions to standard format
    mapForceColumns(forceData, columnHeaders) {
      const mappedData = { ...forceData };
      
      // Define mapping patterns for different naming conventions
      const columnMappings = {
        // Pattern 1: R_ground_force_vx, L_ground_force_vx (current expected format)
        'R_ground_force_vx': ['R_ground_force_vx', 'ground_force_right_vx', 'right_ground_force_vx'],
        'R_ground_force_vy': ['R_ground_force_vy', 'ground_force_right_vy', 'right_ground_force_vy'],
        'R_ground_force_vz': ['R_ground_force_vz', 'ground_force_right_vz', 'right_ground_force_vz'],
        'R_ground_force_px': ['R_ground_force_px', 'ground_force_right_px', 'right_ground_force_px'],
        'R_ground_force_py': ['R_ground_force_py', 'ground_force_right_py', 'right_ground_force_py'],
        'R_ground_force_pz': ['R_ground_force_pz', 'ground_force_right_pz', 'right_ground_force_pz'],
        
        'L_ground_force_vx': ['L_ground_force_vx', 'ground_force_left_vx', 'left_ground_force_vx'],
        'L_ground_force_vy': ['L_ground_force_vy', 'ground_force_left_vy', 'left_ground_force_vy'],
        'L_ground_force_vz': ['L_ground_force_vz', 'ground_force_left_vz', 'left_ground_force_vz'],
        'L_ground_force_px': ['L_ground_force_px', 'ground_force_left_px', 'left_ground_force_px'],
        'L_ground_force_py': ['L_ground_force_py', 'ground_force_left_py', 'left_ground_force_py'],
        'L_ground_force_pz': ['L_ground_force_pz', 'ground_force_left_pz', 'left_ground_force_pz'],
      };
  
      // Apply mappings
      Object.keys(columnMappings).forEach(standardName => {
        const possibleNames = columnMappings[standardName];
        
        // Find which column name exists in the data
        for (const possibleName of possibleNames) {
          if (forceData[possibleName]) {
            mappedData[standardName] = forceData[possibleName];
            console.log(`Mapped ${possibleName} to ${standardName}`);
            break;
          }
        }
      });
  
      // Log what columns were found and mapped
      console.log('Original columns:', columnHeaders);
      console.log('Mapped force data keys:', Object.keys(mappedData).filter(key => 
        key.includes('ground_force') || key.includes('force')
      ));
      
      // Debug: Check if mapping was successful
      const hasRightForces = mappedData.R_ground_force_vx && mappedData.R_ground_force_vy && mappedData.R_ground_force_vz;
      const hasLeftForces = mappedData.L_ground_force_vx && mappedData.L_ground_force_vy && mappedData.L_ground_force_vz;
      console.log('Mapping success check:', {
        hasRightForces,
        hasLeftForces,
        rightForceData: hasRightForces ? 'Mapped successfully' : 'Not found',
        leftForceData: hasLeftForces ? 'Mapped successfully' : 'Not found'
      });
  
      return mappedData;
    },
  
    createArrowHeadGeometry() {
      // Create a traditional arrow head using CylinderGeometry
      // This creates a pointed arrow head that tapers to a point
      const arrowHead = new THREE.CylinderGeometry(
        0,        // radiusTop (pointed tip)
        0.02,     // radiusBottom (base width)
        0.1,      // height
        8,        // radialSegments
        1,        // heightSegments
        false     // openEnded
      );
  
      // Don't rotate the geometry here - keep it aligned with Y-axis like the shaft
      // The rotation will be applied to the mesh during updates
  
      return arrowHead;
    },
  
    createForceArrows() {
      if (!this.scene || this.animations.length === 0) return;
  
      this.clearForceArrows();
  
      // Create traditional arrow head geometry (shared across animations)
      const arrowGeometry = this.createArrowHeadGeometry();
  
      // Create line geometry for arrow shaft using cylinder for better appearance (shared across animations)
      const shaftGeometry = new THREE.CylinderGeometry(0.004, 0.004, 1, 8);
  
      // Map force platforms with both force vectors and center of pressure
      const forceToFootMapping = [
        {
          platform: 'R',
          footSegment: 'calcn_r',
          forceColumns: ['R_ground_force_vx', 'R_ground_force_vy', 'R_ground_force_vz'],
          copColumns: ['R_ground_force_px', 'R_ground_force_py', 'R_ground_force_pz']
        },
        {
          platform: 'L',
          footSegment: 'calcn_l',
          forceColumns: ['L_ground_force_vx', 'L_ground_force_vy', 'L_ground_force_vz'],
          copColumns: ['L_ground_force_px', 'L_ground_force_py', 'L_ground_force_pz']
        }
      ];
  
      // Create force arrows for each animation that has force data
      Object.keys(this.forcesDatasets).forEach(animationIndexStr => {
        const animationIndex = parseInt(animationIndexStr);
        const forcesData = this.forcesDatasets[animationIndex];
        const targetAnimation = this.animations[animationIndex];
  
                 if (!targetAnimation || !forcesData) {
           return;
         }
  
        // Check if the selected animation has required foot segments
        const hasRequiredSegments = forceToFootMapping.some(mapping =>
          targetAnimation.data.bodies[mapping.footSegment]
        );
  
        if (!hasRequiredSegments) {
          return;
        }
  
        forceToFootMapping.forEach(mapping => {
          if (!targetAnimation.data.bodies[mapping.footSegment]) return;
  
          // Check if force columns exist in the data (try both mapped and original column names)
          const hasForceData = mapping.forceColumns.some(col => {
            // Check mapped column name first
            if (forcesData.data[col]) return true;
            
            // If not found, try original column names as fallback
            if (col === 'R_ground_force_vx' && forcesData.data.ground_force_right_vx) return true;
            if (col === 'R_ground_force_vy' && forcesData.data.ground_force_right_vy) return true;
            if (col === 'R_ground_force_vz' && forcesData.data.ground_force_right_vz) return true;
            if (col === 'L_ground_force_vx' && forcesData.data.ground_force_left_vx) return true;
            if (col === 'L_ground_force_vy' && forcesData.data.ground_force_left_vy) return true;
            if (col === 'L_ground_force_vz' && forcesData.data.ground_force_left_vz) return true;
            
            return false;
          });
          if (!hasForceData) return;
  
          // Create force arrow group for this foot
          const footForceGroup = new THREE.Group();
          footForceGroup.name = `forces_${animationIndex}_${mapping.platform}`;
          footForceGroup.userData = {
            platform: mapping.platform,
            footSegment: mapping.footSegment,
            animationIndex: animationIndex
          };
  
          // Create single combined force arrow (resultant force vector)
          const arrowGroup = new THREE.Group();
          arrowGroup.visible = true; // Ensure initially visible
  
          // Create materials with per-animation colors
          const arrowMaterial = new THREE.MeshPhongMaterial({
            color: new THREE.Color(this.getForceColor(animationIndex)),
            transparent: true,
            opacity: 0.9
          });
  
          const shaftMaterial = new THREE.MeshPhongMaterial({
            color: new THREE.Color(this.getForceColor(animationIndex)),
            transparent: true,
            opacity: 0.9
          });
  
          // Create arrow head
          const arrowHead = new THREE.Mesh(arrowGeometry, arrowMaterial);
          arrowGroup.add(arrowHead);
  
          // Create arrow shaft (cylinder)
          const shaft = new THREE.Mesh(shaftGeometry.clone(), shaftMaterial);
          arrowGroup.add(shaft);
  
          arrowGroup.name = `force_${animationIndex}_${mapping.platform}_resultant`;
          arrowGroup.userData = {
            platform: mapping.platform,
            forceColumns: mapping.forceColumns,
            copColumns: mapping.copColumns,
            animationIndex: animationIndex
          };
  
          footForceGroup.add(arrowGroup);
          footForceGroup.visible = true; // Ensure parent group is visible
          this.scene.add(footForceGroup);
          this.forceArrows.push(footForceGroup);
        });
      });
  
      console.log(`Force arrows created for ${Object.keys(this.forcesDatasets).length} animations: ${this.forceArrows.length} foot segments`);
      console.log('Force arrows list:', this.forceArrows.map(arrow => ({
        name: arrow.name,
        userData: arrow.userData,
        visible: arrow.visible,
        children: arrow.children.length
      })));
  
      // Debug: Update for current frame immediately
      if (this.frames && this.frame < this.frames.length) {
        console.log('Updating force arrows for current frame:', this.frame);
        this.updateForceArrows(this.frame);
      }
  
      // Render the scene after creating force arrows
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
    },
  
    updateForceArrows(frameIndex) {
      if (!this.showForces || this.forceArrows.length === 0) {
        console.log('updateForceArrows skipped:', { showForces: this.showForces, forceArrowsLength: this.forceArrows.length });
        return;
      }
  
      // Handle standalone forces (no animation frames)
      let currentTime;
      if (!this.frames || this.frames.length === 0) {
        // For standalone forces, use the force data's own time array
        const forcesData = this.forcesDatasets[Object.keys(this.forcesDatasets)[0]];
        if (!forcesData || !forcesData.time || forcesData.time.length === 0) {
          return;
        }
        const timeIndex = Math.min(frameIndex, forcesData.time.length - 1);
        currentTime = forcesData.time[timeIndex];
      } else {
        // For forces associated with animations, use the animation's time
        currentTime = this.frames[frameIndex];
      }
      // Removed excessive logging - only log when debugging is needed
  
      this.forceArrows.forEach(footForceGroup => {
        const groupData = footForceGroup.userData;
        if (!groupData || typeof groupData.animationIndex === 'undefined') return;
  
        // Get the force data and animation for this specific arrow group
        const animationIndex = groupData.animationIndex;
        const forcesData = this.forcesDatasets[animationIndex];
        const animation = this.animations[animationIndex];
  
        if (!forcesData || !animation) return;
  
        // Find the closest time index in forces data for this animation
        let forceFrameIndex = 0;
        for (let i = 0; i < forcesData.time.length; i++) {
          if (Math.abs(forcesData.time[i] - currentTime) < Math.abs(forcesData.time[forceFrameIndex] - currentTime)) {
            forceFrameIndex = i;
          }
        }
  
        // Get COP position from the first child arrow (they should all have the same COP)
        const firstArrow = footForceGroup.children[0];
        if (!firstArrow || !firstArrow.userData || !firstArrow.userData.copColumns) return;
  
        const copColumns = firstArrow.userData.copColumns;
  
        // Get COP position from forces data
        let copPosition = new THREE.Vector3(0, 0, 0);
        let hasCopData = false;
  
        if (copColumns.length >= 3) {
          const copX = forcesData.data[copColumns[0]] ?
                      forcesData.data[copColumns[0]][forceFrameIndex] || 0 : 0;
          const copY = forcesData.data[copColumns[1]] ?
                      forcesData.data[copColumns[1]][forceFrameIndex] || 0 : 0;
          const copZ = forcesData.data[copColumns[2]] ?
                      forcesData.data[copColumns[2]][forceFrameIndex] || 0 : 0;
  
          // Only use COP if at least one coordinate is non-zero
          if (copX !== 0 || copY !== 0 || copZ !== 0) {
            copPosition.set(copX, copY, copZ);
            hasCopData = true;
          }
        }
  
        // Fallback to foot position if no COP data available
        if (!hasCopData && groupData.footSegment) {
          const footBody = animation.data.bodies[groupData.footSegment];
          if (footBody && footBody.translation[frameIndex]) {
            copPosition.set(
              footBody.translation[frameIndex][0],
              footBody.translation[frameIndex][1],
              footBody.translation[frameIndex][2]
            );
          }
        }
  
        // Apply animation offset
        copPosition.add(animation.offset);
        footForceGroup.position.copy(copPosition);
  
                // Debug logging for COP positioning (commented out to reduce console spam)
          // if (frameIndex === 0 || frameIndex % 30 === 0) {
          //   console.log(`COP debug - Animation ${animationIndex}:`, {
          //     copPosition: copPosition.toArray(),
          //     hasCopData,
          //     animationOffset: animation.offset
          //   });
          // }
  
        // Update each force arrow in the group
        footForceGroup.children.forEach(arrowGroup => {
          const arrowData = arrowGroup.userData;
          if (!arrowData || !arrowData.forceColumns) return;
  
          // Calculate resultant force vector
          const forceVector = new THREE.Vector3(0, 0, 0);
          const forceColumns = arrowData.forceColumns;
  
          if (forceColumns.length >= 3) {
            // Helper function to get force value with fallback to original column names
            const getForceValue = (mappedCol, originalCol) => {
              if (forcesData.data[mappedCol]) {
                return forcesData.data[mappedCol][forceFrameIndex] || 0;
              }
              if (forcesData.data[originalCol]) {
                return forcesData.data[originalCol][forceFrameIndex] || 0;
              }
              return 0;
            };
  
            const fx = getForceValue(forceColumns[0], 
              forceColumns[0] === 'R_ground_force_vx' ? 'ground_force_right_vx' : 
              forceColumns[0] === 'L_ground_force_vx' ? 'ground_force_left_vx' : null);
            const fy = getForceValue(forceColumns[1], 
              forceColumns[1] === 'R_ground_force_vy' ? 'ground_force_right_vy' : 
              forceColumns[1] === 'L_ground_force_vy' ? 'ground_force_left_vy' : null);
            const fz = getForceValue(forceColumns[2], 
              forceColumns[2] === 'R_ground_force_vz' ? 'ground_force_right_vz' : 
              forceColumns[2] === 'L_ground_force_vz' ? 'ground_force_left_vz' : null);
  
            forceVector.set(fx, fy, fz);
          }
  
          // Calculate original force magnitude before scaling
          const originalMagnitude = forceVector.length();
  
          // Debug logging (commented out to reduce console spam)
          // if (frameIndex === 0 || frameIndex % 30 === 0) { // Log every 30 frames to avoid spam
          //   const mappedFx = forcesData.data[forceColumns[0]] ? forcesData.data[forceColumns[0]][forceFrameIndex] : 'missing';
          //   const mappedFy = forcesData.data[forceColumns[1]] ? forcesData.data[forceColumns[1]][forceFrameIndex] : 'missing';
          //   const mappedFz = forcesData.data[forceColumns[2]] ? forcesData.data[forceColumns[2]][forceFrameIndex] : 'missing';
          //   
          //   // Get original column names for comparison
          //   const originalColX = forceColumns[0] === 'R_ground_force_vx' ? 'ground_force_right_vx' : 
          //                       forceColumns[0] === 'L_ground_force_vx' ? 'ground_force_left_vx' : forceColumns[0];
          //   const originalColY = forceColumns[1] === 'R_ground_force_vy' ? 'ground_force_right_vy' : 
          //                       forceColumns[1] === 'L_ground_force_vy' ? 'ground_force_left_vy' : forceColumns[1];
          //   const originalColZ = forceColumns[2] === 'R_ground_force_vz' ? 'ground_force_right_vz' : 
          //                       forceColumns[2] === 'L_ground_force_vz' ? 'ground_force_left_vz' : forceColumns[2];
          //   
          //   const originalFx = forcesData.data[originalColX] ? forcesData.data[originalColX][forceFrameIndex] : 'missing';
          //   const originalFy = forcesData.data[originalColY] ? forcesData.data[originalColY][forceFrameIndex] : 'missing';
          //   const originalFz = forcesData.data[originalColZ] ? forcesData.data[originalColZ][forceFrameIndex] : 'missing';
          //   
          //   console.log(`Force debug - Animation ${animationIndex}, Platform ${arrowData.platform}:`, {
          //     mapped: { fx: mappedFx, fy: mappedFy, fz: mappedFz },
          //     original: { fx: originalFx, fy: originalFy, fz: originalFz },
          //     final: { fx: forceVector.x, fy: forceVector.y, fz: forceVector.z },
          //     magnitude: originalMagnitude,
          //     frameIndex: forceFrameIndex
          //   });
          // }
  
          // Update arrow visibility based on original force magnitude
          arrowGroup.visible = originalMagnitude > this.forceMinMagnitude;
  
          // Arrow visibility logging (commented out to reduce console spam)
          // if (frameIndex === 0 || frameIndex % 30 === 0) {
          //   console.log(`Arrow visibility - Animation ${animationIndex}, Platform ${arrowData.platform}: visible=${arrowGroup.visible}, magnitude=${originalMagnitude}`);
          // }
  
          if (arrowGroup.visible) {
            // Scale the force vector for display
            forceVector.multiplyScalar(this.forceScale);
            const scaledLength = forceVector.length();
  
            // Update shaft (cylinder) and arrow head
            const arrowHead = arrowGroup.children[0]; // Arrow head is first child
            const shaft = arrowGroup.children[1]; // Shaft is second child
  
            if (shaft && arrowHead && scaledLength > 0) {
              const direction = forceVector.clone().normalize();
  
              // Reset transformations
              shaft.position.set(0, 0, 0);
              shaft.rotation.set(0, 0, 0);
              shaft.scale.set(1, 1, 1);
              arrowHead.position.set(0, 0, 0);
              arrowHead.rotation.set(0, 0, 0);
  
              // Position shaft center at half the force vector length
              shaft.position.copy(forceVector.clone().multiplyScalar(0.5));
  
              // Scale shaft to match force vector length
              shaft.scale.set(1, scaledLength, 1);
  
              // Create rotation matrix to align cylinder (which points up by default) with force direction
              const up = new THREE.Vector3(0, 1, 0);
              const quaternion = new THREE.Quaternion();
              quaternion.setFromUnitVectors(up, direction);
              shaft.setRotationFromQuaternion(quaternion);
  
              // Position arrow head at the tip of the force vector
              arrowHead.position.copy(forceVector);
  
              // Rotate arrow head to point in force direction
              arrowHead.setRotationFromQuaternion(quaternion);
            }
          }
        });
      });
  
    // Render the scene after updating force arrows
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  },
  
    clearForceArrows() {
      this.forceArrows.forEach(arrowGroup => {
        if (this.scene) {
          this.scene.remove(arrowGroup);
        }
  
        // Dispose of geometries and materials
        arrowGroup.traverse((child) => {
          if (child.geometry) child.geometry.dispose();
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(mat => mat.dispose());
            } else {
              child.material.dispose();
            }
          }
        });
      });
    this.forceArrows = [];
  },

  ensureProjectionCanvas() {
    const canvas = this.videoProjectionCanvasElement;
    const video = this.videoPreviewElement;
    if (!canvas || !video) {
      return null;
    }
    const width = video.clientWidth || video.videoWidth || canvas.width;
    const height = video.clientHeight || video.videoHeight || canvas.height;
    if (!width || !height) {
      return canvas;
    }
    const dpr = window.devicePixelRatio || 1;
    const displayWidth = Math.round(width);
    const displayHeight = Math.round(height);
    if (canvas.width !== displayWidth * dpr || canvas.height !== displayHeight * dpr) {
      canvas.width = displayWidth * dpr;
      canvas.height = displayHeight * dpr;
      canvas.style.width = `${displayWidth}px`;
      canvas.style.height = `${displayHeight}px`;
    }
    const ctx = canvas.getContext('2d');
    if (ctx) {
      if (typeof ctx.resetTransform === 'function') {
        ctx.resetTransform();
      } else {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
      }
    }
    return canvas;
  },
  clearProjectionCanvas() {
    const canvas = this.videoProjectionCanvasElement;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  },
  drawProjectedSkeleton() {
    if (!this.videoOverlayMode || !this.videoFile) {
      this.clearProjectionCanvas();
      return;
    }

    const canvas = this.ensureProjectionCanvas();
    if (!canvas) {
      return;
    }
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }

    const video = this.videoPreviewElement;
    const displayWidth = video ? (video.clientWidth || video.videoWidth || canvas.width) : canvas.width;
    const displayHeight = video ? (video.clientHeight || video.videoHeight || canvas.height) : canvas.height;

    const subject = this.resolveActiveSubject && this.resolveActiveSubject();
    if (!subject || subject.type !== 'smpl') {
      this.clearProjectionCanvas();
      return;
    }

    const sequence = subject.sequence;
    if (!sequence) {
      this.clearProjectionCanvas();
      return;
    }

    const projectedFrames = this.ensureSequenceProjectionCache(sequence);
    if (!projectedFrames || !Array.isArray(projectedFrames)) {
      this.clearProjectionCanvas();
      return;
    }

    const frameIndex = sequence.lastRenderedFrame >= 0
      ? sequence.lastRenderedFrame
      : Math.min(Math.max(this.frame, 0), projectedFrames.length - 1);

    const frameProjection = projectedFrames[Math.min(frameIndex, projectedFrames.length - 1)];
    if (!frameProjection) {
      this.clearProjectionCanvas();
      return;
    }

    const fallbackWidth = this.videoPreviewElement?.videoWidth || displayWidth;
    const fallbackHeight = this.videoPreviewElement?.videoHeight || displayHeight;
    const imageSize = Array.isArray(sequence.projectedImageSize)
      ? this.normalizeImageSize(sequence.projectedImageSize)
      : (this.cameraImageSize || null);
    const imageWidth = imageSize && Number.isFinite(Number(imageSize.width)) && Number(imageSize.width) > 0
      ? Number(imageSize.width)
      : fallbackWidth;
    const imageHeight = imageSize && Number.isFinite(Number(imageSize.height)) && Number(imageSize.height) > 0
      ? Number(imageSize.height)
      : fallbackHeight;
    const scaleX = imageWidth ? displayWidth / imageWidth : 1;
    const scaleY = imageHeight ? displayHeight / imageHeight : 1;

    const dpr = window.devicePixelRatio || 1;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    ctx.lineWidth = 2;
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.85)';
    ctx.beginPath();
    const edges = sequence.skeletonEdges || [];
    edges.forEach(([parent, child]) => {
      const pIndex = parent * 2;
      const cIndex = child * 2;
      const pu = frameProjection[pIndex];
      const pv = frameProjection[pIndex + 1];
      const cu = frameProjection[cIndex];
      const cv = frameProjection[cIndex + 1];
      if (!Number.isFinite(pu) || !Number.isFinite(pv) || !Number.isFinite(cu) || !Number.isFinite(cv)) {
        return;
      }
      ctx.moveTo(pu * scaleX, pv * scaleY);
      ctx.lineTo(cu * scaleX, cv * scaleY);
    });
    ctx.stroke();

    ctx.fillStyle = 'rgba(0, 255, 255, 0.95)';
    const jointCount = sequence.jointCount || frameProjection.length / 2;
    for (let i = 0; i < jointCount; i++) {
      const u = frameProjection[i * 2];
      const v = frameProjection[i * 2 + 1];
      if (!Number.isFinite(u) || !Number.isFinite(v)) {
        continue;
      }
      ctx.beginPath();
      ctx.arc(u * scaleX, v * scaleY, 3, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.setTransform(1, 0, 0, 1, 0, 0);
  },
  ensureSequenceProjectionCache(sequence) {
    if (!sequence || sequence.projectionDirty) {
      return null;
    }
    if (
      (!sequence.projectedFrames || sequence.projectedFrames.length === 0) &&
      sequence.projectedFramesBuffer &&
      Array.isArray(sequence.projectedFramesShape)
    ) {
      const [frames, joints, dims] = sequence.projectedFramesShape;
      const expectedLength = frames * joints * dims;
      if (
        dims === 2 &&
        frames > 0 &&
        joints > 0 &&
        sequence.projectedFramesBuffer.length >= expectedLength
      ) {
        const frameStride = joints * dims;
        const list = new Array(frames);
        for (let frame = 0; frame < frames; frame++) {
          list[frame] = sequence.projectedFramesBuffer.subarray(frame * frameStride, (frame + 1) * frameStride);
        }
        sequence.projectedFrames = list;
      }
    }
    return sequence.projectedFrames || null;
  },
  refreshSequenceProjectionValidity(sequence) {
    if (!sequence) return;
    const hasProjection = (Array.isArray(sequence.projectedFrames) && sequence.projectedFrames.length > 0) ||
      (sequence.projectedFramesBuffer && Array.isArray(sequence.projectedFramesShape));
    if (!hasProjection) {
      sequence.projectionDirty = true;
      return;
    }
    const offset = sequence.offset;
    const offsetIsZero = !offset ||
      (Math.abs(offset.x || 0) < 1e-6 &&
       Math.abs(offset.y || 0) < 1e-6 &&
       Math.abs(offset.z || 0) < 1e-6);
    const rotation = sequence.rotation;
    const rotationIsZero = !rotation ||
      (Math.abs(rotation.x || 0) < 1e-6 &&
       Math.abs(rotation.y || 0) < 1e-6 &&
       Math.abs(rotation.z || 0) < 1e-6);
    sequence.projectionDirty = !(offsetIsZero && rotationIsZero);
  },
  
    clearForceArrowsForAnimation(animationIndex) {
      // Remove force arrows for a specific animation
      const animationIndexInt = parseInt(animationIndex);
  
      // Filter out force arrows belonging to this animation
      const arrowsToRemove = this.forceArrows.filter(arrowGroup =>
        arrowGroup.userData && arrowGroup.userData.animationIndex === animationIndexInt
      );
  
      // Remove from scene and dispose resources
      arrowsToRemove.forEach(arrowGroup => {
        if (this.scene) {
          this.scene.remove(arrowGroup);
        }
  
        arrowGroup.traverse((child) => {
          if (child.geometry) child.geometry.dispose();
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(mat => mat.dispose());
            } else {
              child.material.dispose();
            }
          }
        });
      });
  
      // Update forceArrows array
      this.forceArrows = this.forceArrows.filter(arrowGroup =>
        !arrowGroup.userData || arrowGroup.userData.animationIndex !== animationIndexInt
      );
  
      // Remove from forcesDatasets
      delete this.forcesDatasets[animationIndex];
  
      console.log(`Cleared force arrows for animation ${animationIndex}`);
    },
  
    getForceArrowCount(animationIndex) {
      // Count force arrows for a specific animation
      const animationIndexInt = parseInt(animationIndex);
      return this.forceArrows.filter(arrowGroup =>
        arrowGroup.userData && arrowGroup.userData.animationIndex === animationIndexInt
      ).length;
    },
  
    updateForceColor(colorValue, animationIndex) {
      let colorHex;
  
      // Handle v-color-picker input format
      if (colorValue && typeof colorValue === 'object') {
        if (colorValue.hex) {
          colorHex = '#' + colorValue.hex;
        }
      } else if (typeof colorValue === 'string') {
        colorHex = colorValue;
      }
  
      if (colorHex) {
        // Update color for specific animation index using $set for reactivity
        this.$set(this.forceColors, animationIndex, colorHex);
        this.$set(this.forceDisplayColors, animationIndex, colorHex);
  
                 // Update existing force colors for this specific animation
         this.updateForceArrowColors(animationIndex);
       }
     },
  
     updateForceArrowColors(animationIndex) {
      // Create THREE.Color object for proper color handling
       const threejsColor = new THREE.Color(this.getForceColor(animationIndex));
  
       // Update arrow colors for specific animation index
      this.forceArrows.forEach(platformGroup => {
         if (platformGroup.userData && platformGroup.userData.animationIndex === parseInt(animationIndex)) {
        platformGroup.children.forEach(arrowGroup => {
          arrowGroup.children.forEach(child => {
            if (child.material) {
              child.material.color.copy(threejsColor);
              child.material.needsUpdate = true;
            }
          });
        });
         }
      });
  
      // Re-render the scene
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
  
    updateForceScale() {
      // Re-create force arrows with new scale
      if (Object.keys(this.forcesDatasets).length > 0) {
        this.createForceArrows();
        // Update for current frame
        if (this.frames && this.frame < this.frames.length) {
          this.updateForceArrows(this.frame);
        }
      }
    },
  
    updateForceMinMagnitude() {
      // Update force arrow visibility based on new threshold
      if (Object.keys(this.forcesDatasets).length > 0) {
        // Update for current frame
        if (this.frames && this.frames.length) {
          this.updateForceArrows(this.frame);
        } else if (this.forceArrows.length > 0) {
          // For standalone forces, update with current frame index
          this.updateForceArrows(this.frame || 0);
        }
      }
    },
  
    // Extract marker data from JSON animation files for plotting
    extractMarkerDataFromJson(jsonData, animationIndex, fileName) {
      // Check if the JSON contains marker data
      if (!jsonData || !jsonData.time || !jsonData.bodies) return;
  
      // Look for marker data in the JSON structure
      const markerData = {};
      const markerNames = [];
  
      // Find all bodies that have translation data (potential markers)
      Object.keys(jsonData.bodies).forEach(bodyKey => {
        const body = jsonData.bodies[bodyKey];
  
        // Check if this body has translation data
        if (body.translation && Array.isArray(body.translation) && body.translation.length > 0) {
                     // Only extract explicit markers - be very restrictive
  
           // 1. Check if the body name explicitly suggests it's a marker
           const nameIndicatesMarker = bodyKey && bodyKey.toLowerCase && (
             bodyKey.toLowerCase().includes('marker') ||
             bodyKey.toLowerCase().includes('sphere') ||
             bodyKey.toLowerCase().includes('point')
           );
  
           // 2. Check if it has geometry that explicitly suggests it's a marker
           let geometryIndicatesMarker = false;
           if (body.attachedGeometries && body.attachedGeometries.length > 0) {
             geometryIndicatesMarker = body.attachedGeometries.some(geom =>
               geom && geom.meshName && geom.meshName.toLowerCase && (
                 geom.meshName.toLowerCase().includes('marker') ||
                 geom.meshName.toLowerCase().includes('sphere') ||
                 geom.meshName.toLowerCase().includes('point')
               )
             );
           }
  
           // Only include if explicitly marked as a marker (no general body parts)
           if (nameIndicatesMarker || geometryIndicatesMarker) {
             // Extract marker name from body key
             const markerName = bodyKey && bodyKey.replace ? bodyKey.replace(/[^a-zA-Z0-9_]/g, '_') : 'unknown_marker';
             if (markerName) {
               markerNames.push(markerName);
  
               // Initialize marker data arrays
               markerData[markerName] = {
                 x: [],
                 y: [],
                 z: []
               };
  
               // Extract position data for each frame
               for (let frameIndex = 0; frameIndex < jsonData.time.length; frameIndex++) {
                 if (body.translation[frameIndex] && Array.isArray(body.translation[frameIndex])) {
                   markerData[markerName].x.push(body.translation[frameIndex][0] || 0);
                   markerData[markerName].y.push(body.translation[frameIndex][1] || 0);
                   markerData[markerName].z.push(body.translation[frameIndex][2] || 0);
                 } else {
                   markerData[markerName].x.push(0);
                   markerData[markerName].y.push(0);
                   markerData[markerName].z.push(0);
                 }
               }
             }
           }
        }
      });
  
      // If we found marker data, store it in markersDatasets
      if (markerNames.length > 0) {
        const parsedData = {
          header: { source: 'JSON file' },
          markers: markerNames,
          frames: jsonData.time.map((_, index) => index),
          times: jsonData.time,
          data: markerData,
          fileName: fileName
        };
  
        // Store dataset for this animation
        this.markersDatasets[animationIndex] = parsedData;
  
        // Set visibility to true for new marker dataset
        this.$set(this.markersVisible, String(animationIndex), true);
  
        // Initialize colors for new marker dataset
        if (!this.markerColors[animationIndex]) {
          this.$set(this.markerColors, animationIndex, '#ff0000'); // Default red color
          this.$set(this.markerDisplayColors, animationIndex, '#ff0000');
        }
  
        console.log(`Extracted ${markerNames.length} markers from JSON file ${fileName} for animation ${animationIndex}:`, markerNames);
      } else {
        console.log(`No marker data found in JSON file ${fileName}`);
      }
    },
  
    // Marker visualization methods
    openMarkersDialogFromImport() {
      this.showImportDialog = false;
      // Trigger the hidden file input for markers files
      this.$refs.markersFileInput.click();
    },
  
    handleMarkersFileSelectFromImport(event) {
      const file = event.target.files[0];
      if (file) {
        this.markersFile = file;
        // Open the markers dialog with the selected file
      this.showMarkersDialog = true;
      }
      // Clear the input value so the same file can be selected again if needed
      event.target.value = '';
    },
  
    closeMarkersDialog() {
      this.showMarkersDialog = false;
      this.markersFile = null;
    },
  
    handleMarkersFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.markersFile = file;
      }
      // Clear the input value so the same file can be selected again if needed
      event.target.value = '';
    },
  
    updateMarkerColor(colorValue, animationIndex) {
      let colorHex;
  
      // Handle v-color-picker input format
      if (colorValue && typeof colorValue === 'object') {
        if (colorValue.hex) {
          colorHex = '#' + colorValue.hex;
        }
      } else if (typeof colorValue === 'string') {
        colorHex = colorValue;
      }
  
      if (colorHex) {
        // Update color for specific animation index using $set for reactivity
        this.$set(this.markerColors, animationIndex, colorHex);
        this.$set(this.markerDisplayColors, animationIndex, colorHex);
  
        // Update existing marker colors for this specific animation
        this.updateMarkerSphereColors(animationIndex);
      }
    },
  
    updateMarkerSphereColors(animationIndex) {
      // Create THREE.Color object for proper color handling
      const threejsColor = new THREE.Color(this.getMarkerColor(animationIndex));
  
      // Update marker sphere colors for specific animation index
      this.markerSpheres.forEach(sphere => {
        if (sphere.material && sphere.userData.animationIndex === parseInt(animationIndex)) {
          sphere.material.color.copy(threejsColor);
          sphere.material.needsUpdate = true;
        }
      });
  
      // Re-render the scene
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
  
    async loadMarkersFile() {
      if (!this.markersFile) return;
      this.loadingMarkers = true;
  
      // Set initial visibility for this animation
      const targetAnimationIndex = this.selectedAnimationForMarkers === null ? 0 : this.selectedAnimationForMarkers;
      this.$set(this.markersVisible, String(targetAnimationIndex), true);
  
      // Initialize marker visibility state if not set
      if (typeof this.markersVisible === 'undefined') {
        this.markersVisible = {};
      }
       try {
         const reader = new FileReader();
         reader.onload = (e) => {
           try {
           const wasEmpty = this.animations.length === 0;
           this.parseTrcFile(e.target.result, this.markersFile.name);
           this.showMarkersDialog = false;
           const message = wasEmpty ?
             'Markers file loaded as standalone visualization!' :
             'Markers file loaded successfully!';
           this.$toasted.success(message);
           } catch (parseError) {
             console.error('Error parsing markers file:', parseError);
             this.$toasted.error('Error parsing markers file');
           } finally {
             this.loadingMarkers = false;
           }
         };
         reader.onerror = () => {
           console.error('Error reading markers file');
           this.$toasted.error('Error reading markers file');
           this.loadingMarkers = false;
         };
         reader.readAsText(this.markersFile);
       } catch (error) {
         console.error('Error loading markers file:', error);
         this.$toasted.error('Error loading markers file');
         this.loadingMarkers = false;
       }
     },
  
     parseTrcFile(content, fileName = 'markers.trc') {
       console.log('Parsing TRC file:', fileName);
       console.log('Content length:', content.length);
       console.log('First 500 characters:', content.substring(0, 500));
       
       const lines = content.trim().split('\n');
       console.log('Number of lines:', lines.length);
       console.log('First 5 lines:', lines.slice(0, 5));
  
       // Parse header information
       const header = {};
       let dataStartIndex = 0;
  
       // Find the header end and data start
       let headerNames = [];
       let headerValues = [];
       let markerNamesLineIndex = -1;
       
       for (let i = 0; i < lines.length; i++) {
         const line = lines[i] ? lines[i].trim() : '';
         if (!line) continue;
         
         if (line.includes('DataRate') || line.includes('CameraRate') || line.includes('NumFrames') || line.includes('NumMarkers') || line.includes('Units')) {
           // This is the header names line
           headerNames = line.split('\t');
           // The next line should contain the values
           if (i + 1 < lines.length) {
             const valueLine = lines[i + 1] ? lines[i + 1].trim() : '';
             if (valueLine) {
               headerValues = valueLine.split('\t');
               
               // Create header object from names and values
               for (let j = 0; j < headerNames.length && j < headerValues.length; j++) {
                 header[headerNames[j]] = headerValues[j];
               }
               console.log('Parsed header:', header);
             }
           }
         }
  
         // Check for column headers line (contains Frame# and Time)
         if (line.includes('Frame#') && line.includes('Time')) {
           // This is the marker names line, store it for later parsing
           markerNamesLineIndex = i;
           // Skip the coordinate labels line and find the actual data start
           for (let j = i + 1; j < lines.length; j++) {
             const dataLine = lines[j] ? lines[j].trim() : '';
             if (dataLine && /^\d+\s/.test(dataLine)) {  // Line starts with a number
               dataStartIndex = j;
               break;
             }
           }
           break;
         }
       }
  
       // Parse column headers - find the marker names line (should contain Frame# and Time)
       if (markerNamesLineIndex === -1) {
         for (let i = 0; i < dataStartIndex; i++) {
           if (lines[i] && lines[i].includes('Frame#') && lines[i].includes('Time')) {
             markerNamesLineIndex = i;
             break;
           }
         }
       }
  
       if (markerNamesLineIndex === -1) {
         throw new Error('Could not find marker names line (Frame# and Time) in TRC file');
       }
  
       const headerLine = lines[markerNamesLineIndex];
       if (!headerLine) {
         throw new Error('Header line is undefined');
       }
       
       const columnHeaders = headerLine.split('\t');
  
       // Extract marker names by finding non-empty columns after Frame# and Time
       const markerNames = [];
       for (let i = 2; i < columnHeaders.length; i++) {
         const headerName = columnHeaders[i];
         if (headerName && headerName.trim()) {
           // Remove coordinate suffixes like :X, :Y, :Z
           const markerName = headerName.replace(/:.*$/, '').trim();
           if (markerName && markerNames.indexOf(markerName) === -1) {
             markerNames.push(markerName);
           }
         }
       }
  
       // Parse data rows
       const frameData = [];
       const timeData = [];
       const markerData = {};
  
       // Initialize marker data arrays
       markerNames.forEach(name => {
         markerData[name] = {
           x: [], y: [], z: []
         };
       });
  
       // Parse each data row
       for (let i = dataStartIndex; i < lines.length; i++) {
         const line = lines[i].trim();
         if (!line) continue;
  
         const values = line.split('\t');
         if (values.length < 2) continue;
  
         const frame = parseInt(values[0]);
         const time = parseFloat(values[1]);
  
         frameData.push(frame);
         timeData.push(time);
  
         // Parse marker positions (every 3 values after frame and time)
         let markerIndex = 0;
         for (let j = 2; j < values.length && markerIndex < markerNames.length; j += 3) {
           const markerName = markerNames[markerIndex];
           const x = parseFloat(values[j]) || 0;
           const y = parseFloat(values[j + 1]) || 0;
           const z = parseFloat(values[j + 2]) || 0;
  
           // Apply unit conversion based on header units
           let xConverted = x;
           let yConverted = y;
           let zConverted = z;
           
           const units = header.Units ? header.Units.toLowerCase().trim() : '';
           
           switch (units) {
             case 'mm':
             case 'millimeters':
               // Convert from mm to meters
               xConverted = x / 1000;
               yConverted = y / 1000;
               zConverted = z / 1000;
               break;
             case 'cm':
             case 'centimeters':
               // Convert from cm to meters
               xConverted = x / 100;
               yConverted = y / 100;
               zConverted = z / 100;
               break;
             case 'm':
             case 'meters':
             case 'meter':
               // Already in meters, no conversion needed
               xConverted = x;
               yConverted = y;
               zConverted = z;
               break;
             case 'in':
             case 'inches':
               // Convert from inches to meters (1 inch = 0.0254 meters)
               xConverted = x * 0.0254;
               yConverted = y * 0.0254;
               zConverted = z * 0.0254;
               break;
             case 'ft':
             case 'feet':
               // Convert from feet to meters (1 foot = 0.3048 meters)
               xConverted = x * 0.3048;
               yConverted = y * 0.3048;
               zConverted = z * 0.3048;
               break;
             default:
               // Default assumption: mm to meters (for backward compatibility)
               // Also log a warning for debugging
               if (units && units !== '') {
                 console.warn(`Unknown units "${units}" in TRC file, assuming millimeters`);
               }
               xConverted = x / 1000;
               yConverted = y / 1000;
               zConverted = z / 1000;
               break;
           }
  
           markerData[markerName].x.push(xConverted);
           markerData[markerName].y.push(yConverted);
           markerData[markerName].z.push(zConverted);
  
           markerIndex++;
         }
       }
  
       // Store the parsed data
       const parsedData = {
         header: header,
         markers: markerNames,
         frames: frameData,
         times: timeData,
         data: markerData,
         fileName: fileName
       };
  
       // Debug: Log the first few marker positions to verify parsing
       console.log('TRC File parsing debug:');
       console.log('Header units:', header.Units);
       console.log('Number of markers:', markerNames.length);
       console.log('Number of frames:', frameData.length);
       if (markerNames.length > 0) {
         const firstMarker = markerNames[0];
         console.log(`First marker "${firstMarker}" positions:`, {
           x: markerData[firstMarker].x.slice(0, 5),
           y: markerData[firstMarker].y.slice(0, 5),
           z: markerData[firstMarker].z.slice(0, 5)
         });
         
         // Also log a few more markers to see the range
         console.log('Sample marker positions (first 3 markers, first 3 frames):');
         for (let i = 0; i < Math.min(3, markerNames.length); i++) {
           const marker = markerNames[i];
           console.log(`${marker}:`, {
             x: markerData[marker].x.slice(0, 3),
             y: markerData[marker].y.slice(0, 3),
             z: markerData[marker].z.slice(0, 3)
           });
         }
       }
  
       // Handle case where no animations exist - create a standalone marker visualization
       let animationIndex = this.selectedAnimationForMarkers;
  
       if (this.animations.length === 0 || animationIndex === null) {
         // For standalone marker files, set up the frames for animation control
        if (this.frames.length === 0) {
         this.frames = timeData;
         this.frame = 0;
         if (timeData.length > 0) {
           this.updateDisplayedTime(0);
         } else {
           this.time = '0.000';
         }
        }
  
         // Calculate frame rate for marker data
         if(!this.frameRate) {
           this.frameRate = this.calculateFrameRate(timeData);
         }
  
         // Initialize the trial object for standalone markers
         this.trial = { results: [] };
  
         // Set animation index for markers
         if (this.animations.length === 0) {
           // Find next available index for standalone markers
           animationIndex = this.getNextAvailableMarkerIndex();
         } else {
           animationIndex = this.selectedAnimationForMarkers || 0;
         }
  
         this.selectedAnimationForMarkers = animationIndex;
       } else if (animationIndex === undefined) {
         // If no animation is selected but animations exist, use the first one
         animationIndex = 0;
         this.selectedAnimationForMarkers = 0;
       }
  
       // Store dataset for selected animation
       this.markersDatasets[animationIndex] = parsedData;
  
       // Debug: Log the stored data
       console.log('Stored marker dataset:', {
         animationIndex,
         dataset: this.markersDatasets[animationIndex],
         totalDatasets: Object.keys(this.markersDatasets).length
       });
  
       // Set visibility to true for new marker dataset
       this.$set(this.markersVisible, String(animationIndex), true);
  
       // Initialize colors for new marker dataset
       if (!this.markerColors[animationIndex]) {
         this.$set(this.markerColors, animationIndex, '#ff0000'); // Default red color
         this.$set(this.markerDisplayColors, animationIndex, '#ff0000');
       }
  
       // Store marker time data for syncing
       this.markerTimeData = {
         times: timeData,
         frames: frameData
       };
  
       // Initialize scene if it doesn't exist
       if (!this.scene && !this.sceneInitializing) {
         console.log('Initializing scene for standalone markers...');
         this.sceneInitializing = true;
         // Wait for DOM to be ready before initializing scene
         this.$nextTick(() => {
           this.$nextTick(() => {
             this.initScene();
             // Create marker spheres after scene is initialized
             this.$nextTick(() => {
               this.createMarkerSpheres();
               this.handlePostMarkerCreation();
             });
           });
         });
       } else {
         console.log('Scene already exists, using existing scene');
         // Create marker spheres
         this.createMarkerSpheres();
         this.handlePostMarkerCreation();
       }
     },
  
           handlePostMarkerCreation() {
        // For standalone marker files, start the animation loop and render first frame
        if (this.animations.length === 0) {
          this.animate();
          this.animateOneFrame();
  
          // Position camera to view markers
          this.positionCameraForMarkers();
  
          // Calculate animation duration for headless operation
          if (this.frames && this.frames.length > 0 && this.frameRate > 0) {
            this.animationDurationInSeconds = (this.frames.length - 1) / this.frameRate;
          }
  
          // Signal that all visuals are loaded for headless operation
          window.allVisualsLoaded = true;
        }
  
       // Clear any existing selection
       this.selectedMarker = null;
      },
  
     getNextAvailableMarkerIndex() {
       // Find the next available index for standalone markers
       let index = 0;
       while (this.markersDatasets[index]) {
         index++;
       }
       return index;
     },
  
     getMarkerVisibility(animationIndex) {
       // Return visibility for specific marker dataset
       // Ensure consistent key type (convert to string)
       const key = String(animationIndex);
       if (this.markersVisible[key] === undefined) {
         return true; // Default to visible
       }
       return this.markersVisible[key];
     },
  
     getMarkerColor(animationIndex) {
       // Return color for specific marker dataset
       if (this.markerColors[animationIndex] === undefined) {
         return '#ff0000'; // Default red color
       }
       return this.markerColors[animationIndex];
     },
  
     getMarkerDisplayColor(animationIndex) {
       // Ensure display color exists for color picker
       if (this.markerDisplayColors[animationIndex] === undefined) {
         this.$set(this.markerDisplayColors, animationIndex, this.getMarkerColor(animationIndex));
       }
       return this.markerDisplayColors[animationIndex];
     },
  
     getForceColor(animationIndex) {
       // Return color for specific force dataset
       if (this.forceColors[animationIndex] === undefined) {
         return '#00ff00'; // Default green color
       }
       return this.forceColors[animationIndex];
     },
  
     getForceDisplayColor(animationIndex) {
       // Ensure display color exists for color picker
       if (this.forceDisplayColors[animationIndex] === undefined) {
         this.$set(this.forceDisplayColors, animationIndex, this.getForceColor(animationIndex));
       }
       return this.forceDisplayColors[animationIndex];
     },
  
     createMarkerSpheres() {
       // Clear existing marker spheres
       this.clearMarkerSpheres();
  
       // Check if scene is initialized
       if (!this.scene && !this.sceneInitializing) {
         console.error('Scene not initialized when creating marker spheres');
         console.log('Attempting to initialize scene...');
         this.sceneInitializing = true;
         this.$nextTick(() => {
           this.$nextTick(() => {
             this.initScene();
             this.$nextTick(() => {
               this.createMarkerSpheres();
             });
           });
         });
         return;
       }
  
       // Create spheres for all marker datasets
       Object.keys(this.markersDatasets).forEach(animationIndex => {
       const markersData = this.markersDatasets[animationIndex];
  
       if (!markersData) {
           console.error('No markers data found for animation index:', animationIndex);
         return;
       }
  
       const markerNames = markersData.markers;
       const sphereGeometry = new THREE.SphereGeometry(this.markerSize / 1000, 16, 16); // Convert to meters
       const sphereMaterial = new THREE.MeshPhongMaterial({
           color: new THREE.Color(this.getMarkerColor(animationIndex)),
         transparent: true,
         opacity: 0.8
       });
  
         // Create spheres for each marker in this dataset
       markerNames.forEach(markerName => {
         const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial.clone());
           sphere.name = `${markerName}_${animationIndex}`;
         sphere.userData = {
           type: 'marker',
           markerName: markerName,
             animationIndex: parseInt(animationIndex)
         };
  
         // Set initial position (frame 0)
         if (markersData.data[markerName] && markersData.data[markerName].x.length > 0) {
             const x = markersData.data[markerName].x[0];
             const y = markersData.data[markerName].y[0];
             const z = markersData.data[markerName].z[0];
             sphere.position.set(x, y, z);
             console.log(`Created marker ${markerName} (dataset ${animationIndex}) at position (${x.toFixed(3)}, ${y.toFixed(3)}, ${z.toFixed(3)})`);
             
             // Debug: Check if position is very small (indicating potential unit conversion issue)
             if (Math.abs(x) < 0.001 && Math.abs(y) < 0.001 && Math.abs(z) < 0.001) {
               console.warn(`Warning: Marker ${markerName} has very small position values. This might indicate a unit conversion issue.`);
             }
           } else {
             console.warn(`No data found for marker ${markerName} in dataset ${animationIndex}`);
           }
  
           // Set visibility based on marker visibility state
           sphere.visible = this.getMarkerVisibility(parseInt(animationIndex));
  
         // Add to scene
         this.scene.add(sphere);
         this.markerSpheres.push(sphere);
         });
       });
  
       console.log(`Created marker spheres for ${Object.keys(this.markersDatasets).length} datasets. Total spheres: ${this.markerSpheres.length}`);
  
       // Add click event listener for marker selection
       this.addMarkerClickListener();
  
       // Update markers for current frame
       this.updateMarkerPositions();
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
     clearMarkerSpheres() {
       // Remove existing marker spheres from scene
       this.markerSpheres.forEach(sphere => {
         if (this.scene) {
           this.scene.remove(sphere);
         }
  
         // Dispose of geometry and material
         if (sphere.geometry) sphere.geometry.dispose();
         if (sphere.material) sphere.material.dispose();
       });
  
       this.markerSpheres = [];
  
       // Clear measurement data
       this.clearMeasurement();
  
       // Clear marker labels
       Object.values(this.markerLabels).forEach(label => {
         if (this.scene) {
           this.scene.remove(label);
         }
         if (label.material && label.material.map) {
           label.material.map.dispose();
         }
         if (label.material) label.material.dispose();
       });
  
       this.markerLabels = {};
     },
  
     updateMarkerPositions() {
       if (!this.showMarkers || this.markerSpheres.length === 0) return;
  
       // Use the frame reference for marker data
       if (!this.frames || this.frame >= this.frames.length || this.frame < 0) return;
  
       // For standalone marker files, use frame index directly
       const useFrameIndex = this.animations.length === 0;
       const currentTime = useFrameIndex ? this.frame : parseFloat(this.frames[this.frame]);
  
       // Update each marker sphere position
       this.markerSpheres.forEach(sphere => {
         const markerName = sphere.userData.markerName;
         const animationIndex = sphere.userData.animationIndex;
         const markersData = this.markersDatasets[animationIndex];
  
         if (!markersData || !markersData.data[markerName]) {
           return;
         }
  
         // Find the appropriate index in the marker data
         let closestIndex = 0;
  
         if (useFrameIndex) {
           // For standalone marker files, use frame index directly
           closestIndex = Math.min(this.frame, markersData.data[markerName].x.length - 1);
         } else {
           // For marker files with animations, find closest time
           const times = markersData.times;
         let minTimeDiff = Math.abs(times[0] - currentTime);
  
         for (let i = 1; i < times.length; i++) {
           const timeDiff = Math.abs(times[i] - currentTime);
           if (timeDiff < minTimeDiff) {
             minTimeDiff = timeDiff;
             closestIndex = i;
             }
           }
         }
  
         // Update sphere position
         const markerData = markersData.data[markerName];
         if (closestIndex < markerData.x.length) {
           const x = markerData.x[closestIndex];
           const y = markerData.y[closestIndex];
           const z = markerData.z[closestIndex];
  
           sphere.position.set(x, y, z);
  
           // Update selected marker coordinates if this is the selected marker
           if (this.selectedMarker &&
               this.selectedMarker.name === markerName &&
               this.selectedMarker.animationIndex === animationIndex) {
             this.selectedMarker.position.set(x, y, z);
           }
         }
       });
  
       // Update measurement positions if in measurement mode
       this.updateMeasurementPositions();
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
     addMarkerClickListener() {
       if (!this.renderer || !this.renderer.domElement) return;
  
       // Remove existing listener if it exists
       if (this.handleMarkerClick) {
         this.renderer.domElement.removeEventListener('click', this.handleMarkerClick);
       }
  
       // Create new click handler
       this.handleMarkerClick = (event) => {
         event.preventDefault();
  
         // Calculate mouse position in normalized device coordinates
         const rect = this.renderer.domElement.getBoundingClientRect();
         const mouse = new THREE.Vector2();
         mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
         mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  
         // Create raycaster
         const raycaster = new THREE.Raycaster();
         raycaster.setFromCamera(mouse, this.camera);
  
         // Check for intersections with marker spheres
         const intersects = raycaster.intersectObjects(this.markerSpheres);
  
         if (intersects.length > 0) {
           const selectedSphere = intersects[0].object;
           const markerName = selectedSphere.userData.markerName;
  
           // Check if in measurement mode and modifier keys are pressed
           if (this.measurementMode && (event.metaKey || event.ctrlKey || event.shiftKey)) {
             // Add/remove marker from measurement
             this.addMeasurementMarker(
               markerName,
               selectedSphere.position,
               selectedSphere.userData.animationIndex
             );
           } else {
             // Normal marker selection
           this.selectedMarker = {
             name: markerName,
             position: selectedSphere.position.clone(),
                        animationIndex: selectedSphere.userData.animationIndex
         };
  
         // Optional: Highlight selected marker
           this.highlightSelectedMarker(selectedSphere);
           }
         } else {
           // Deselect if clicking empty space
           this.selectedMarker = null;
           this.clearMarkerHighlight();
         }
       };
  
       // Add click event listener
       this.renderer.domElement.addEventListener('click', this.handleMarkerClick);
     },
  
     highlightSelectedMarker(selectedSphere) {
       // Reset all marker materials first
       this.markerSpheres.forEach(sphere => {
         sphere.material.color.setHex(this.markerColor.replace('#', '0x'));
         sphere.material.opacity = 0.8;
       });
  
       // Highlight selected marker
       selectedSphere.material.color.setHex(0xffff00); // Yellow highlight
       selectedSphere.material.opacity = 1.0;
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
     clearMarkerHighlight() {
       // Reset all marker materials
       this.markerSpheres.forEach(sphere => {
         const animationIndex = sphere.userData.animationIndex;
         const markerColor = this.getMarkerColor(animationIndex);
         sphere.material.color.setHex(markerColor.replace('#', '0x'));
         sphere.material.opacity = 0.8;
       });
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
     updateMarkerSize(size) {
       this.markerSize = size;
  
       // Update existing sphere sizes
       this.markerSpheres.forEach(sphere => {
         if (sphere.geometry) {
           sphere.geometry.dispose();
         }
         sphere.geometry = new THREE.SphereGeometry(size / 1000, 16, 16); // Convert to meters
       });
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
     clearMarkersForAnimation(animationIndex) {
       // Remove markers for specific animation
       if (this.markersDatasets[animationIndex]) {
         delete this.markersDatasets[animationIndex];
       }
  
       // Clear marker spheres for this animation
       this.markerSpheres = this.markerSpheres.filter(sphere => {
         if (sphere.userData.animationIndex === parseInt(animationIndex)) {
           this.scene.remove(sphere);
           return false;
         }
         return true;
       });
  
       // Clear selected marker if it belongs to this animation
       if (this.selectedMarker && this.selectedMarker.animationIndex === parseInt(animationIndex)) {
         this.selectedMarker = null;
       }
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
  
       this.$toasted.success('Markers cleared for animation');
     },
  
     clearAllMarkers() {
       // Clear all marker datasets
       this.markersDatasets = {};
  
       // Clear all marker spheres
       this.clearMarkerSpheres();
  
       // Clear selected marker
       this.selectedMarker = null;
  
       // Clear marker time data
       this.markerTimeData = null;
  
       // Clear measurement data
       this.clearMeasurement();
  
       this.$toasted.success('All markers cleared');
     },
  
     // Distance measurement methods
     toggleMeasurementMode() {
       this.measurementMode = !this.measurementMode;
  
       if (this.measurementMode) {
         this.$toasted.info('Measurement mode enabled. Hold Cmd/Shift + Click on markers to measure distance.');
       } else {
         this.$toasted.info('Measurement mode disabled.');
         this.clearMeasurement();
       }
     },
  
     clearMeasurement() {
       // Clear measurement markers
       this.measurementMarkers = [];
  
       // Remove measurement line from scene
       if (this.measurementLine) {
         this.scene.remove(this.measurementLine);
         this.measurementLine.geometry.dispose();
         this.measurementLine.material.dispose();
         this.measurementLine = null;
       }
  
       // Reset distance
       this.currentDistance = 0;
  
       // Re-render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
     addMeasurementMarker(markerName, position, animationIndex) {
       // Check if this marker is already selected
       const existingIndex = this.measurementMarkers.findIndex(m => m.name === markerName);
  
       if (existingIndex !== -1) {
         // If marker is already selected, remove it
         this.measurementMarkers.splice(existingIndex, 1);
         this.$toasted.info(`Removed ${markerName} from measurement`);
       } else {
         // Add new marker
         if (this.measurementMarkers.length >= 2) {
           // Replace the first marker with the new one
           this.measurementMarkers.shift();
         }
  
         this.measurementMarkers.push({
           name: markerName,
           position: position.clone(),
           animationIndex: animationIndex
         });
  
         this.$toasted.info(`Added ${markerName} to measurement`);
       }
  
       // Update measurement line and distance
       this.updateMeasurementLine();
     },
  
     updateMeasurementLine() {
       // Remove existing line
       if (this.measurementLine) {
         this.scene.remove(this.measurementLine);
         this.measurementLine.geometry.dispose();
         this.measurementLine.material.dispose();
         this.measurementLine = null;
       }
  
       // Create new line if we have exactly 2 markers
       if (this.measurementMarkers.length === 2) {
         const marker1 = this.measurementMarkers[0];
         const marker2 = this.measurementMarkers[1];
  
         // Calculate distance
         this.currentDistance = marker1.position.distanceTo(marker2.position);
  
         // Create line geometry
         const lineGeometry = new THREE.BufferGeometry().setFromPoints([
           marker1.position,
           marker2.position
         ]);
  
         // Create line material
         const lineMaterial = new THREE.LineBasicMaterial({
           color: 0x00ff00,
           linewidth: 3,
           transparent: true,
           opacity: 0.8
         });
  
         // Create line mesh
         this.measurementLine = new THREE.Line(lineGeometry, lineMaterial);
         this.measurementLine.userData = { type: 'measurement' };
  
         // Add to scene
         this.scene.add(this.measurementLine);
  
         // Re-render the scene
         if (this.renderer && this.scene && this.camera) {
           this.renderer.render(this.scene, this.camera);
         }
       } else {
         this.currentDistance = 0;
       }
     },
  
     updateMeasurementPositions() {
       if (!this.measurementMode || this.measurementMarkers.length !== 2) return;
  
       // Update marker positions in measurement array
       this.measurementMarkers.forEach((measurementMarker, index) => {
         // Find the corresponding sphere in the scene
         const sphere = this.markerSpheres.find(s =>
           s.userData.markerName === measurementMarker.name &&
           s.userData.animationIndex === measurementMarker.animationIndex
         );
  
         if (sphere) {
           this.measurementMarkers[index].position.copy(sphere.position);
         }
       });
  
       // Update the measurement line with new positions
       this.updateMeasurementLine();
     },
  
     positionCameraForMarkers() {
       if (!this.markerSpheres || this.markerSpheres.length === 0) {
         console.log('No markers to position camera for');
         return;
       }
  
       // Calculate bounding box of all markers
       const box = new THREE.Box3();
       this.markerSpheres.forEach(sphere => {
         box.expandByObject(sphere);
       });
  
       if (box.isEmpty()) {
         console.log('Marker bounding box is empty');
         return;
       }
  
       // Get the center and size of the bounding box
       const center = box.getCenter(new THREE.Vector3());
       const size = box.getSize(new THREE.Vector3());
  
       // Calculate the maximum dimension to determine camera distance
       const maxDim = Math.max(size.x, size.y, size.z);
  
       // Position camera at a comfortable distance
       const distance = maxDim * 3; // Adjust multiplier as needed
       const height = Math.max(center.y + size.y, 2); // Ensure camera is above ground
  
       // Set camera position
       this.camera.position.set(
         center.x + distance * 0.7,
         height,
         center.z + distance * 0.7
       );
  
       // Point camera at the center of the markers
       this.camera.lookAt(center);
  
       // Update camera controls target
       if (this.controls) {
         this.controls.target.copy(center);
         this.controls.update();
       }
  
       console.log(`Camera positioned for markers at distance ${distance.toFixed(2)} from center:`, center);
  
       // Render the scene
       if (this.renderer && this.scene && this.camera) {
         this.renderer.render(this.scene, this.camera);
       }
     },
  
    toggleCameraControls() {
      this.showCameraControls = !this.showCameraControls;
      console.log('Toggled camera controls visibility:', this.showCameraControls);
    },
  
    toggleForceVisibility(animationIndex) {
      const key = String(animationIndex);
      this.$set(this.forcesVisible, key, !this.forcesVisible[key]);
      this.forceArrows.forEach(group => {
        if (group.userData && group.userData.animationIndex === parseInt(animationIndex)) {
          group.visible = this.forcesVisible[key];
        }
      });
      this.renderer.render(this.scene, this.camera);
    },
  
    toggleMarkerVisibility(animationIndex) {
      // Ensure consistent key type (convert to string)
      const key = String(animationIndex);
      this.$set(this.markersVisible, key, !this.markersVisible[key]);
      this.markerSpheres.forEach(sphere => {
        if (sphere.userData && sphere.userData.animationIndex === parseInt(animationIndex)) {
          sphere.visible = this.markersVisible[key];
        }
      });
      this.renderer.render(this.scene, this.camera);
    },
  
    // Sample selection methods
    selectSampleSet(sampleSetId) {
      console.log('Selected sample set:', sampleSetId);
      this.showSampleSelectionDialog = false;
      // Always load video when selecting from UI dialog
      this.loadSampleFiles(sampleSetId, null, true);
    },
  
    getSampleIcon(sampleSetId) {
      const iconMap = {
        'STS': 'mdi-chair-rolling',
        'squat': 'mdi-human-handsdown',
        'walk': 'mdi-walk',
        'rmasb': 'mdi-run-fast',
        'walk_ts': 'mdi-walk'
      };
      return iconMap[sampleSetId] || 'mdi-play-circle';
    },
  
    // Share functionality methods
    async openShareDialog() {
      this.showShareDialog = true;
      this.loadingInitialShare = true;
      try {
        await this.generateShareUrl();
      } finally {
        this.loadingInitialShare = false;
      }
    },
  
    async generateShareUrl() {
      this.generatingShareUrl = true;
      try {
        const shareData = this.getShareData();
        const compressed = this.compressShareData(shareData);
        const baseUrl = window.location.origin + window.location.pathname;
  
        // If the compressed data is still too large, use hash-based storage
        if (compressed.length > 1000) {
          // Only generate a new shareId if one doesn't already exist
          if (!this.shareId) {
            this.shareId = this.generateShareId();
          }
          await this.storeShareData(this.shareId, shareData);
          this.shareUrl = `${baseUrl}?shareId=${this.shareId}`;
        } else {
          this.shareUrl = `${baseUrl}?share=${compressed}`;
        }
  
        this.shareUrlSize = this.shareUrl.length;
      } catch (error) {
        console.error('Error generating share URL:', error);
        this.$toasted.error('Failed to generate share URL');
      } finally {
        this.generatingShareUrl = false;
      }
    },
  
    generateShareId() {
      // Generate a short, unique ID
      const timestamp = Date.now().toString(36);
      const random = Math.random().toString(36).substr(2, 5);
      return `${timestamp}${random}`;
    },
  
    async storeShareData(shareId, data) {
      try {
        if (!shareId || !data) {
          throw new Error('shareId and data are required');
        }

        // Try cloud storage first
        const response = await fetch('https://opencap-share-backend.onrender.com/api/share', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ shareId, data })
        });
  
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            console.log(`Stored share data in cloud with ID: ${shareId}`);
            return;
          } else {
            throw new Error('Server returned unsuccessful response');
          }
        } else {
          // Parse error response
          let errorMessage = 'Failed to store share data';
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorData.details || errorMessage;
            console.error('Server error:', errorData);
          } catch (e) {
            console.error('Failed to parse error response:', e);
          }
          
          // Fallback to localStorage if cloud fails
          console.warn('Cloud storage failed, falling back to localStorage:', errorMessage);
          const shareKey = `opencap_share_${shareId}`;
          localStorage.setItem(shareKey, JSON.stringify(data));
          console.log(`Stored share data locally with ID: ${shareId}`);
          return;
        }
  
      } catch (error) {
        console.error('Error storing share data:', error);
        // Final fallback to localStorage
        try {
          const shareKey = `opencap_share_${shareId}`;
          localStorage.setItem(shareKey, JSON.stringify(data));
          console.log(`Fallback: Stored share data locally with ID: ${shareId}`);
        } catch (localError) {
          console.error('Failed to store in localStorage:', localError);
          throw new Error('Failed to store share data in both cloud and local storage');
        }
      }
    },
  
    async loadShareData(shareId) {
      try {
        if (!shareId) {
          throw new Error('Share ID is required');
        }

        // Try cloud storage first
        const response = await fetch(`https://opencap-share-backend.onrender.com/api/share/${shareId}`);
  
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.data) {
            console.log(`Loaded share data from cloud with ID: ${shareId}`);
            return result.data;
          } else {
            throw new Error('Invalid response format from server');
          }
        } else {
          // Parse error response
          let errorMessage = 'Share not found';
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch (e) {
            // If response is not JSON, use status text
            errorMessage = response.statusText || errorMessage;
          }
          
          // Only fallback to localStorage if it's a 404 (not found)
          if (response.status === 404) {
            console.warn('Cloud data not found, trying localStorage');
            const shareKey = `opencap_share_${shareId}`;
            const storedData = localStorage.getItem(shareKey);
            if (storedData) {
              console.log(`Loaded share data from localStorage with ID: ${shareId}`);
              return JSON.parse(storedData);
            }
          }
          
          throw new Error(errorMessage);
        }
  
      } catch (error) {
        console.error('Error loading share data:', error);
        // Re-throw with more context
        if (error.message) {
          throw error;
        }
        throw new Error('Invalid or expired share ID');
      }
    },
  
    getShareData() {
      // Only include essential animation data - no settings by default
      const data = {
        animations: this.animations.map(anim => ({
          data: this.compressAnimationData(anim.data),
          trialName: anim.trialName,
          fileName: anim.fileName,
          offset: [anim.offset.x, anim.offset.y, anim.offset.z], // Use array instead of object
          rotation: anim.rotation ? {
            x: THREE.Math.radToDeg(anim.rotation.x),
            y: THREE.Math.radToDeg(anim.rotation.y),
            z: THREE.Math.radToDeg(anim.rotation.z)
          } : { x: 0, y: 0, z: 0 }
        })),
        smplSequences: this.smplSequences.map(seq => ({
          name: seq.name,
          fileName: seq.fileName,
          gender: seq.gender,
          frame_count: seq.frameCount,
          vertex_count: seq.vertexCount,
          joint_count: seq.jointCount,
          fps: seq.fps,
          time: seq.time,
          faces: seq.faces || [],
          vertices: seq.vertices ? this.encodeFloat32ToBase64(seq.vertices) : '',
          joints: seq.joints ? this.encodeFloat32ToBase64(seq.joints) : '',
          skeleton_edges: seq.skeletonEdges || [],
          offset: [seq.offset.x, seq.offset.y, seq.offset.z],
          rotation: seq.rotation ? {
            x: THREE.Math.radToDeg(seq.rotation.x),
            y: THREE.Math.radToDeg(seq.rotation.y),
            z: THREE.Math.radToDeg(seq.rotation.z)
          } : { x: 0, y: 0, z: 0 },
          color: seq.color ? seq.color.getHex() : null,
          opacity: seq.opacity !== undefined ? seq.opacity : 1.0,
          visible: seq.visible !== undefined ? seq.visible : true,
          playable: seq.playable !== undefined ? seq.playable : true,
          showSkeleton: seq.showSkeleton !== undefined ? seq.showSkeleton : false,
          speedMultiplier: seq.speedMultiplier !== undefined ? seq.speedMultiplier : 1.0,
          projected_joints: seq.projectedFramesBuffer ? this.encodeFloat32ToBase64(seq.projectedFramesBuffer) : null,
          projected_shape: seq.projectedFramesShape || null,
          projected_image_size: seq.projectedImageSize || null
        })),
        forces: this.forcesDatasets,
        markers: this.markersDatasets
      };
  
      // Only include optional data if specifically requested
      if (this.shareSettings.includeCamera && this.camera) {
        data.camera = {
          position: {
            x: this.camera.position.x,
            y: this.camera.position.y,
            z: this.camera.position.z
          },
          target: {
            x: this.controls?.target.x || 0,
            y: this.controls?.target.y || 0,
            z: this.controls?.target.z || 0
          }
        };
      }
  
      if (this.shareSettings.includeColors) {
        data.colors = this.colors.map(color => color.getHex());
        data.alphaValues = [...this.alphaValues];
      }
  
      if (this.shareSettings.includeCurrentFrame) {
        data.currentFrame = this.frame;
      }
  
      // Include timelapse data if timelapse mode is enabled and there are timelapse meshes
      if (this.timelapseMode && Object.keys(this.timelapseMeshes).length > 0) {
        data.timelapse = {
          enabled: true,
          interval: this.timelapseInterval,
          opacity: this.timelapseOpacity,
          meshes: Object.values(this.timelapseMeshes).map(({mesh, frame, animIndex, body, geom}) => {
            return {
              frame: frame,
              animIndex: animIndex,
              body: body,
              geom: geom,
              position: [mesh.position.x, mesh.position.y, mesh.position.z],
              rotation: [mesh.quaternion.x, mesh.quaternion.y, mesh.quaternion.z, mesh.quaternion.w],
              scale: [mesh.scale.x, mesh.scale.y, mesh.scale.z]
            };
          })
        };
      }
  
      return data;
    },
  
    compressAnimationData(animData) {
      // Create a highly compressed version of animation data
      const compressed = {
        t: animData.time, // Keep time array as is for now
        b: {} // bodies
      };
  
      // Compress each body's data
      Object.keys(animData.bodies).forEach(bodyKey => {
        const body = animData.bodies[bodyKey];
        // Processing body data for compression
  
        compressed.b[bodyKey] = {
          g: body.attachedGeometries, // geometries
          s: body.scaleFactors, // scale factors
          p: [], // positions (compressed)
          r: []  // rotations (compressed)
        };
  
        // Compress position data - reduce precision and use deltas
        if (body.translation && body.translation.length > 0) {
          const positions = [];
          for (let frame = 0; frame < body.translation.length; frame++) {
            if (frame === 0) {
              // First frame: store full coordinates with reduced precision
              positions.push([
                Math.round(body.translation[frame][0] * 1000) / 1000,
                Math.round(body.translation[frame][1] * 1000) / 1000,
                Math.round(body.translation[frame][2] * 1000) / 1000
              ]);
            } else {
              // Subsequent frames: store deltas if significant
              const prev = body.translation[frame - 1];
              const curr = body.translation[frame];
              const deltaX = Math.round((curr[0] - prev[0]) * 1000) / 1000;
              const deltaY = Math.round((curr[1] - prev[1]) * 1000) / 1000;
              const deltaZ = Math.round((curr[2] - prev[2]) * 1000) / 1000;
  
              // Only store if delta is significant (>0.001)
              if (Math.abs(deltaX) > 0.001 || Math.abs(deltaY) > 0.001 || Math.abs(deltaZ) > 0.001) {
                positions.push([deltaX, deltaY, deltaZ]);
              } else {
                positions.push(null); // No significant change
              }
            }
          }
          compressed.b[bodyKey].p = positions;
        }
  
        // Compress rotation data similarly
        if (body.rotation && body.rotation.length > 0) {
          const rotations = [];
          for (let frame = 0; frame < body.rotation.length; frame++) {
            if (frame === 0) {
              rotations.push([
                Math.round(body.rotation[frame][0] * 1000) / 1000,
                Math.round(body.rotation[frame][1] * 1000) / 1000,
                Math.round(body.rotation[frame][2] * 1000) / 1000
              ]);
            } else {
              const prev = body.rotation[frame - 1];
              const curr = body.rotation[frame];
              const deltaX = Math.round((curr[0] - prev[0]) * 1000) / 1000;
              const deltaY = Math.round((curr[1] - prev[1]) * 1000) / 1000;
              const deltaZ = Math.round((curr[2] - prev[2]) * 1000) / 1000;
  
              if (Math.abs(deltaX) > 0.001 || Math.abs(deltaY) > 0.001 || Math.abs(deltaZ) > 0.001) {
                rotations.push([deltaX, deltaY, deltaZ]);
              } else {
                rotations.push(null);
              }
            }
          }
          compressed.b[bodyKey].r = rotations;
        }
      });
  
      // Compression complete
  
      return compressed;
    },
  
    decompressAnimationData(compressed) {
      // Reconstruct the original animation data format
      const animData = {
        time: compressed.t,
        bodies: {}
      };
  
      Object.keys(compressed.b).forEach(bodyKey => {
        const compressedBody = compressed.b[bodyKey];
        animData.bodies[bodyKey] = {
          attachedGeometries: compressedBody.g,
          scaleFactors: compressedBody.s,
          translation: [],
          rotation: []
        };
  
        // Decompress positions
        if (compressedBody.p && compressedBody.p.length > 0) {
          let currentPos = [0, 0, 0];
          for (let frame = 0; frame < compressedBody.p.length; frame++) {
            if (frame === 0) {
              currentPos = [...compressedBody.p[frame]];
            } else {
              if (compressedBody.p[frame] !== null) {
                currentPos[0] += compressedBody.p[frame][0];
                currentPos[1] += compressedBody.p[frame][1];
                currentPos[2] += compressedBody.p[frame][2];
              }
            }
            animData.bodies[bodyKey].translation.push([...currentPos]);
          }
        }
  
        // Decompress rotations
        if (compressedBody.r && compressedBody.r.length > 0) {
          let currentRot = [0, 0, 0];
          for (let frame = 0; frame < compressedBody.r.length; frame++) {
            if (frame === 0) {
              currentRot = [...compressedBody.r[frame]];
            } else {
              if (compressedBody.r[frame] !== null) {
                currentRot[0] += compressedBody.r[frame][0];
                currentRot[1] += compressedBody.r[frame][1];
                currentRot[2] += compressedBody.r[frame][2];
              }
            }
            animData.bodies[bodyKey].rotation.push([...currentRot]);
          }
        }
      });
  
      // Decompression complete
  
      return animData;
    },
  
    compressShareData(data) {
      try {
        // Optimize the data structure for smaller size
        const optimizedData = this.optimizeShareData(data);
        const jsonString = JSON.stringify(optimizedData);
  
        // Use more efficient encoding
        return this.lzCompress(jsonString);
      } catch (error) {
        console.error('Error compressing share data:', error);
        throw new Error('Failed to compress data for sharing');
      }
    },
  
    optimizeShareData(data) {
      // Create a more compact representation
      const optimized = {
        v: 1, // version
        a: data.animations.map(anim => ({
          d: anim.data,
          n: anim.trialName,
          f: anim.fileName,
          o: [anim.offset.x, anim.offset.y, anim.offset.z]
        }))
      };
  
      if (data.camera) {
        optimized.c = {
          p: [data.camera.position.x, data.camera.position.y, data.camera.position.z],
          t: [data.camera.target.x, data.camera.target.y, data.camera.target.z]
        };
      }
  
      if (data.colors) {
        optimized.col = data.colors;
      }
  
      if (data.alphaValues) {
        optimized.alp = data.alphaValues;
      }
  
      if (data.settings) {
        optimized.s = data.settings;
      }
  
      if (data.currentFrame !== undefined) {
        optimized.fr = data.currentFrame;
      }
  
      if (data.timelapse) {
        optimized.tl = data.timelapse;
      }
  
      return optimized;
    },
  
    unoptimizeShareData(optimized) {
      // Convert back to full format
      const data = {
        animations: optimized.a.map(anim => ({
          data: anim.d,
          trialName: anim.n,
          fileName: anim.f,
          offset: {
            x: anim.o[0] || 0,
            y: anim.o[1] || 0,
            z: anim.o[2] || 0
          }
        }))
      };
  
      if (optimized.c) {
        data.camera = {
          position: {
            x: optimized.c.p[0],
            y: optimized.c.p[1],
            z: optimized.c.p[2]
          },
          target: {
            x: optimized.c.t[0],
            y: optimized.c.t[1],
            z: optimized.c.t[2]
          }
        };
      }
  
      if (optimized.col) {
        data.colors = optimized.col;
      }
  
      if (optimized.alp) {
        data.alphaValues = optimized.alp;
      }
  
      if (optimized.s) {
        data.settings = optimized.s;
      }
  
      if (optimized.fr !== undefined) {
        data.currentFrame = optimized.fr;
      }
  
      if (optimized.tl) {
        data.timelapse = optimized.tl;
      }
  
      return data;
    },
  
    lzCompress(str) {
      // Simple LZ-style compression for URLs
      const dict = {};
      let data = (str + '').split('');
      let out = [];
      let currChar;
      let phrase = data[0];
      let code = 256;
  
      for (let i = 1; i < data.length; i++) {
        currChar = data[i];
        if (dict[phrase + currChar] != null) {
          phrase += currChar;
        } else {
          out.push(phrase.length > 1 ? dict[phrase] : phrase.charCodeAt(0));
          dict[phrase + currChar] = code;
          code++;
          phrase = currChar;
        }
      }
      out.push(phrase.length > 1 ? dict[phrase] : phrase.charCodeAt(0));
  
      // Convert to base64 for URL safety
      return btoa(encodeURIComponent(JSON.stringify(out)));
    },
  
    lzDecompress(compressed) {
      try {
        const out = JSON.parse(decodeURIComponent(atob(compressed)));
        const dict = {};
        let data = [];
        let currChar = String.fromCharCode(out[0]);
        let oldPhrase = currChar;
        data.push(currChar);
        let code = 256;
        let phrase;
  
        for (let i = 1; i < out.length; i++) {
          let currCode = out[i];
          if (currCode < 256) {
            phrase = String.fromCharCode(currCode);
          } else {
            phrase = dict[currCode] ? dict[currCode] : (oldPhrase + currChar);
          }
          data.push(phrase);
          currChar = phrase.charAt(0);
          dict[code] = oldPhrase + currChar;
          code++;
          oldPhrase = phrase;
        }
        return data.join('');
      } catch (error) {
        console.error('LZ decompression failed:', error);
        throw error;
      }
    },
  
    decompressShareData(compressed) {
      try {
        const jsonString = this.lzDecompress(compressed);
        const optimizedData = JSON.parse(jsonString);
        return this.unoptimizeShareData(optimizedData);
      } catch (error) {
        console.error('Error decompressing share data:', error);
        // Try fallback to old format
        try {
          const jsonString = decodeURIComponent(atob(compressed));
          return JSON.parse(jsonString);
        } catch (fallbackError) {
          console.error('Fallback decompression also failed:', fallbackError);
          throw new Error('Invalid share data');
        }
      }
    },
  
    async loadSharedVisualization(shareData) {
      try {
        console.log('Loading shared visualization:', shareData);
  
        // Set up the trial structure
        this.trial = { results: [] };
        this.animations = [];
        this.meshes = {};
  
        // Load animations from shared data
        for (let i = 0; i < shareData.animations.length; i++) {
          const animData = shareData.animations[i];
  
          // Decompress animation data if it's in compressed format
          const decompressedData = animData.data.t ?
            this.decompressAnimationData(animData.data) :
            animData.data;
  
          // Handle both old and new offset formats
          const offset = Array.isArray(animData.offset) ?
            new THREE.Vector3(animData.offset[0] || 0, animData.offset[1] || 0, animData.offset[2] || 0) :
            new THREE.Vector3(
              animData.offset?.x || 0,
              animData.offset?.y || 0,
              animData.offset?.z || 0
            );
  
          this.animations.push({
            data: decompressedData,
            trialName: animData.trialName,
            fileName: animData.fileName,
            offset: offset,
            rotation: new THREE.Euler(
              THREE.Math.degToRad(animData.rotation?.x || 0),
              THREE.Math.degToRad(animData.rotation?.y || 0),
              THREE.Math.degToRad(animData.rotation?.z || 0),
              'XYZ'
            ),
            calculatedFps: this.calculateFrameRate(decompressedData.time),
            visible: true, // Default to visible
            playable: true // Default to playable
          });
  
          this.initializeAlphaValue(i);
          // Ensure all color arrays are synchronized when adding new animations
          this.ensureColorArraysSync();
        }
  
        // Load SMPL sequences from shared data
        if (shareData.smplSequences && Array.isArray(shareData.smplSequences)) {
          for (let i = 0; i < shareData.smplSequences.length; i++) {
            const seqData = shareData.smplSequences[i];
            
            // Prepare sequence data in the format expected by addSmplSequence
            const sequenceData = {
              name: seqData.name,
              frame_count: seqData.frame_count,
              vertex_count: seqData.vertex_count,
              joint_count: seqData.joint_count,
              fps: seqData.fps,
              time: seqData.time,
              faces: seqData.faces || [],
              vertices: seqData.vertices || '',
              joints: seqData.joints || '',
              skeleton_edges: seqData.skeleton_edges || [],
              gender: seqData.gender || 'neutral',
              projected_joints: seqData.projected_joints || null,
              projected_shape: seqData.projected_shape || null,
              projected_image_size: seqData.projected_image_size || seqData.projected_imageSize || null
            };
            
            // Load the SMPL sequence
            await this.addSmplSequence(sequenceData, seqData.fileName || seqData.name);
            
            // Apply offset, rotation, color, and other properties after loading
            const loadedSequence = this.smplSequences[this.smplSequences.length - 1];
            if (loadedSequence) {
              // Apply offset
              if (Array.isArray(seqData.offset)) {
                loadedSequence.offset.set(seqData.offset[0] || 0, seqData.offset[1] || 0, seqData.offset[2] || 0);
              } else if (seqData.offset) {
                loadedSequence.offset.set(seqData.offset.x || 0, seqData.offset.y || 0, seqData.offset.z || 0);
              }
              
              // Apply rotation
              if (seqData.rotation) {
                const rotX = seqData.rotation.x !== undefined ? THREE.Math.degToRad(seqData.rotation.x) : 0;
                const rotY = seqData.rotation.y !== undefined ? THREE.Math.degToRad(seqData.rotation.y) : 0;
                const rotZ = seqData.rotation.z !== undefined ? THREE.Math.degToRad(seqData.rotation.z) : 0;
                loadedSequence.rotation.set(rotX, rotY, rotZ);
              }
              
              // Apply color
              if (seqData.color !== undefined && seqData.color !== null) {
                loadedSequence.color.setHex(seqData.color);
                loadedSequence.baseColor.setHex(seqData.color);
                loadedSequence.displayColor = this.formatColor(loadedSequence.color);
                if (loadedSequence.mesh && loadedSequence.mesh.material) {
                  loadedSequence.mesh.material.color.setHex(seqData.color);
                }
              }
              
              // Apply opacity
              if (seqData.opacity !== undefined) {
                loadedSequence.opacity = seqData.opacity;
                if (loadedSequence.mesh && loadedSequence.mesh.material) {
                  loadedSequence.mesh.material.opacity = seqData.opacity;
                  loadedSequence.mesh.material.transparent = seqData.opacity < 1.0;
                }
              }
              
              // Apply visibility and playability
              if (seqData.visible !== undefined) {
                loadedSequence.visible = seqData.visible;
                if (loadedSequence.mesh) {
                  loadedSequence.mesh.visible = seqData.visible;
                }
                if (loadedSequence.skeleton) {
                  loadedSequence.skeleton.visible = seqData.visible && loadedSequence.showSkeleton;
                }
              }
              
              if (seqData.playable !== undefined) {
                loadedSequence.playable = seqData.playable;
              }
              
              if (seqData.showSkeleton !== undefined) {
                loadedSequence.showSkeleton = seqData.showSkeleton;
                if (loadedSequence.skeleton) {
                  loadedSequence.skeleton.visible = loadedSequence.visible && seqData.showSkeleton;
                }
              }
              
              if (seqData.speedMultiplier !== undefined) {
                loadedSequence.speedMultiplier = seqData.speedMultiplier;
              }
              
              // Update mesh position and rotation
              if (loadedSequence.mesh) {
                loadedSequence.mesh.position.copy(loadedSequence.offset);
                loadedSequence.mesh.rotation.copy(loadedSequence.rotation);
              }
              if (loadedSequence.skeleton) {
                loadedSequence.skeleton.position.copy(loadedSequence.offset);
                loadedSequence.skeleton.rotation.copy(loadedSequence.rotation);
              }
            }
          }
        }

        // Load forces and markers if they exist
        if (shareData.forces) {
          this.forcesDatasets = shareData.forces;
        }
        if (shareData.markers) {
          this.markersDatasets = shareData.markers;
        }

        // Set frames from first animation or SMPL sequence
        if (this.animations.length > 0) {
          this.frames = this.animations[0].data.time;
          this.frameRate = this.animations[0].calculatedFps;
          console.log(`[loadSharedVisualization] Frames setup - Total frames: ${this.frames.length}, Frame rate: ${this.frameRate}, Current frame: ${this.frame}`);
          console.log(`[loadSharedVisualization] First few frames:`, this.frames.slice(0, 5));
          console.log(`[loadSharedVisualization] Last few frames:`, this.frames.slice(-5));
        } else if (this.smplSequences.length > 0 && this.smplSequences[0].time) {
          this.frames = [...this.smplSequences[0].time];
          this.frameRate = this.smplSequences[0].fps || 60;
          this.frame = 0;
          console.log(`[loadSharedVisualization] Frames setup from SMPL - Total frames: ${this.frames.length}, Frame rate: ${this.frameRate}`);
        }
  
        // Apply shared settings
        if (shareData.settings) {
          const settings = shareData.settings;
          this.backgroundColor = settings.backgroundColor || this.backgroundColor;
          this.groundColor = settings.groundColor || this.groundColor;
          this.groundPositionY = settings.groundPositionY !== undefined ? settings.groundPositionY : this.groundPositionY;
          this.showGround = settings.showGround !== undefined ? settings.showGround : this.showGround;
          this.useGroundTexture = settings.useGroundTexture !== undefined ? settings.useGroundTexture : this.useGroundTexture;
          this.useCheckerboard = settings.useCheckerboard !== undefined ? settings.useCheckerboard : this.useCheckerboard;
                  // Marker settings removed
        }
  
        // Apply shared colors
        if (shareData.colors) {
          shareData.colors.forEach((colorHex, index) => {
            if (index < this.colors.length) {
              this.colors[index].setHex(colorHex);
            }
          });
        }
  
        if (shareData.alphaValues) {
          this.alphaValues = [...shareData.alphaValues];
        }
  
        // Set current frame
        if (shareData.currentFrame !== undefined) {
          this.frame = Math.round(shareData.currentFrame);
          this.updateDisplayedTime(this.frame);
        }
  
        // Initialize the 3D scene
        await this.$nextTick();
        if (!this.sceneInitializing) {
          this.sceneInitializing = true;
        }
        this.initScene();
  
        // After scene is initialized, create markers and forces if they exist
        if (this.markersDatasets && Object.keys(this.markersDatasets).length > 0) {
          this.createMarkerSpheres();
        }
        if (this.forcesDatasets && Object.keys(this.forcesDatasets).length > 0) {
          this.createForceArrows();
        }
  
        // Start the animation loop for shared visualizations
        this.animate();
  
        // Load 3D models
        let totalModelsToLoad = 0;
        let modelsLoaded = 0;
  
        // Count total models to load
        this.animations.forEach((animation, index) => {
          for (let body in animation.data.bodies) {
            let bd = animation.data.bodies[body];
            totalModelsToLoad += bd.attachedGeometries.length;
          }
        });
  
        console.log(`Total models to load: ${totalModelsToLoad}`);
  
        const checkAllModelsLoaded = () => {
          modelsLoaded++;
          if (modelsLoaded >= totalModelsToLoad) {
            console.log(`[loadSharedVisualization] All models loaded. Ready for animation.`);
            console.log(`[loadSharedVisualization] Current state - Frame: ${this.frame}, Playing: ${this.playing}, Frames length: ${this.frames.length}`);
  
            // Update time to match the current frame now that data is fully loaded
            if (shareData.currentFrame !== undefined) {
              this.updateDisplayedTime(this.frame);
            }
  
            // All models loaded, now animate to current frame
            setTimeout(() => {
              this.animateOneFrame();
              console.log(`[loadSharedVisualization] Initial frame animation complete. Try using play controls or navigating frames.`);
              
              // Restore timelapse meshes if they exist in shared data
              if (shareData.timelapse && shareData.timelapse.enabled && shareData.timelapse.meshes) {
                this.restoreTimelapseFromShare(shareData.timelapse);
              }
            }, 100);
          }
        };
  
        // If no models to load, animate immediately
        if (totalModelsToLoad === 0) {
          // Update time to match the current frame
          if (shareData.currentFrame !== undefined) {
            this.updateDisplayedTime(this.frame);
          }
  
          setTimeout(() => {
            this.animateOneFrame();
            
            // Restore timelapse meshes if they exist in shared data
            if (shareData.timelapse && shareData.timelapse.enabled && shareData.timelapse.meshes) {
              this.restoreTimelapseFromShare(shareData.timelapse);
            }
          }, 100);
        }
  
        this.animations.forEach((animation, index) => {
          for (let body in animation.data.bodies) {
            let bd = animation.data.bodies[body];
            bd.attachedGeometries.forEach((geom) => {
              let path = 'https://mc-opencap-public.s3.us-west-2.amazonaws.com/geometries/' + geom.substr(0, geom.length - 4) + ".obj";
              objLoader.load(path, (root) => {
                root.castShadow = false;
                root.receiveShadow = false;
  
                root.traverse((child) => {
                  if (child instanceof THREE.Mesh) {
                    child.castShadow = false;
                    child.material = new THREE.MeshPhongMaterial({
                      color: this.colors[index],
                      transparent: this.alphaValues[index] < 1.0,
                      opacity: this.alphaValues[index] || 1.0
                    });
                  }
                });
  
                const meshKey = `anim${index}_${body}${geom}`;
                this.meshes[meshKey] = root;
                this.meshes[meshKey].scale.set(bd.scaleFactors[0], bd.scaleFactors[1], bd.scaleFactors[2]);
  
                root.position.add(animation.offset);
                this.scene.add(root);
  
                // Check if all models are loaded
                checkAllModelsLoaded();
              });
            });
          }
        });
  
        // Apply camera position if shared
        if (shareData.camera && this.camera && this.controls) {
          setTimeout(() => {
            if (Array.isArray(shareData.camera)) {
              // New format: [posX, posY, posZ, targetX, targetY, targetZ]
              this.camera.position.set(
                shareData.camera[0],
                shareData.camera[1],
                shareData.camera[2]
              );
  
              this.controls.target.set(
                shareData.camera[3],
                shareData.camera[4],
                shareData.camera[5]
              );
            } else {
              // Old format: {position: {x, y, z}, target: {x, y, z}}
              this.camera.position.set(
                shareData.camera.position.x,
                shareData.camera.position.y,
                shareData.camera.position.z
              );
  
              this.controls.target.set(
                shareData.camera.target.x,
                shareData.camera.target.y,
                shareData.camera.target.z
              );
            }
  
            this.controls.update();
          }, 1000);
        }
  
        console.log('Shared visualization loaded successfully');
        this.loadingSharedSession = false;
  
      } catch (error) {
        console.error('Error loading shared visualization:', error);
        this.$toasted.error('Failed to load shared visualization');
        this.loadingSharedSession = false;
      }
    },
  
    copyToClipboard(text) {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          this.$toasted.success('Share URL copied to clipboard!');
        }).catch(() => {
          this.fallbackCopyToClipboard(text);
        });
      } else {
        this.fallbackCopyToClipboard(text);
      }
    },
  
    fallbackCopyToClipboard(text) {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        this.$toasted.success('Share URL copied to clipboard!');
      } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
        this.$toasted.error('Failed to copy URL to clipboard');
      }
      document.body.removeChild(textArea);
    },
  
    openInNewTab(url) {
      window.open(url, '_blank');
    },
  
    cleanupOldShares() {
      // Clean up old share data from localStorage
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('opencap_share_')) {
          keysToRemove.push(key);
        }
      }
  
      keysToRemove.forEach(key => {
        localStorage.removeItem(key);
      });
  
      console.log(`Cleaned up ${keysToRemove.length} old share entries`);
      this.$toasted.success(`Cleaned up ${keysToRemove.length} old share entries`);
    },
  
    downloadShareFile() {
      try {
        const shareData = this.getShareData();
        const jsonString = JSON.stringify(shareData, null, 2);
  
        // Create blob and download
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
  
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.shareFileName}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
  
        // Clean up the URL
        URL.revokeObjectURL(url);
  
        this.$toasted.success('Share file downloaded successfully!');
      } catch (error) {
        console.error('Error downloading share file:', error);
        this.$toasted.error('Failed to download share file');
      }
    },
    downloadConvertedJson(animationIndex) {
      try {
        const animation = this.animations[animationIndex];
        if (!animation) {
          this.$toasted.error('Animation not found');
          return;
        }
  
        // Get the converted JSON data from the map using the filename
        const convertedJsonData = this.convertedJsonDataMap[animation.fileName];
        if (!convertedJsonData) {
          this.$toasted.error('Converted JSON data not found for this animation');
          return;
        }
  
        // Create JSON string
        const jsonString = JSON.stringify(convertedJsonData, null, 2);
  
        // Create blob and download
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
  
        const link = document.createElement('a');
        link.href = url;
        link.download = animation.fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
  
        // Clean up the URL
        URL.revokeObjectURL(url);
  
        this.$toasted.success('Converted JSON file downloaded successfully!');
      } catch (error) {
        console.error('Error downloading converted JSON file:', error);
        this.$toasted.error('Failed to download converted JSON file');
      }
    },
    async loadTrial() {
      console.log('loadTrial started')
        this.time = "0.000"
  
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
                    rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
                    fileName: 'test.json',
                    trialName: 'Subject 1',
                    calculatedFps: 0, // Add this line
                    visible: true, // Default to visible
                    playable: true // Default to playable
                }
            ]
  
            // Initialize alpha values
            this.initializeAlphaValue(0);
  
            // Add second animation if available
            if (res2 && res2.data) {
                this.animations.push({
                    data: res2.data,
                    offset: new THREE.Vector3(0, 0, -1),
                    rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
                    fileName: 'test2.json',
                    trialName: 'Subject 2',
                    calculatedFps: 0, // Add this line
                    visible: true, // Default to visible
                    playable: true // Default to playable
                });
                this.initializeAlphaValue(1);
            }
  
            // Ensure all color arrays are synchronized
            this.ensureColorArraysSync();
  
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
                      context.fillStyle = this.formatColor(this.colors[index]);
  
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
        if (!this.animateLoopStarted) {
          this.animateLoopStarted = true;
        }
        // Always schedule the next frame first
        requestAnimationFrame(this.animate);

        this.updateVideoPlaneTransform();

        // In live streaming mode, don't advance frames based on our own clock.
        // Just render the current state; frames are driven by incoming WebSocket data.
        if (this.liveMode) {
          if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
          }
          return;
        }

        // If not playing, just render the current state and exit
        if (!this.playing) {
          // Optionally log pause state
          // console.log('[animate] Paused. Rendering static frame.');
          if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
          }
          return;
        }
  
        // --- If playing, continue below ---
        // console.log(`[animate] Playing. Frame: ${this.frame}`);
  
        // Calculate time since last frame
        const currentTime = performance.now();
        let deltaTime = (currentTime - this.lastFrameTime) / 1000; // Convert to seconds
        if (!Number.isFinite(deltaTime) || deltaTime < 0) {
          deltaTime = 0;
        }
        const MAX_FRAME_DELTA = 0.1;
        const clampedDelta = Math.min(deltaTime, MAX_FRAME_DELTA);
        this.lastFrameTime = currentTime;
        const effectiveFrameRate = Number.isFinite(this.frameRate) && this.frameRate > 0 ? this.frameRate : 60;
        const effectiveSpeed = Number.isFinite(this.playSpeed) && this.playSpeed > 0 ? this.playSpeed : 1;

        // Check if we have markers or animations to animate
        // Refined check for clarity: Checks if any animation is playable OR if markers exist
        const hasAnimatedContent = this.animations.some(a => a.playable !== false) ||
                                 this.smplSequences.some(seq => seq.playable !== false) ||
                                 (this.markerSpheres.length > 0) ||
                                 (Object.keys(this.markersDatasets).length > 0);

        // Note: Debug removed - animation loop should now work for shared visualizations

        let advancedFrame = false;
        if (hasAnimatedContent) {
            this.frameAccumulator += clampedDelta * effectiveFrameRate * effectiveSpeed;
            let framesToAdvance = Math.floor(this.frameAccumulator);
            if (framesToAdvance > 0) {
                const MAX_ADVANCE_PER_TICK = 12;
                if (framesToAdvance > MAX_ADVANCE_PER_TICK) {
                    framesToAdvance = MAX_ADVANCE_PER_TICK;
                }
                this.frameAccumulator -= framesToAdvance;
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
                        this.updateDisplayedTime();
                        this.animateOneFrame(); // Render the final frame
                        this.stopRecording();
                        // Stop playing state is handled by stopRecording
                        return; // Exit this specific animate cycle
                    }
                } else if (nextFrame >= this.frames.length) {
                    // If not recording OR loopCount is Infinite, check playback looping
                    if (this.isLooping) {
                      // Loop back normally using modulo
                      nextFrame = nextFrame % this.frames.length;
  
                    // When looping, also reset video to beginning if present
                    if (this.videoFile && this.videoPreviewElement) {
                      try {
                        console.log('[animate] Looping animation, resetting video to beginning');
                        this.videoPreviewElement.currentTime = 0;
  
                        // Ensure video keeps playing if it was previously playing
                        if (this.playing && this.videoPreviewElement.paused) {
                          const playPromise = this.videoPreviewElement.play();
                          if (playPromise !== undefined) {
                            playPromise.catch(error => {
                              console.log('Video playback error on loop:', error);
                            });
                          }
                        }
                      } catch (error) {
                        console.log('Video reset error on loop:', error);
                      }
                    }
                    } else {
                      // If not looping, stop at the last frame
                      nextFrame = this.frames.length - 1;
                      this.playing = false; // Stop playback
                      console.log('[animate] Reached end and not looping. Setting playing=false.');
                    }
                }
                // If nextFrame < this.frames.length, it's a normal advance.

                // Update the frame *before* updating time and rendering
                this.frame = nextFrame;

                // Update displayed time
                this.updateDisplayedTime();

                // Render the current frame *after* state update
                this.animateOneFrame();

                // If a loop was just completed and we are starting the next one
                if (loopNeedsReset) {
                    // Ensure onNavigate syncs things like video if needed
                    this.onNavigate(this.frame);
                }
  
                // After advancing and rendering, if playing is now false (e.g., reached end), exit loop
                if (!this.playing) {
                    console.log('[animate] Exiting loop after reaching end.');
                    return;
                }
                advancedFrame = true;
            }
        }
        // Render even if not enough time has passed to advance the frame, but still playing
        // This ensures smoother rendering, especially at high frame rates or low play speeds
        if (this.playing && !advancedFrame) {
             if (this.renderer && this.scene && this.camera) {
                // Re-render the *current* frame without advancing
                // We could call animateOneFrame here, but that might be redundant if marker/model updates are heavy.
                // A simple render might suffice.
                this.renderer.render(this.scene, this.camera);
             }
        }
      },
      animateOneFrame() {
        let cframe = this.frame;
  
        if (cframe < this.frames.length) {
          // Update each animation
          this.animations.forEach((animation, animIndex) => {
            // Skip animation updates if not playable, but still keep visible
            if (!animation.playable) return;
  
            let json = animation.data;
            const speedMultiplier = animation.speedMultiplier || 1.0;
            // Calculate the frame index for this animation based on speed multiplier
            const animFrame = speedMultiplier !== 1.0 
              ? Math.floor(cframe * speedMultiplier) % this.frames.length
              : cframe;
            for (let body in json.bodies) {
              json.bodies[body].attachedGeometries.forEach((geom) => {
                const meshKey = `anim${animIndex}_${body}${geom}`;
                if (this.meshes[meshKey]) {
                  // Check if translation data exists for this frame
                  if (!json.bodies[body].translation || !json.bodies[body].translation[animFrame]) {
                    console.error(`[animateOneFrame] Missing translation data for body ${body} frame ${animFrame}`);
                    return; // Skip this geometry
                  }
  
                  // Get base position from animation data
                  const basePosition = new THREE.Vector3(
                    json.bodies[body].translation[animFrame][0],
                    json.bodies[body].translation[animFrame][1],
                    json.bodies[body].translation[animFrame][2]
                  );
  
                  // Apply animation rotation if it exists
                  let finalPosition = basePosition.clone();
                  if (animation.rotation) {
                    const animQuaternion = new THREE.Quaternion().setFromEuler(animation.rotation);
                    finalPosition.applyQuaternion(animQuaternion);
                  }
  
                  // Add animation offset after rotation
                  finalPosition.add(animation.offset);
  
                  // Set final position
                  this.meshes[meshKey].position.copy(finalPosition);
  
                  // Check if rotation data exists for this frame
                  if (!json.bodies[body].rotation || !json.bodies[body].rotation[animFrame]) {
                    console.error(`[animateOneFrame] Missing rotation data for body ${body} frame ${animFrame}`);
                    return; // Skip this geometry
                  }
  
                  // Get base rotation
                  var baseEuler = new THREE.Euler(
                    json.bodies[body].rotation[animFrame][0],
                    json.bodies[body].rotation[animFrame][1],
                    json.bodies[body].rotation[animFrame][2]
                  );
                  
                  // Apply animation rotation if it exists
                  if (animation.rotation) {
                    const baseQuaternion = new THREE.Quaternion().setFromEuler(baseEuler);
                    const animQuaternion = new THREE.Quaternion().setFromEuler(animation.rotation);
                    const finalQuaternion = animQuaternion.multiply(baseQuaternion);
                    this.meshes[meshKey].quaternion.copy(finalQuaternion);
                  } else {
                    this.meshes[meshKey].quaternion.setFromEuler(baseEuler);
                  }
  
                  // Handle timelapse if enabled
                  if (this.timelapseMode && this.playing && animFrame % this.timelapseInterval === 0) {
                    const scale = new THREE.Vector3(
                      json.bodies[body].scaleFactors[0],
                      json.bodies[body].scaleFactors[1],
                      json.bodies[body].scaleFactors[2]
                    );
                    this.createTimelapseMesh(
                      animIndex,
                      body,
                      geom,
                      finalPosition.clone(),
                      this.meshes[meshKey].quaternion.clone(),
                      scale
                    );
                  }
                }
              });
            }
          });
  
          // Update SMPL sequences
          this.smplSequences.forEach((sequence) => {
            if (!sequence.mesh) return;
            const maxFrame = Math.max(sequence.frameCount - 1, 0);
            const speedMultiplier = sequence.speedMultiplier || 1.0;
            
            // Calculate the frame based on speed multiplier
            let scaledFrame = cframe;
            if (speedMultiplier !== 1.0 && sequence.playable !== false) {
              scaledFrame = Math.floor(cframe * speedMultiplier) % (maxFrame + 1);
            }
            
            const desiredFrame = sequence.playable !== false
              ? Math.min(scaledFrame, maxFrame)
              : (sequence.lastRenderedFrame >= 0 ? sequence.lastRenderedFrame : Math.min(scaledFrame, maxFrame));
            const forceUpdate = sequence.playable === false && sequence.lastRenderedFrame < 0;
            this.updateSmplSequenceFrame(sequence, desiredFrame, forceUpdate);
          });
  
          // Render the scene (moved before marker update)
          if (this.renderer && this.scene && this.camera) {
            this.updateVideoPlaneTransform();
            this.renderer.render(this.scene, this.camera);
          }
  
          // Handle markers separately based on markersPlayable flag
          // Update marker positions if markers are loaded
          if (this.markerSpheres.length > 0 && this.showMarkers) {
            this.updateMarkerPositions();
          }
  
          // Update force arrows
          if (Object.keys(this.forcesDatasets).length > 0 && this.showForces) {
            this.updateForceArrows(cframe);
          }

          // Render the scene again after force updates
          if (this.renderer && this.scene && this.camera) {
            this.updateVideoPlaneTransform();
            this.renderer.render(this.scene, this.camera);
          }
        } else {
            // If frame is out of bounds, still render the scene
            if (this.renderer && this.scene && this.camera) {
              this.updateVideoPlaneTransform();
              this.renderer.render(this.scene, this.camera);
            }
        }
  
        // Update real-time plot if enabled
        if (this.showPlottingDialog && this.plotUpdatesEnabled) {
          this.updatePlotInRealTime();
        }
        this.drawProjectedSkeleton();
      },
  
  
    togglePlay(value) {
        // Determine the new playing state
        const newPlayingState = value !== undefined ? value : !this.playing;
  
        // Log the intended change
        console.log(`[togglePlay] Attempting to set playing state to: ${newPlayingState}`);
  
        // Special handling for pause during recording if needed (currently just pauses)
        if (!newPlayingState && this.isRecording) {
             console.log('[togglePlay] Pause requested during recording. Stopping visual playback.');
             // Note: Recording continues until explicitly stopped by stopRecording()
        }
  
        // Set the playing state
        this.playing = newPlayingState;
        console.log(`[togglePlay] Actual playing state set to: ${this.playing}`);

        if (this.playing) {
          if (this.liveMode) {
            // In live mode, jump to the latest streamed frame when resuming
            if (this.liveAnimationIndex !== null) {
              const anim = this.animations[this.liveAnimationIndex];
              if (anim && Array.isArray(anim.data.time) && anim.data.time.length > 0) {
                this.frames = anim.data.time;
                this.frame = this.frames.length - 1;
                this.updateDisplayedTime();
              }
            }
            // Render the current frame without resetting internal timing (handled by streamer)
            this.animateOneFrame();
          } else {
            // Normal playback: reset timing references when starting
            this.lastFrameTime = performance.now();
            this.frameAccumulator = 0;
            this.updateDisplayedTime();
            // Make sure first frame gets displayed immediately if starting from pause
            this.animateOneFrame();
          }
        }
        // No specific 'else' action needed here for pause, the animate loop handles it.
  
        // Video sync logic
        if (this.videoFile && this.videoPreviewElement) {
          try {
            // Set video playback rate to match current playSpeed
            if (typeof this.videoPreviewElement.playbackRate !== 'undefined') {
              this.videoPreviewElement.playbackRate = this.playSpeed;
            }
            
            if (this.playing) {
              const playPromise = this.videoPreviewElement.play();
              if (playPromise !== undefined) {
                playPromise.catch(error => {
                  console.log('Video playback error:', error);
                  // Don't throw the error, just log it
                });
              }
            } else {
              this.videoPreviewElement.pause();
            }
          } catch (error) {
            console.log('Video control error:', error);
          }
        }
  
        // Send play/pause state to parent window if running in an iframe
        if (window.parent && window.parent !== window) {
          try {
            window.parent.postMessage({ type: 'playbackState', isPlaying: this.playing }, '*');
          } catch (error) {
            console.error('Error sending message to parent:', error);
          }
        }
      },
      onNavigate(frame) {
        // Update frame and time
        const framesLength = Array.isArray(this.frames) ? this.frames.length : 0;
        if (framesLength > 0) {
          const clamped = Math.min(Math.max(Math.round(frame), 0), framesLength - 1);
          this.frame = clamped;
          this.updateDisplayedTime(clamped);
        } else {
          this.frame = Math.max(Math.round(frame), 0);
          this.updateDisplayedTime(this.frame);
        }
        this.frameAccumulator = 0;

        // Render the frame without advancing
        this.animateOneFrame();

        // Sync video playback position with proper error handling
        if (this.videoFile && this.videoPreviewElement) {
          try {
          // Temporarily remove the timeupdate listener to prevent feedback loops
          const videoElement = this.videoPreviewElement;
          const originalHandler = videoElement.ontimeupdate;
          videoElement.ontimeupdate = null;
  
          // Set the video time directly from the animation time when available
          if (this.frames[frame] !== undefined) {
            // Use the actual time value from the animation data if available
            videoElement.currentTime = parseFloat(this.frames[frame]);
          } else {
            // Fall back to calculating based on frame position
            const totalFrames = this.frames.length - 1;
            const videoTimePosition = (frame / totalFrames) * this.videoDuration;
            videoElement.currentTime = videoTimePosition;
          }
  
          // Restore the timeupdate handler after a short delay
          setTimeout(() => {
            videoElement.ontimeupdate = originalHandler;
          }, 100);
          } catch (error) {
            console.log('Video sync error:', error);
          }
        }
      },
    syncVideoToFrame(frame, forceSync = false) {
      // Sync video playback position to match the given frame
      if (this.videoFile && this.videoPreviewElement) {
        try {
          const videoElement = this.videoPreviewElement;
          
          // Set the video time directly from the animation time when available
          if (this.frames[frame] !== undefined) {
            // Use the actual time value from the animation data if available
            videoElement.currentTime = parseFloat(this.frames[frame]);
          } else if (this.videoDuration > 0 && this.frames.length > 0) {
            // Fall back to calculating based on frame position
            const totalFrames = this.frames.length - 1;
            const videoTimePosition = (frame / totalFrames) * this.videoDuration;
            videoElement.currentTime = videoTimePosition;
          }
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
    debouncedUpdateOffset(animationIndex, axis, value) {
        // Clear any existing timer for this combination
        const timerKey = `${animationIndex}_${axis}`;
        if (this.offsetUpdateTimers[timerKey]) {
            clearTimeout(this.offsetUpdateTimers[timerKey]);
        }
  
        // Set a new timer to update after 150ms of no changes
        this.offsetUpdateTimers[timerKey] = setTimeout(() => {
            this.updateOffset(animationIndex, axis, value);
            delete this.offsetUpdateTimers[timerKey];
        }, 150);
    },
  
    updateAnimationRotation(animationIndex, axis, value) {
        // Get the animation
        const animation = this.animations[animationIndex];
        if (!animation) return;
  
        // Initialize rotation if it doesn't exist
        if (!animation.rotation) {
            this.$set(animation, 'rotation', new THREE.Euler(0, 0, 0, 'XYZ'));
        }
  
        // Convert degrees to radians
        const radians = THREE.Math.degToRad(Number(value));
        
        // Update the rotation value
        animation.rotation[axis] = radians;
  
        // Update all meshes for this animation
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${animationIndex}_`)) {
                const mesh = this.meshes[key];
                const body = key.split('_')[1].split('.')[0]; // Extract body name from key
  
                // Get current frame's base position and rotation
                if (animation.data.bodies[body] &&
                    animation.data.bodies[body].translation &&
                    animation.data.bodies[body].translation[this.frame] &&
                    animation.data.bodies[body].rotation &&
                    animation.data.bodies[body].rotation[this.frame]) {
  
                    // Get base position and rotation
                    const basePosition = new THREE.Vector3(
                        animation.data.bodies[body].translation[this.frame][0],
                        animation.data.bodies[body].translation[this.frame][1],
                        animation.data.bodies[body].translation[this.frame][2]
                    );
  
                    const baseRotation = new THREE.Euler(
                        animation.data.bodies[body].rotation[this.frame][0],
                        animation.data.bodies[body].rotation[this.frame][1],
                        animation.data.bodies[body].rotation[this.frame][2],
                        'XYZ'
                    );
  
                    // Apply animation rotation first, then translate
                    // Create a quaternion from the animation rotation
                    const animQuaternion = new THREE.Quaternion().setFromEuler(animation.rotation);
                    
                    // Rotate the position around origin
                    const rotatedPosition = basePosition.clone().applyQuaternion(animQuaternion);
                    
                    // Add the offset after rotation
                    rotatedPosition.add(animation.offset);
                    
                    // Set the mesh position
                    mesh.position.copy(rotatedPosition);
  
                    // Combine rotations: base rotation + animation rotation
                    const baseQuaternion = new THREE.Quaternion().setFromEuler(baseRotation);
                    const finalQuaternion = animQuaternion.multiply(baseQuaternion);
                    mesh.quaternion.copy(finalQuaternion);
                }
            }
        });
  
        // Update text sprites for this animation
        const textSprite = this.textSprites[`text_${animationIndex}`];
        if (textSprite) {
            // For text sprite, just apply the offset and rotation to its position
            const spriteBasePos = animation.offset.clone();
            spriteBasePos.y += 2; // Position above the model
            
            // Rotate the sprite position
            const animQuaternion = new THREE.Quaternion().setFromEuler(animation.rotation);
            spriteBasePos.applyQuaternion(animQuaternion);
            
            textSprite.position.copy(spriteBasePos);
        }
  
        // Render the scene with updated rotations
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
            this.animateOneFrame();
        }
    },
  
    debouncedUpdateAnimationRotation(animationIndex, axis, value) {
        // Clear any existing timer for this combination
        const timerKey = `${animationIndex}_${axis}`;
        if (this.rotationUpdateTimers[timerKey]) {
            clearTimeout(this.rotationUpdateTimers[timerKey]);
        }
  
        // Set a new timer to update after 150ms of no changes
        this.rotationUpdateTimers[timerKey] = setTimeout(() => {
            this.updateAnimationRotation(animationIndex, axis, value);
            delete this.rotationUpdateTimers[timerKey];
        }, 150);
    },
  
    openRotationDialog(index) {
        this.$set(this.rotationDialogs, index, true);
    },
  
    resetAnimationRotation(index) {
        const animation = this.animations[index];
        if (!animation) return;
  
        // Reset rotation to zero
        if (animation.rotation) {
            animation.rotation.set(0, 0, 0);
        }
  
        // Update all three axes
        this.updateAnimationRotation(index, 'x', 0);
        this.updateAnimationRotation(index, 'y', 0);
        this.updateAnimationRotation(index, 'z', 0);
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
  
    // Check which codecs are supported
    const supportedMimeTypes = [
      'video/webm;codecs=vp9',
      'video/webm;codecs=vp8',
      'video/webm',
      'video/mp4;codecs=h264',
      'video/mp4'
    ];
  
    const checkMimeType = (type) => {
      try {
        return MediaRecorder.isTypeSupported(type);
      } catch (e) {
        return false;
      }
    };
  
    // Determine best format based on user selection
      if (this.recordingFormat === 'mp4') {
      // For MP4, try to use H.264 codec (most compatible)
      if (checkMimeType('video/mp4;codecs=h264')) {
        mimeType = 'video/mp4;codecs=h264';
      fileExtension = '.mp4';
      } else {
      // Fallback to WebM if MP4 with H.264 isn't supported (better compatibility)
      console.warn('MP4 with H.264 not supported by browser, using WebM for better compatibility');
        this.recordingFormat = 'webm';
      if (checkMimeType('video/webm;codecs=vp8')) {
        mimeType = 'video/webm;codecs=vp8';
      } else {
        mimeType = supportedMimeTypes.find(checkMimeType) || 'video/webm';
      }
      fileExtension = '.webm';
    }
      } else {
      // For WebM
      if (checkMimeType('video/webm;codecs=vp8')) {
        // VP8 is more widely compatible than VP9
        mimeType = 'video/webm;codecs=vp8';
      } else if (checkMimeType('video/webm')) {
        mimeType = 'video/webm';
      } else {
        mimeType = supportedMimeTypes.find(checkMimeType) || 'video/webm';
      }
        fileExtension = '.webm';
      }
  
    console.log(`Using format: ${mimeType}`);
  
      // Update the file name based on the selected format
    this.recordingFileName = `opencap-recording${fileExtension}`;
  
    // Try to create MediaRecorder with selected format
      try {
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: mimeType,
          videoBitsPerSecond: this.videoBitrate
        });
  
      console.log(`MediaRecorder created with: ${mimeType}, bitrate: ${this.videoBitrate}`);
      } catch (error) {
    console.warn(`Failed to create MediaRecorder with ${mimeType}, trying WebM fallback`, error);
  
    // Fallback to WebM if MP4 fails
    if (this.recordingFormat === 'mp4') {
      console.log('MP4 recording failed, falling back to WebM for compatibility');
      this.recordingFormat = 'webm';
      const webmMimeType = checkMimeType('video/webm;codecs=vp8') ? 'video/webm;codecs=vp8' : 'video/webm';
      
      try {
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: webmMimeType,
          videoBitsPerSecond: this.videoBitrate
        });
        console.log(`MediaRecorder created with WebM fallback: ${webmMimeType}`);
      } catch (webmError) {
        console.error('WebM fallback also failed', webmError);
        alert('Recording is not supported in your browser');
        return;
      }
    } else {
      console.error('Failed to create MediaRecorder', error);
        alert('Recording is not supported in your browser');
        return;
      }
      }
  
      this.recordedChunks = [];
      // Only reset currentLoop if not in infinite mode
      if (this.loopCount !== Infinity) {
        this.currentLoop = 1;
      } else {
        this.currentLoop = 0; // Keep it 0 for infinite
      }
  
    // Request data frequently to ensure better quality
      this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };
  
      this.mediaRecorder.onstop = () => {
      console.log(`Recording stopped. ${this.recordedChunks.length} chunks captured.`);
  
      if (this.recordedChunks.length === 0) {
        console.error('No data was recorded');
        alert('Failed to record video. Try using a different format or browser.');
        this.isRecording = false;
        return;
      }
  
      // Explicitly specify the MIME type when creating the blob
      const finalMimeType = this.mediaRecorder.mimeType || (this.recordingFormat === 'mp4' ? 'video/mp4' : 'video/webm');
  
      const options = {
        type: finalMimeType
      };
  
      console.log(`Creating blob with type: ${finalMimeType}`);
      const blob = new Blob(this.recordedChunks, options);
        const url = URL.createObjectURL(blob);
  
      // Check if we're in headless mode
      const isHeadless = this.$route.query.headless === 'true';
  
      if (isHeadless && typeof window.finishedRecording === 'function') {
        // For headless mode, pass the URL to the Node.js process
        console.log('[Headless] Recording finished, notifying Node.js process');
        window.finishedRecording(url);
      } else {
        // Normal download in browser
        const a = document.createElement('a');
        document.body.appendChild(a);
        a.style = 'display: none';
        a.href = url;
        a.download = this.recordingFileName;
        a.click();
  
        // Clean up
        setTimeout(() => {
          document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        }, 100);
      }
  
        this.recordedChunks = [];
        this.currentLoop = 0;
      };
  
    // Start recording with timeslices based on frame rate for smooth capture
    // This ensures data is captured at the right intervals for smooth video
    const timeslice = Math.round(1000 / this.frameRate); // e.g., ~33ms for 30fps
    this.mediaRecorder.start(timeslice); // Capture at frame rate intervals
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
  
    async handleFileUpload(event) {
        const files = event.target.files;
        if (!files.length) return;
  
        try {
            if (!this.scene && !this.sceneInitializing) {
                this.sceneInitializing = true;
                await this.$nextTick();
                this.initScene();
            }
  
            const filePromises = Array.from(files).map(file => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            const data = JSON.parse(e.target.result);
                            resolve({ data, file });
                        } catch (error) {
                            reject({ error, file });
                        }
                    };
                    reader.readAsText(file);
                });
            });
  
            const results = await Promise.allSettled(filePromises);
  
            const successfulResults = results
                .filter(result => result.status === 'fulfilled')
                .map(result => result.value);
  
            const errors = results.filter(result => result.status === 'rejected');
            errors.forEach(error => {
                console.error('Error loading file:', error.reason);
                this.$toasted.error(`Error loading file: ${error.reason.file.name}`);
            });
  
            if (successfulResults.length === 0) {
                this.$toasted.error('No valid files could be loaded');
                return;
            }
  
            const shareFiles = successfulResults.filter(({ data }) =>
                (data && data.animations && Array.isArray(data.animations)) ||
                (data && data.smplSequences && Array.isArray(data.smplSequences))
            );
  
            if (shareFiles.length > 0) {
                const shareData = shareFiles[0].data;
                this.loadSharedVisualization(shareData);
                this.$toasted.success('Share file loaded successfully!');
                return;
            }
  
            const animationPayloads = [];
            const smplPayloads = [];
  
            successfulResults.forEach(({ data, file }) => {
                const offset = new THREE.Vector3(0, 0, 0);
                const fileFps = this.calculateFrameRate(data.time);
  
                if (data && data.vertices && data.frame_count) {
                    smplPayloads.push({ data, file });
                    return;
                }
  
                const newAnimIndex = this.animations.length;
                this.animations.push({
                    data: data,
                    offset: offset,
                    rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
                    fileName: file.name,
                    trialName: `Subject ${newAnimIndex + 1}`,
                    visible: true,
                    playable: true,
                    calculatedFps: fileFps,
                    speedMultiplier: 1.0
                });
  
                if (this.animations.length === 1) {
                    this.frames = data.time;
                    this.trial = { results: [] };
                    this.frameRate = fileFps;
                    this.frame = 0;
                    if (Array.isArray(data.time) && data.time.length > 0) {
                        this.updateDisplayedTime(0);
                    } else {
                        this.time = "0.000";
                    }
                }
  
                this.initializeAlphaValue(newAnimIndex);
                this.extractMarkerDataFromJson(data, newAnimIndex, file.name);
  
                animationPayloads.push({ data, animIndex: newAnimIndex });
            });
  
            if (smplPayloads.length > 0) {
                const sceneReady = await this.ensureSceneReady();
                if (!sceneReady) {
                    this.$toasted.error('Unable to initialize viewer for SMPL data.');
                    return;
                }
  
                // First, load the example JSON file to initialize the scene correctly
                try {
                    console.log('Loading example mocap file to initialize scene...');
                    const exampleResponse = await fetch('/samples/squat/sample_mocap.json');
                    const exampleData = await exampleResponse.json();
                    
                    // Add the example data as a temporary animation to initialize the scene
                    const tempAnimIndex = this.animations.length;
                    const fileFps = this.calculateFrameRate(exampleData.time);
                    
                    this.animations.push({
                        data: exampleData,
                        offset: new THREE.Vector3(0, 0, 0),
                        rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
                        fileName: 'temp_example.json',
                        trialName: 'Temp Subject',
                        visible: true,
                        playable: true,
                        calculatedFps: fileFps
                    });
                    
                    if (this.animations.length === 1) {
                        this.frames = exampleData.time;
                        this.trial = { results: [] };
                        this.frameRate = fileFps;
                        this.frame = 0;
                        if (Array.isArray(exampleData.time) && exampleData.time.length > 0) {
                            this.updateDisplayedTime(0);
                        } else {
                            this.time = "0.000";
                        }
                    }
                    
                    // Initialize and extract marker data to properly set up the scene
                    this.initializeAlphaValue(tempAnimIndex);
                    this.extractMarkerDataFromJson(exampleData, tempAnimIndex, 'temp_example.json');
                    
                    // Wait a moment for initialization, then remove the temporary animation
                    await new Promise(resolve => setTimeout(resolve, 100));
                    
                    // Remove the temporary example animation
                    this.animations.splice(tempAnimIndex, 1);
                    this.meshes = {}; // Clear meshes to start fresh
                    
                    console.log('Example file loaded and removed, scene initialized');
                } catch (error) {
                    console.error('Error loading example file:', error);
                }
  
                // Now load the actual SMPL files
                for (const { data, file } of smplPayloads) {
                    try {
                        await this.addSmplSequence(data, file.name);
                        this.$toasted.success(`SMPL file loaded: ${file.name}`);
                    } catch (error) {
                        console.error('Error adding SMPL sequence:', error);
                        this.$toasted.error(`Failed to load SMPL file: ${file.name}`);
                    }
                }
            }
  
            this.ensureColorArraysSync();
  
            let geometriesLoaded = 0;
            const totalGeometries = animationPayloads.reduce((total, { data }) => {
                return total + Object.values(data.bodies || {}).reduce((sum, body) =>
                    sum + body.attachedGeometries.length, 0);
            }, 0);
  
            let loadsFinalized = false;
            const finalizeLoads = () => {
                if (loadsFinalized) return;
                loadsFinalized = true;
  
                if (this.syncMode !== 'none') {
                    this.applySyncMode();
                } else if (this.animations.length > 1) {
                    this.syncAllAnimations();
                }
  
                if (this.frames && this.frames.length > 0 && this.frameRate > 0) {
                    this.animationDurationInSeconds = (this.frames.length - 1) / this.frameRate;
                }
  
                this.animate();
                this.frame = 0;
                this.animateOneFrame();
                if (!this.playing) {
                    this.togglePlay(true);
                }
                window.allVisualsLoaded = true;
            };
  
            if (animationPayloads.length > 0) {
                const sceneReady = await this.ensureSceneReady();
                if (!sceneReady) {
                    this.$toasted.error('Unable to initialize viewer for animation data.');
                    return;
                }
  
                animationPayloads.forEach(({ data, animIndex }) => {
                    for (let body in data.bodies) {
                        let bd = data.bodies[body];
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
                                            transparent: false,
                                            opacity: 1.0
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
                                const animation = this.animations[animIndex];
                                if (animation && animation.offset) {
                                    root.position.add(animation.offset);
                                }
                                this.scene.add(root);
  
                                geometriesLoaded++;
                                if (geometriesLoaded === totalGeometries) {
                                    finalizeLoads();
                                }
                            });
                        });
                    }
                });
            }
  
            if (totalGeometries === 0) {
                finalizeLoads();
            }
        } finally {
            event.target.value = '';
        }
    },
    initScene(retryCount = 0) {
        // console.log('initScene called', retryCount > 0 ? `(retry ${retryCount})` : '');
        
        // Set the flag if not already set (allow external setting)
        if (retryCount === 0 && !this.sceneInitializing) {
          this.sceneInitializing = true;
        }
        
        // Check if scene already exists
        if (this.scene) {
          console.log('Scene already exists, skipping initialization');
          this.sceneInitializing = false;
          return;
        }
        
        // Check if component is mounted and DOM is ready
        const domReady = document.readyState === 'complete' || document.readyState === 'interactive';
        if (!this.$el || !domReady) {
          // console.log('Component not mounted or DOM not ready, retrying...');
          if (retryCount < 10) {
            this.$nextTick(() => {
              this.initScene(retryCount + 1);
            });
          } else {
            console.error('Failed to initialize scene after 10 retries - component not mounted');
            this.sceneInitializing = false;
          }
          return;
        }
        
        const container = this.$refs.mocap;
        if (!container) {
          console.error('Container not found in initScene');
          console.log('Available refs:', Object.keys(this.$refs));
          console.log('DOM ready?', document.readyState);
          console.log('Component mounted?', !!this.$el);
          console.log('Trial:', !!this.trial);
          console.log('Animations:', this.animations.length);
          console.log('MarkerSpheres:', this.markerSpheres.length);
          console.log('TrialLoading:', this.trialLoading);
          console.log('Converting:', this.converting);
  
          // Always retry in the next tick if container is not found (max 10 retries)
          if (retryCount < 10) {
            // console.log('Retrying initScene in next tick...');
            this.$nextTick(() => {
              this.initScene(retryCount + 1);
            });
          } else {
            console.error('Failed to initialize scene after 10 retries');
            this.sceneInitializing = false;
          }
          return;
        }
  
        let ratio = container.clientWidth / container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(35, ratio, 0.1, 125);
        this.camera.position.x = 3.33;
        this.camera.position.z = -2.30;
        this.camera.position.y = 3.5;
        this.camera.lookAt(0, 1, 0);
  
        this.scene = new THREE.Scene();
        // console.log('Scene and camera initialized');
  
        // Re-add existing SMPL meshes if reinitializing the scene
        if (this.smplSequences.length > 0) {
          this.smplSequences.forEach(sequence => {
            if (sequence.mesh && !this.scene.children.includes(sequence.mesh)) {
              sequence.mesh.visible = sequence.visible;
              this.scene.add(sequence.mesh);
            }
            if (sequence.skeleton && !this.scene.children.includes(sequence.skeleton)) {
              sequence.skeleton.visible = sequence.visible && sequence.showSkeleton;
              this.scene.add(sequence.skeleton);
            }
          });
        }
  
        // Create group for axes objects
        this.axesGroup = new THREE.Group();
        // Add thick coordinate axes
        const axesSize = 0.25; // Size of the axes lines
        const lineThickness = 3; // Thickness of the lines
        const resolution = new THREE.Vector2(container.clientWidth, container.clientHeight);
  
        // X Axis (Red)
        const pointsX = [0, 0.01, 0, axesSize, 0.01, 0]; // Added small Y offset
        const geometryX = new LineGeometry();
        geometryX.setPositions(pointsX);
        const materialX = new LineMaterial({
            color: 0xff0000, // Red
            linewidth: lineThickness,
            resolution: resolution,
            dashed: false,
        });
        const lineX = new Line2(geometryX, materialX);
        this.axesGroup.add(lineX);
  
        // Y Axis (Green)
        const pointsY = [0, 0.01, 0, 0, axesSize, 0];
        const geometryY = new LineGeometry();
        geometryY.setPositions(pointsY);
        const materialY = new LineMaterial({
            color: 0x00ff00, // Green
            linewidth: lineThickness,
            resolution: resolution,
            dashed: false,
        });
        const lineY = new Line2(geometryY, materialY);
        this.axesGroup.add(lineY);
  
        // Z Axis (Blue)
        const pointsZ = [0, 0.01, 0, 0, 0.01, axesSize]; // Added small Y offset
        const geometryZ = new LineGeometry();
        geometryZ.setPositions(pointsZ);
        const materialZ = new LineMaterial({
            color: 0x0000ff, // Blue
            linewidth: lineThickness,
            resolution: resolution,
            dashed: false,
        });
        const lineZ = new Line2(geometryZ, materialZ);
        this.axesGroup.add(lineZ);
  
        // Helper function to create axis labels
        const createAxisLabel = (text, color, position) => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            const fontSize = 24; // Reduced font size
            context.font = `Bold ${fontSize}px Arial`;
            const textWidth = context.measureText(text).width;
  
            // Adjust canvas size dynamically based on text width
            canvas.width = textWidth + 10; // Add some padding
            canvas.height = fontSize + 10; // Add some padding
  
            // Re-apply font settings after resizing
            context.font = `Bold ${fontSize}px Arial`;
            context.fillStyle = color;
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(text, canvas.width / 2, canvas.height / 2);
  
            const texture = new THREE.CanvasTexture(canvas);
            const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
            const sprite = new THREE.Sprite(material);
  
            // Scale the sprite - adjust as needed for visibility
            const scale = 0.15;
            sprite.scale.set(scale * (canvas.width / canvas.height), scale, scale);
  
            sprite.position.copy(position);
            this.axesGroup.add(sprite);
        };
  
        // Position labels slightly offset from the axis ends
        const labelOffset = 0.05; // Adjust offset as needed
        const labelYOffset = 0.01; // Match the line offset
        const labelGroundClearance = 0.02; // Extra offset for labels above ground
  
        createAxisLabel('X', '#ff0000', new THREE.Vector3(axesSize + labelOffset, labelYOffset + labelGroundClearance, 0));
        createAxisLabel('Y', '#00ff00', new THREE.Vector3(0, axesSize + labelYOffset + labelOffset, 0)); // Adjusted Y position for label
        createAxisLabel('Z', '#0000ff', new THREE.Vector3(0, labelYOffset + labelGroundClearance, axesSize + labelOffset));
  
        // Add the axes group to the scene
        this.scene.add(this.axesGroup);
        // Set initial visibility
        this.axesGroup.visible = this.showAxes;
  
        // Set background color from current setting
        // console.log(`[initScene] Setting background color to: ${this.backgroundColor}`);
        this.scene.background = new THREE.Color(this.backgroundColor);
  
        // Configure renderer with current background color and better shadows
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.setClearColor(this.backgroundColor);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;

        this.onResize();
        
        try {
          container.appendChild(this.renderer.domElement);
          // console.log('[initScene] Renderer DOM element appended successfully');
        } catch (error) {
          console.error('[initScene] Error appending renderer to container:', error);
        }
        
        try {
          this.controls = new THREE_OC.OrbitControls(this.camera, this.renderer.domElement);
          // Keep the target centered at head-height but otherwise use default control behavior
          this.controls.target.set(0, 1, 0);
          this.controls.screenSpacePanning = true; // default: pan in screen space for intuitive drag
          this.controls.enableDamping = false; // default behavior (no smoothing) to match previous feel
          this.controls.minDistance = 0; // restore default zoom range
          this.controls.maxDistance = Infinity;
          this.controls.maxPolarAngle = Math.PI; // allow full vertical rotation (default)
          this.controls.update();
          // console.log('[initScene] Orbit controls created successfully');
        } catch (error) {
          console.error('[initScene] Error creating orbit controls:', error);
        }
  
        // Create a much larger plane for "infinite" appearance
        const planeSize = 200; // Make plane much larger for "infinite" appearance
        const loader = new THREE.TextureLoader();
        const texture = loader.load('https://threejsfundamentals.org/threejs/resources/images/checker.png');
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.magFilter = THREE.NearestFilter;
        const repeats = 100; // More repeats for the larger plane
        texture.repeat.set(repeats, repeats);
  
        // Store the texture reference
        this.groundTexture = texture;
  
        // Create a ground plane with fog for distance fading
        const planeGeo = new THREE.PlaneGeometry(planeSize, planeSize);
        // Always use MeshPhongMaterial - lighting mode is controlled by light intensities
        const isTransparent = this.groundOpacity < 1.0;
        const planeMat = new THREE.MeshPhongMaterial({
            map: this.useGroundTexture ? texture : null,
            side: THREE.DoubleSide,
            color: new THREE.Color(this.groundColor),
            opacity: this.groundOpacity,
            transparent: isTransparent,
            depthWrite: !isTransparent // Disable depth write for transparent ground to fix view-angle issues
        });
        const groundMesh = new THREE.Mesh(planeGeo, planeMat);
        groundMesh.rotation.x = Math.PI * -.5;
        groundMesh.position.y = this.groundPositionY;
        groundMesh.receiveShadow = true;
        this.scene.add(groundMesh);
  
        // Store the mesh reference
        this.groundMesh = groundMesh;
  
        // Add fog to create the fading effect at the edges (DISABLED for marker visibility)
        // this.scene.fog = new THREE.FogExp2(this.backgroundColor, 0.025); // Increased density from 0.01 to 0.025
  
        // Add lights with good default settings
        const skyColor = 0xB1E1FF;
        const groundColor = 0xB97A20;
        const hemisphereIntensity = 0.8;
        const hemisphereLight = new THREE.HemisphereLight(skyColor, groundColor, hemisphereIntensity);
        this.scene.add(hemisphereLight);
        this.lights.hemisphere = hemisphereLight;
        this.lights.hemisphereOriginalIntensity = hemisphereIntensity;

        // Main directional light with softer intensity
        const lightIntensity = 0.5;
        const lightColor = 0xFFFFFF;
        const directionalLight = new THREE.DirectionalLight(lightColor, lightIntensity);
        directionalLight.position.set(-10, 10, -10);
        directionalLight.target.position.set(0, 0, 0);
        this.scene.add(directionalLight);
        this.scene.add(directionalLight.target);
        this.lights.directionals = [directionalLight];
        this.lights.directionalOriginalIntensity = lightIntensity;

        // Add spotlight to create the gradient lighting effect around subjects
        const spotLightIntensity = 1;
        const spotLight = new THREE.SpotLight(0xffffff, spotLightIntensity);
        spotLight.position.set(0, 15, 0);
        spotLight.angle = Math.PI / 4;
        spotLight.penumbra = 0.9; // Increased from 0.8 to 0.9 for softer edge
        spotLight.decay = 2.0; // Increased from 1.5 to 2.0 for faster falloff
        spotLight.distance = 30; // Reduced from 40 to 30 for tighter spotlight
        spotLight.castShadow = true;
        spotLight.shadow.mapSize.width = 1024;
        spotLight.shadow.mapSize.height = 1024;
        spotLight.shadow.bias = -0.0001;
        this.scene.add(spotLight);
        this.lights.spotlight = spotLight;
        this.lights.spotlightOriginalIntensity = spotLightIntensity;

        // Create an ambient light with higher intensity for better marker visibility
        const ambientIntensity = 0.6;
        const ambientLight = new THREE.AmbientLight(0x404040, ambientIntensity);
        this.scene.add(ambientLight);
        this.lights.ambient = ambientLight;
        this.lights.ambientOriginalIntensity = ambientIntensity;
  
        // Initial render
        try {
          this.renderer.render(this.scene, this.camera);
          // console.log('[initScene] Initial render completed successfully');
        } catch (error) {
          console.error('[initScene] Error during initial render:', error);
        }
  
        // Apply loaded settings after scene initialization
        // console.log('[initScene] Calling applyLoadedSceneSettings() at the end of initScene.');
        this.applyLoadedSceneSettings();
        
        // Reset initialization flag
        this.sceneInitializing = false;
        
        // console.log('[initScene] Scene initialization completed successfully:', {
        //   scene: !!this.scene,
        //   renderer: !!this.renderer,
        //   camera: !!this.camera,
        //   container: !!this.$refs.mocap
        // });
    },
    async ensureSceneReady(maxAttempts = 40) {
        if (this.scene && this.renderer && this.camera && this.$refs.mocap) {
          return true;
        }
  
        if (!this.scene && !this.sceneInitializing) {
          this.sceneInitializing = true;
          await this.$nextTick();
          this.initScene();
        }
  
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 25));
  
          if (this.scene && this.renderer && this.camera && this.$refs.mocap) {
            return true;
          }
  
          if (!this.scene && !this.sceneInitializing) {
            this.sceneInitializing = true;
            await this.$nextTick();
            this.initScene();
          }
        }
  
        console.error('[ensureSceneReady] Unable to initialize scene within allotted attempts');
        return false;
    },
    onChangeTime(time) {
        const numericTime = Number(time);
        if (!Number.isFinite(numericTime)) {
          return;
        }
        if (Number.isFinite(this.frameRate) && this.frameRate > 0) {
          const framesLength = Array.isArray(this.frames) ? this.frames.length : 0;
          const targetFrame = Math.round(numericTime * this.frameRate);
          if (framesLength > 0) {
            this.frame = Math.min(Math.max(targetFrame, 0), framesLength - 1);
          } else {
            this.frame = Math.max(targetFrame, 0);
          }
        } else {
          this.frame = Math.max(Math.round(numericTime * 60), 0);
        }
        this.frameAccumulator = 0;
        this.updateDisplayedTime();
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
            this.syncMarkerDataToTimeline(this.markerTimeData.times);
        }
  
        // Update frames array to match the new common time array
        this.frames = commonTimeArray;
        this.frame = 0;
        if (this.frames.length > 0) {
            this.updateDisplayedTime(0);
        } else {
            this.time = '0.000';
        }
  
        // Update frame rate based on new time steps
        this.frameRate = this.calculateFrameRate(commonTimeArray);

        // Update the view
        this.animateOneFrame();
    },
    applySyncMode() {
      if (this.syncMode === 'time') {
        this.alignTimeBased();
      } else if (this.syncMode === 'frame') {
        this.alignByReferenceFrame(this.syncReferenceFrame);
      }
    },
    getPrimaryTimeArray() {
      if (this.animations.length > 0 && Array.isArray(this.animations[0].data?.time)) {
        return this.animations[0].data.time;
      }
      if (this.smplSequences.length > 0 && Array.isArray(this.smplSequences[0].time)) {
        return this.smplSequences[0].time;
      }
      return Array.isArray(this.frames) ? this.frames : [];
    },
    alignTimeBased() {
      const shiftByFirst = (timeArray) => {
        if (!Array.isArray(timeArray) || timeArray.length === 0) {
          return timeArray;
        }
        const start = Number(timeArray[0]);
        if (!Number.isFinite(start)) {
          return timeArray;
        }
        return timeArray.map(value => parseFloat((value - start).toFixed(6)));
      };

      this.animations.forEach(animation => {
        if (Array.isArray(animation.data?.time)) {
          animation.data.time = shiftByFirst(animation.data.time);
        }
      });

      this.smplSequences.forEach(sequence => {
        if (Array.isArray(sequence.time)) {
          sequence.time = shiftByFirst(sequence.time);
        }
      });

      const primaryTime = this.getPrimaryTimeArray();
      if (primaryTime.length > 0) {
        this.frames = [...primaryTime];
      }

      if (this.frames.length > 1) {
        this.frameRate = this.calculateFrameRate(this.frames);
      }
      this.frame = Math.min(this.frame, Math.max(this.frames.length - 1, 0));
      this.updateDisplayedTime();
      this.animateOneFrame();
      this.drawProjectedSkeleton();
      this.syncVideoToFrame(this.frame, true);
    },
    alignByReferenceFrame(referenceFrame) {
      if (!Array.isArray(this.frames) || this.frames.length === 0) {
        return;
      }
      const refFrame = Math.max(0, Math.min(this.maxFrameIndex, Math.round(referenceFrame)));
      const shiftByReference = (timeArray) => {
        if (!Array.isArray(timeArray) || timeArray.length === 0) {
          return timeArray;
        }
        const safeIndex = Math.min(refFrame, timeArray.length - 1);
        const anchor = Number(timeArray[safeIndex]);
        if (!Number.isFinite(anchor)) {
          return timeArray;
        }
        return timeArray.map(value => parseFloat((value - anchor).toFixed(6)));
      };

      this.animations.forEach(animation => {
        if (Array.isArray(animation.data?.time)) {
          animation.data.time = shiftByReference(animation.data.time);
        }
      });

      this.smplSequences.forEach(sequence => {
        if (Array.isArray(sequence.time)) {
          sequence.time = shiftByReference(sequence.time);
        }
      });

      this.frames = shiftByReference(this.frames);
      if (this.frames.length > 1) {
        this.frameRate = this.calculateFrameRate(this.frames);
      }
      this.frame = Math.min(Math.max(this.frame, 0), this.maxFrameIndex);
      this.updateDisplayedTime();
      this.animateOneFrame();
      this.drawProjectedSkeleton();
      this.syncVideoToFrame(this.frame, true);
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
    async openEyeDropper(target, index = null) {
      if (!window.EyeDropper) {
        alert('Your browser does not support the EyeDropper API.');
        return;
      }
  
      // Close any open dialogs before using eyedropper
      this.closeActiveMenus();
  
      const eyeDropper = new window.EyeDropper();
      try {
        // Ensure drag state doesn't interfere with eyedropper
        this.isDragging = false;
  
        const result = await eyeDropper.open();
        const selectedColorHex = result.sRGBHex;
        console.log(`Eyedropper selected: ${selectedColorHex} for target: ${target}, index: ${index}`);
  
        if (target === 'backgroundColor') {
          this.backgroundColor = selectedColorHex;
          this.updateBackgroundColor(selectedColorHex);
        } else if (target === 'groundColor') {
          this.groundColor = selectedColorHex;
          this.updateGroundColor(selectedColorHex);
        } else if (target === 'subject' && index !== null) {
          this.updateSubjectColor(index, selectedColorHex);
        } else if (target === 'marker' && index !== null) {
          this.updateMarkerColor(selectedColorHex, index);
        } else if (target === 'object' && index !== null) {
           // This part handles object colors if needed, based on the previous apply attempt
          const obj = this.customObjects.find(o => o.id === index);
          if (obj) {
              this.$set(obj, 'color', selectedColorHex);
              this.updateObjectColor(index, selectedColorHex);
          }
        } else if (target === 'force' && index !== null) {
          this.updateForceColor(selectedColorHex, index);
        }
        this.saveSettings(); // Save settings after color change
  
        // Force the next tick to ensure Vue updates DOM
        this.$nextTick(() => {
          // Make sure no lingering v-menu or dialogs stay open
          this.closeActiveMenus();
        });
  
      } catch (e) {
        console.log('EyeDropper cancelled or failed:', e);
        // Handle cancellation or error (e.g., user pressed Esc)
        this.closeActiveMenus();
      }
    },
  
    // Helper method to ensure all menus are closed
    closeActiveMenus() {
      // Make sure all dialog values are explicitly set to false
      this.showRecordingSettings = false;
      this.showCaptureSettings = false;
      this.showTimelapseSettings = false;
      this.showTimelapseManager = false;
      this.showMarkerDialog = false;
      this.showLoadObjectDialog = false;
      this.showCustomObjectsManager = false;
      this.showImportDialog = false;
  
      // Force a repaint to ensure menus are fully closed
      this.$forceUpdate();
    },
  
    // Safe methods to open settings dialogs that prevent event propagation
    openRecordingSettings(event) {
      if (event) {
        event.stopPropagation();
        event.preventDefault();
      }
      // Reset all other dialog states
      this.closeActiveMenus();
      // Set just this dialog to true
      this.$nextTick(() => {
        this.showRecordingSettings = true;
      });
    },
  
    openCaptureSettings(event) {
      if (event) {
        event.stopPropagation();
        event.preventDefault();
      }
      // Reset all other dialog states
      this.closeActiveMenus();
      // Set just this dialog to true
      this.$nextTick(() => {
        this.showCaptureSettings = true;
      });
    },
  
    openTimelapseSettings(event) {
      if (event) {
        event.stopPropagation();
        event.preventDefault();
      }
      // Reset all other dialog states
      this.closeActiveMenus();
      // Set just this dialog to true
      this.$nextTick(() => {
        this.showTimelapseSettings = true;
      });
    },
  
    // Helper function to safely format colors whether they're THREE.Color objects or hex strings
    formatColor(color) {
      if (!color) return '#CCCCCC'; // Default fallback color
  
      // If it's a THREE.Color with getHexString method
      if (color && typeof color.getHexString === 'function') {
        return '#' + color.getHexString();
      }
  
      // If it's already a hex string
      if (typeof color === 'string') {
        if (color.startsWith('#')) {
          return color;
        } else {
          return '#' + color;
        }
      }
  
      // If it has r,g,b properties (like a THREE.Color but without methods)
      if (color.r !== undefined && color.g !== undefined && color.b !== undefined) {
        const r = Math.round(color.r * 255).toString(16).padStart(2, '0');
        const g = Math.round(color.g * 255).toString(16).padStart(2, '0');
        const b = Math.round(color.b * 255).toString(16).padStart(2, '0');
        return `#${r}${g}${b}`;
      }
  
      // Final fallback
      return '#CCCCCC';
    },
  
    // Global click handler for debugging UI issues
    handleGlobalClick(event) {
      // Check if clicking on a settings button
      if (event.target && event.target.closest &&
          (event.target.closest('.settings-text-btn') ||
           event.target.classList && event.target.classList.contains('settings-text-btn'))) {
        console.log('Settings button clicked:', event.target);
        // Let the specific button handler take over
        return;
      }
  
      // Log when dialogs should be closing due to outside clicks
      const isRecordingDialogOpen = document.querySelector('.recording-settings-dialog');
      const isCaptureDialogOpen = document.querySelector('.capture-settings-dialog');
  
      if (isRecordingDialogOpen || isCaptureDialogOpen) {
        // Don't do anything, let Vuetify handle dialog clicks
        console.log('Click while dialog is open - target:', event.target);
      }
    },
  
    // Initialize display colors for v-color-picker
    initializeDisplayColors() {
      // Convert THREE.Color objects to hex strings for v-color-picker
      this.displayColors = this.colors.map(color => {
        if (color && typeof color.getHexString === 'function') {
          return '#' + color.getHexString();
        } else if (typeof color === 'string') {
          return color;
        }
        return '#FFFFFF'; // Default fallback
      });
  
      // Log for debugging
      console.log('Initialized displayColors:', this.displayColors);
    },
    updateSubjectColor(index, colorValue) {
        // Extract hex value based on the input format
        let colorHex;
  
        if (typeof colorValue === 'string') {
            // Direct hex string passed
            colorHex = colorValue;
        } else if (colorValue && colorValue.hex) {
            // Object with hex property (from v-color-picker @input)
            colorHex = colorValue.hex;
        } else if (colorValue && colorValue.rgba) {
            // Object with rgba values
            const { r, g, b } = colorValue.rgba;
            // Convert RGB to hex
            colorHex = '#' +
                Math.round(r).toString(16).padStart(2, '0') +
                Math.round(g).toString(16).padStart(2, '0') +
                Math.round(b).toString(16).padStart(2, '0');
        } else {
            console.error('Invalid color format received:', colorValue);
            return;
        }
  
        // Ensure colorHex is a valid hex string (e.g., #RRGGBB)
        if (!/^#[0-9A-F]{6}$/i.test(colorHex)) {
            console.error(`Invalid hex color received in updateSubjectColor: ${colorHex}`);
            return;
        }
  
        // Ensure arrays are properly sized before updating
        this.ensureColorArraysSync();
  
        // Update all color arrays
        const threejsColor = new THREE.Color(colorHex);
  
        // Convert hex to RGB (0-255) for RGB sliders
        const hex = colorHex.substring(1); // Remove #
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
  
        // Update all arrays simultaneously
        this.$set(this.colors, index, threejsColor);
        this.$set(this.displayColors, index, colorHex);
        this.$set(this.rgbValues, index, { r, g, b });
        // Keep existing alpha value if it exists
        if (this.alphaValues[index] === undefined) {
            this.$set(this.alphaValues, index, 1.0);
        }
  
        // Update the actual mesh colors in the scene
        Object.keys(this.meshes).forEach(key => {
            if (key.startsWith(`anim${index}_`)) {
                const mesh = this.meshes[key];
                mesh.traverse((child) => {
                    if (child instanceof THREE.Mesh) {
                        // Preserve transparency, only change color
                        child.material.color.copy(threejsColor);
                        child.material.needsUpdate = true;
                    }
                });
            }
        });
  
        // Update text sprite color
        this.updateTextSpriteColor(index, colorHex);
  
        // Render scene
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
  
        // Save settings
        this.saveSettings();
    },
    // Helper to ensure all color-related arrays are synchronized
    ensureColorArraysSync() {
        const targetLength = this.animations.length;
  
        // Ensure all arrays have the correct length
        while (this.colors.length < targetLength) {
            this.colors.push(new THREE.Color('#FFFFFF'));
        }
        while (this.displayColors.length < targetLength) {
            this.displayColors.push('#FFFFFF');
        }
        while (this.alphaValues.length < targetLength) {
            this.alphaValues.push(1.0);
        }
        while (this.rgbValues.length < targetLength) {
            this.rgbValues.push({ r: 255, g: 255, b: 255 });
        }
  
        // Trim arrays if they're too long
        if (this.colors.length > targetLength) {
            this.colors.splice(targetLength);
        }
        if (this.displayColors.length > targetLength) {
            this.displayColors.splice(targetLength);
        }
        if (this.alphaValues.length > targetLength) {
            this.alphaValues.splice(targetLength);
        }
        if (this.rgbValues.length > targetLength) {
            this.rgbValues.splice(targetLength);
        }
    },
    // Helper to initialize color arrays for a new subject
    initializeSubjectColors(index, color = null) {
        const defaultColor = color || this.getDefaultColor(index);
        const threejsColor = new THREE.Color(defaultColor);
  
        // Convert THREE.Color to RGB values (0-255)
        const r = Math.round(threejsColor.r * 255);
        const g = Math.round(threejsColor.g * 255);
        const b = Math.round(threejsColor.b * 255);
  
        // Ensure arrays are long enough
        while (this.colors.length <= index) {
            this.colors.push(new THREE.Color('#FFFFFF'));
        }
        while (this.displayColors.length <= index) {
            this.displayColors.push('#FFFFFF');
        }
        while (this.alphaValues.length <= index) {
            this.alphaValues.push(1.0);
        }
        while (this.rgbValues.length <= index) {
            this.rgbValues.push({ r: 255, g: 255, b: 255 });
        }
  
        // Set the specific values for this index
        this.$set(this.colors, index, threejsColor);
        this.$set(this.displayColors, index, defaultColor);
        this.$set(this.alphaValues, index, 1.0);
        this.$set(this.rgbValues, index, { r, g, b });
    },
    // Helper to get a default color for a subject index
    getDefaultColor(index) {
        const defaultColors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#FFB84D', '#FF7675', '#74B9FF', '#00B894'
        ];
        return defaultColors[index % defaultColors.length];
    },
    // Helper to update text sprite color separately
    updateTextSpriteColor(index, colorHex) {
        const sprite = this.textSprites[`text_${index}`];
        if (sprite && this.animations[index]) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 64;
  
            context.font = 'bold 40px Arial';
            context.textAlign = 'center';
            context.fillStyle = colorHex;
            context.fillText(this.animations[index].trialName, canvas.width/2, canvas.height/2);
  
            const texture = new THREE.CanvasTexture(canvas);
            // Properly dispose of old texture to prevent memory leaks
            if (sprite.material.map) sprite.material.map.dispose();
            sprite.material.map = texture;
            sprite.material.needsUpdate = true;
        }
    },
    // Helper to update text sprite content (name changes)
    updateTextSprite(index) {
        if (this.animations[index] && this.colors[index]) {
            this.updateTextSpriteColor(index, this.formatColor(this.colors[index]));
  
            // Render the scene with updated text
            if (this.renderer) {
                this.renderer.render(this.scene, this.camera);
            }
        }
    },
    async handleDrop(event) {
      event.preventDefault();
  
      const files = Array.from(event.dataTransfer.files);
      console.log('Files dropped:', files.map(f => f.name));
  
      // Reset temporary file state variables to ensure clean state
      this.forcesFile = null;
      this.markersFile = null;
  
      // Detect skeleton files (PKL files that are skeleton-only, NOT JSON files)
      // JSON files should be loaded as regular OpenCap JSON format
      const skeletonFiles = files.filter(file => {
        const name = file.name.toLowerCase();
        // Only PKL/pickle files are skeleton sequences, JSON files go to regular OpenCap loader
        return (name.endsWith('.pkl') || name.endsWith('.pickle')) && 
               (name.includes('skeleton') || name.includes('_pp') || name.includes('rotated'));
      });
      
      // Separate files by type - all JSON files go to regular OpenCap JSON processing
      const jsonFiles = files.filter(file => file.name.toLowerCase().endsWith('.json'));
      const trcFiles = files.filter(file => file.name.toLowerCase().endsWith('.trc'));
      const osimFiles = files.filter(file => file.name.toLowerCase().endsWith('.osim'));
      const motFiles = files.filter(file => file.name.toLowerCase().endsWith('.mot'));
      const smplFiles = files.filter(file => {
        const name = file.name.toLowerCase();
        // Exclude skeleton files, intrinsics files, and camera files
        return (name.endsWith('.pkl') || name.endsWith('.pickle')) && 
               !name.includes('intrinsic') && 
               !name.includes('extrinsic') &&
               !name.includes('camera') &&
               !name.includes('skeleton') &&
               !name.includes('_pp') &&
               !name.includes('rotated');
      });
      const intrinsicsFiles = files.filter(file => {
        const name = file.name.toLowerCase();
        // Match files with intrinsic/extrinsic/camera in name, or intrinsics-only files
        return (name.endsWith('.pkl') || name.endsWith('.pickle')) && 
               (name.includes('intrinsic') || name.includes('extrinsic') || name.includes('camera'));
      });
      const videoFiles = files.filter(file => file.type === 'video/mp4' || file.type === 'video/webm');
  
      // Categorize .mot files as either motion or force files
      const { motionFiles, forceFiles } = await this.categorizeMotFiles(motFiles);
  
      console.log('Categorized files:', {
        json: jsonFiles.length,
        trc: trcFiles.length,
        osim: osimFiles.length,
        motion: motionFiles.length,
        force: forceFiles.length,
        smpl: smplFiles.length,
        skeleton: skeletonFiles.length,
        intrinsics: intrinsicsFiles.length,
        video: videoFiles.length
      });
  
      // Handle video files
      if (videoFiles.length > 0) {
        this.videoFile = videoFiles[0];
        this.videoUrl = URL.createObjectURL(this.videoFile);
        this.$toasted.success(`Video loaded: ${videoFiles[0].name}`);
      }
  
      // Handle JSON files
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
  
      // Handle TRC files as marker files
      if (trcFiles.length > 0) {
        for (const trcFile of trcFiles) {
          // Wait to ensure animations are fully loaded if JSON files were also dropped
          await new Promise(resolve => setTimeout(resolve, 300));
  
          // Load as marker file using the existing marker loading infrastructure
          this.markersFile = trcFile;
  
          // Handle standalone marker files and associated marker files differently
          if (this.animations.length === 0) {
            // Load as standalone markers without creating an animation
            this.selectedAnimationForMarkers = null;
          } else {
            // Auto-associate with first animation that doesn't have markers, starting from newest
            let targetAnimationIndex = this.animations.length - 1; // Start with newest animation
            let foundAvailable = false;
  
            // Check from newest to oldest
            for (let i = this.animations.length - 1; i >= 0; i--) {
              if (!this.markersDatasets[i]) {
                targetAnimationIndex = i;
                foundAvailable = true;
                break;
              }
            }
  
            // If all animations have markers, use the most recent one and replace
            if (!foundAvailable) {
              targetAnimationIndex = this.animations.length - 1;
              const animationName = this.animations[targetAnimationIndex].trialName || `Animation ${targetAnimationIndex + 1}`;
              this.$toasted.info(`Replacing existing markers for ${animationName}`);
            }
  
            this.selectedAnimationForMarkers = targetAnimationIndex;
          }
  
          // Load the marker file
          await this.loadMarkersFile();
  
          this.$toasted.success(`Marker file loaded: ${trcFile.name}`);
        }
      }
  
      // Handle OpenSim files (.osim + motion .mot)
      if (osimFiles.length > 0 && motionFiles.length > 0) {
        // Process each pair of osim and mot files
        const minPairs = Math.min(osimFiles.length, motionFiles.length);
        for (let i = 0; i < minPairs; i++) {
          this.osimFile = osimFiles[i];
          this.motFile = motionFiles[i];
          await this.convertAndLoadOpenSimFiles();
        }
  
        // Warn about unpaired files
        if (osimFiles.length > motionFiles.length) {
          this.$toasted.warning(`${osimFiles.length - motionFiles.length} .osim files have no matching .mot files`);
        } else if (motionFiles.length > osimFiles.length) {
          this.$toasted.warning(`${motionFiles.length - osimFiles.length} .mot files have no matching .osim files`);
        }
      } else if (osimFiles.length > 0 || motionFiles.length > 0) {
        // Store individual files if we don't have pairs
        if (osimFiles.length > 0) {
          this.osimFile = osimFiles[0];
        }
        if (motionFiles.length > 0) {
          this.motFile = motionFiles[0];
        }
  
        if (osimFiles.length > 0 && motionFiles.length === 0) {
          this.$toasted.info('OSIM file loaded. Drop a .mot file to complete the pair.');
        } else if (osimFiles.length === 0 && motionFiles.length > 0) {
          this.$toasted.info('Motion file loaded. Drop an .osim file to complete the pair.');
        }
      }
  
      // Handle force files (after animations are loaded)
      if (forceFiles.length > 0) {
        console.log('Processing force files:', forceFiles.map(f => f.name));
        // Wait to ensure animations are fully loaded
        await new Promise(resolve => setTimeout(resolve, 300));
  
        for (const forceFile of forceFiles) {
          await this.processForceFile(forceFile);
        }
      }
  
      // Handle SMPL files (PKL files)
      if (smplFiles.length > 0) {
        console.log('Processing SMPL files:', smplFiles.map(f => f.name));
        if (intrinsicsFiles.length > 0) {
          console.log('Found intrinsics files:', intrinsicsFiles.map(f => f.name));
        }
        // Wait to ensure scene is initialized if needed
        if (!this.scene && !this.sceneInitializing) {
          this.sceneInitializing = true;
          await this.$nextTick();
          this.initScene();
        }
        
        // Use first intrinsics file for all SMPL files (or match by name if needed)
        const intrinsicsFile = intrinsicsFiles.length > 0 ? intrinsicsFiles[0] : null;
        
        for (const smplFile of smplFiles) {
          await this.processSmplSequenceFile(smplFile, intrinsicsFile);
        }
      }

      // Handle skeleton files (PKL files with joints only)
      if (skeletonFiles.length > 0) {
        console.log('Processing skeleton files:', skeletonFiles.map(f => f.name));
        if (intrinsicsFiles.length > 0) {
          console.log('Found intrinsics files for skeleton:', intrinsicsFiles.map(f => f.name));
        }
        // Wait to ensure scene is initialized if needed
        if (!this.scene && !this.sceneInitializing) {
          this.sceneInitializing = true;
          await this.$nextTick();
          this.initScene();
        }
        
        // Use first intrinsics file for all skeleton files
        const intrinsicsFile = intrinsicsFiles.length > 0 ? intrinsicsFiles[0] : null;
        
        for (const skeletonFile of skeletonFiles) {
          await this.processSkeletonSequenceFile(skeletonFile, intrinsicsFile);
        }
      }

      // Handle intrinsics/extrinsics files directly (for video plane positioning with OpenCap JSON)
      if (intrinsicsFiles.length > 0 && (jsonFiles.length > 0 || this.animations.length > 0)) {
        // Process intrinsics files to extract camera parameters for video plane
        for (const intrinsicsFile of intrinsicsFiles) {
          await this.processIntrinsicsFile(intrinsicsFile);
        }
      }
  
      // Show completion message
      if (files.length > 0) {
        this.$toasted.success(`Processed ${files.length} files successfully`);
      }
  
      // Initialize scene if needed
      if (!this.scene &&
          !this.sceneInitializing &&
          (jsonFiles.length > 0 || trcFiles.length > 0 || (osimFiles.length > 0 && motionFiles.length > 0))) {
        this.sceneInitializing = true;
        // Wait for Vue to update the DOM with the sceneInitializing flag
        this.$nextTick(() => {
          this.$nextTick(() => {
            this.initScene();
          });
        });
      }
    },
    async processSmplSequenceFile(file, intrinsicsFile = null) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add intrinsics file if provided
        if (intrinsicsFile) {
          formData.append('intrinsics_file', intrinsicsFile);
          console.log(`Including intrinsics file: ${intrinsicsFile.name}`);
        }
  
        if (!this.scene && !this.sceneInitializing) {
          this.sceneInitializing = true;
          await this.$nextTick();
          this.initScene();
        }

        // If scene isn't properly initialized (no animations/frames), load example JSON first
        // This is the same trick used when loading SMPL via JSON share files
        if ((!this.animations || this.animations.length === 0) && (!this.frames || this.frames.length === 0)) {
          try {
            console.log('Loading example mocap file to initialize scene for PKL import...');
            const exampleResponse = await fetch('/samples/squat/sample_mocap.json');
            const exampleData = await exampleResponse.json();
            
            // Add the example data as a temporary animation to initialize the scene
            const tempAnimIndex = this.animations.length;
            const fileFps = this.calculateFrameRate(exampleData.time);
            
            this.animations.push({
              data: exampleData,
              offset: new THREE.Vector3(0, 0, 0),
              rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
              fileName: 'temp_example.json',
              trialName: 'Temp Subject',
              visible: true,
              playable: true,
              calculatedFps: fileFps
            });
            
            if (this.animations.length === 1) {
              this.frames = exampleData.time;
              this.trial = { results: [] };
              this.frameRate = fileFps;
              this.frame = 0;
              if (Array.isArray(exampleData.time) && exampleData.time.length > 0) {
                this.updateDisplayedTime(0);
              } else {
                this.time = "0.000";
              }
            }
            
            // Initialize and extract marker data to properly set up the scene
            this.initializeAlphaValue(tempAnimIndex);
            this.extractMarkerDataFromJson(exampleData, tempAnimIndex, 'temp_example.json');
            
            // Wait a moment for initialization, then remove the temporary animation
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Remove the temporary example animation
            this.animations.splice(tempAnimIndex, 1);
            this.meshes = {}; // Clear meshes to start fresh
            
            console.log('Example file loaded and removed, scene initialized for PKL import');
          } catch (error) {
            console.error('Error loading example file for PKL import:', error);
          }
        }
  
        const response = await axiosInstance.post('/api/smpl/sequence', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
  
        await this.addSmplSequence(response.data, file.name);
        this.$toasted.success(`SMPL file loaded: ${file.name}`);
      } catch (error) {
        console.error('Error processing SMPL file:', error);
        let errorMessage = `Failed to load SMPL file: ${file.name}`;
        if (error.response && error.response.data) {
          const detail = error.response.data.detail || error.response.data.message || JSON.stringify(error.response.data);
          console.error('Backend error details:', detail);
          errorMessage += ` - ${detail}`;
        }
        this.$toasted.error(errorMessage);
      }
    },
    async processSkeletonSequenceFile(file, intrinsicsFile = null) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add intrinsics file if provided
        if (intrinsicsFile) {
          formData.append('intrinsics_file', intrinsicsFile);
          console.log(`Including intrinsics file for skeleton: ${intrinsicsFile.name}`);
        }
  
        if (!this.scene && !this.sceneInitializing) {
          this.sceneInitializing = true;
          await this.$nextTick();
          this.initScene();
        }

        // If scene isn't properly initialized, load example JSON first
        if ((!this.animations || this.animations.length === 0) && (!this.frames || this.frames.length === 0)) {
          try {
            console.log('Loading example mocap file to initialize scene for skeleton import...');
            const exampleResponse = await fetch('/samples/squat/sample_mocap.json');
            const exampleData = await exampleResponse.json();
            
            const tempAnimIndex = this.animations.length;
            const fileFps = this.calculateFrameRate(exampleData.time);
            
            this.animations.push({
              data: exampleData,
              offset: new THREE.Vector3(0, 0, 0),
              rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
              fileName: 'temp_example.json',
              trialName: 'Temp Subject',
              visible: true,
              playable: true,
              calculatedFps: fileFps
            });
            
            if (this.animations.length === 1) {
              this.frames = exampleData.time;
              this.trial = { results: [] };
              this.frameRate = fileFps;
              this.frame = 0;
              if (Array.isArray(exampleData.time) && exampleData.time.length > 0) {
                this.updateDisplayedTime(0);
              } else {
                this.time = "0.000";
              }
            }
            
            this.initializeAlphaValue(tempAnimIndex);
            this.extractMarkerDataFromJson(exampleData, tempAnimIndex, 'temp_example.json');
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            this.animations.splice(tempAnimIndex, 1);
            this.meshes = {};
            
            console.log('Example file loaded and removed, scene initialized for skeleton import');
          } catch (error) {
            console.error('Error loading example file for skeleton import:', error);
          }
        }
  
        const response = await axiosInstance.post('/api/smpl/skeleton', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
  
        await this.addSmplSequence(response.data, file.name);
        this.$toasted.success(`Skeleton file loaded: ${file.name}`);
      } catch (error) {
        console.error('Error processing skeleton file:', error);
        let errorMessage = `Failed to load skeleton file: ${file.name}`;
        if (error.response && error.response.data) {
          const detail = error.response.data.detail || error.response.data.message || JSON.stringify(error.response.data);
          console.error('Backend error details:', detail);
          errorMessage += ` - ${detail}`;
        }
        this.$toasted.error(errorMessage);
      }
    },
    async processIntrinsicsFile(file) {
      try {
        // Send to backend to parse the intrinsics/extrinsics pickle file
        const formData = new FormData();
        formData.append('intrinsics_file', file);
        
        const response = await axiosInstance.post('/api/smpl/extract-intrinsics', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        const data = response.data;
        
        // Store camera parameters for video plane positioning
        if (data.intrinsicMat) {
          this.cameraIntrinsics = this.normalizeMatrix3x3(data.intrinsicMat);
        }
        if (data.distortion) {
          this.cameraDistortion = this.flattenNumericArray(data.distortion);
        }
        if (data.imageSize) {
          this.cameraImageSize = this.normalizeImageSize(data.imageSize);
        }
        
        // Store extrinsics for video plane positioning (use a special key for standalone intrinsics)
        if (!this.cameraExtrinsicsMap) {
          this.cameraExtrinsicsMap = {};
        }
        if (data.cam_R && data.cam_T) {
          // Convert cam_T: check if it needs unit conversion from mm to meters
          let cam_T_converted = this.toPlainNumeric(data.cam_T);
          let cam_T_magnitude = 0;
          let unit_conversion_applied = false;
          
          if (cam_T_converted) {
            // Calculate magnitude of cam_T to detect if it's in mm (typically > 100 for mm, < 10 for meters)
            if (Array.isArray(cam_T_converted)) {
              if (Array.isArray(cam_T_converted[0])) {
                // Per-frame: [[x,y,z], [x,y,z], ...]
                const first = cam_T_converted[0];
                cam_T_magnitude = Math.sqrt(first[0]*first[0] + first[1]*first[1] + first[2]*first[2]);
              } else {
                // Single frame: [x, y, z]
                cam_T_magnitude = Math.sqrt(cam_T_converted[0]*cam_T_converted[0] + 
                                           cam_T_converted[1]*cam_T_converted[1] + 
                                           cam_T_converted[2]*cam_T_converted[2]);
              }
            }
            
            // If magnitude suggests millimeters (> 50), convert to meters
            if (cam_T_magnitude > 50) {
              unit_conversion_applied = true;
              if (Array.isArray(cam_T_converted[0])) {
                // Per-frame
                cam_T_converted = cam_T_converted.map(frame => 
                  frame.map(val => val / 1000)
                );
              } else {
                // Single frame
                cam_T_converted = cam_T_converted.map(val => val / 1000);
              }
            }
          }
          
          this.cameraExtrinsicsMap['standalone_intrinsics'] = {
            cam_R: this.toPlainNumeric(data.cam_R),
            cam_T: cam_T_converted
          };
          this.videoPlaneWidthLockedByUser = false;
          this.videoPlaneBaseWidth = null;
          this.videoPlaneDistanceLockedByUser = false;
          this.videoPlaneFrameCache = null;
          console.log('Stored camera parameters from intrinsics file:', file.name, {
            cam_T_magnitude_original: cam_T_magnitude.toFixed(2),
            unit_conversion_applied
          });
          this.$toasted.success(`Camera parameters loaded from ${file.name}${unit_conversion_applied ? ' (converted from mm to m)' : ''}`);
          
          // Update video plane if it's visible and video is loaded
          if (this.videoPlaneSettings.visible && this.videoFile) {
            this.$nextTick(() => {
              this.updateVideoPlaneGeometry();
              this.updateVideoPlaneTransform();
            });
          }
        }
      } catch (error) {
        console.error('Error processing intrinsics file:', error);
        let errorMessage = `Failed to load intrinsics file: ${file.name}`;
        if (error.response && error.response.data) {
          const detail = error.response.data.detail || error.response.data.message || JSON.stringify(error.response.data);
          console.error('Backend error details:', detail);
          errorMessage += ` - ${detail}`;
        }
        this.$toasted.error(errorMessage);
      }
    },
    async addSmplSequence(sequenceData, originalFileName) {
      if (!sequenceData) {
        console.warn('Empty SMPL sequence data received.');
        return;
      }
  
      const frameCount = sequenceData.frame_count || sequenceData.frameCount || (Array.isArray(sequenceData.time) ? sequenceData.time.length : 0);
      const vertexCount = sequenceData.vertex_count || sequenceData.vertexCount || 0;
      const jointCount = sequenceData.joint_count || sequenceData.jointCount || 24;
      const fps = sequenceData.fps || this.frameRate || 60;
      const timeArray = Array.isArray(sequenceData.time) && sequenceData.time.length === frameCount
        ? sequenceData.time
        : this.generateTimeArray(frameCount, fps);
      const verticesArray = sequenceData.vertices && sequenceData.vertices.length > 0 
        ? this.decodeBase64ToFloat32(sequenceData.vertices) 
        : null;
      const jointsArray = sequenceData.joints ? this.decodeBase64ToFloat32(sequenceData.joints) : null;
      let projectedFramesBuffer = null;
      let projectedFrameList = null;
      let projectedShape = null;
      if (Array.isArray(sequenceData.projected_shape)) {
        projectedShape = sequenceData.projected_shape.map(value => Number(value));
      }
      if (sequenceData.projected_joints && projectedShape && projectedShape.length === 3) {
        const [projectedFrameCount, projectedJointCount, projectedDims] = projectedShape;
        const projectedFlat = this.decodeBase64ToFloat32(sequenceData.projected_joints);
        const expectedLength = projectedFrameCount * projectedJointCount * projectedDims;
        if (
          projectedFlat &&
          projectedDims === 2 &&
          expectedLength === projectedFlat.length &&
          projectedFrameCount === frameCount &&
          projectedJointCount === jointCount
        ) {
          projectedFramesBuffer = projectedFlat;
          const frameStride = projectedJointCount * projectedDims;
          projectedFrameList = new Array(projectedFrameCount);
          for (let frame = 0; frame < projectedFrameCount; frame++) {
            projectedFrameList[frame] = projectedFlat.subarray(frame * frameStride, (frame + 1) * frameStride);
          }
        } else if (projectedFlat) {
          console.warn('SMPL projected joint payload shape mismatch. Overlay disabled.', {
            projectedFrameCount,
            projectedJointCount,
            projectedDims,
            expectedLength,
            actualLength: projectedFlat.length,
            frameCount,
            jointCount
          });
        }
      }
  
      // Handle skeleton-only sequences (no vertices)
      const isSkeletonOnly = !verticesArray || verticesArray.length === 0 || !vertexCount;
      
      let geometry = null;
      let positionAttribute = null;
      let mesh = null;
      
      if (!isSkeletonOnly) {
      const initialPositions = verticesArray.slice(0, vertexCount * 3);
        positionAttribute = new THREE.Float32BufferAttribute(initialPositions, 3);
        geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', positionAttribute);
      if (sequenceData.faces && sequenceData.faces.length) {
        let facesArray = sequenceData.faces;
        if (Array.isArray(facesArray[0])) {
          facesArray = facesArray.flat();
        }
        const typedIndices = facesArray.constructor === Uint16Array || facesArray.constructor === Uint32Array
          ? facesArray
          : (vertexCount > 65535 ? new Uint32Array(facesArray) : new Uint16Array(facesArray));
        geometry.setIndex(new THREE.BufferAttribute(typedIndices, 1));
      }
      geometry.computeVertexNormals();
      geometry.computeBoundingBox();
      geometry.computeBoundingSphere();
  
      const colorIndex = this.smplSequences.length % this.colors.length;
      const baseColor = this.colors[colorIndex] ? this.colors[colorIndex].clone() : new THREE.Color(0xd3d3d3);
      // Always use MeshPhongMaterial - lighting mode is controlled by light intensities
      const material = new THREE.MeshPhongMaterial({
        color: baseColor,
        transparent: false,
        opacity: 1.0,
        side: THREE.DoubleSide
      });
  
        mesh = new THREE.Mesh(geometry, material);
      mesh.castShadow = false;
      mesh.receiveShadow = false;
      mesh.frustumCulled = false;
      } else {
        // For skeleton-only, we still need joints
        if (!jointsArray || jointsArray.length === 0) {
          console.warn('No joints data found in skeleton sequence.');
          return;
        }
      }
  
      const sequenceId = this.nextSmplSequenceId++;
      const skeletonEdges = Array.isArray(sequenceData.skeleton_edges) && sequenceData.skeleton_edges.length > 0
        ? sequenceData.skeleton_edges
        : SMPL_SKELETON_EDGES;
  
      // For skeleton-only sequences, create skeleton visualization but don't auto-enable it
      // Skeleton lines can be enabled manually if needed
      let skeleton = null;
      let skeletonAttribute = null;
      
      // Create skeleton visualization for skeleton-only sequences (but don't auto-show)
      if (isSkeletonOnly && jointsArray && skeletonEdges.length > 0) {
        const skeletonGeometry = new THREE.BufferGeometry();
        skeletonAttribute = new THREE.Float32BufferAttribute(new Float32Array(skeletonEdges.length * 2 * 3), 3);
        skeletonGeometry.setAttribute('position', skeletonAttribute);
        const skeletonMaterial = new THREE.LineBasicMaterial({ color: 0xffb04a });
        skeleton = new THREE.LineSegments(skeletonGeometry, skeletonMaterial);
      }
      
      // Previously enabled skeleton rendering:
      // if (jointsArray && skeletonEdges.length > 0) {
      //   const skeletonGeometry = new THREE.BufferGeometry();
      //   skeletonAttribute = new THREE.Float32BufferAttribute(new Float32Array(skeletonEdges.length * 2 * 3), 3);
      //   skeletonGeometry.setAttribute('position', skeletonAttribute);
      //   const skeletonMaterial = new THREE.LineBasicMaterial({ color: 0xffb04a });
      //   skeleton = new THREE.LineSegments(skeletonGeometry, skeletonMaterial);
      // }
  
      const colorIndex = this.smplSequences.length % this.colors.length;
      const baseColor = this.colors[colorIndex] ? this.colors[colorIndex].clone() : new THREE.Color(0xd3d3d3);
  
      const sequence = {
        id: sequenceId,
        name: sequenceData.name || originalFileName || (isSkeletonOnly ? `Skeleton Sequence ${sequenceId}` : `SMPL Sequence ${sequenceId}`),
        fileName: originalFileName,
        gender: sequenceData.gender || 'neutral',
        vertexCount,
        jointCount,
        frameCount,
        fps,
        time: timeArray,
        faces: sequenceData.faces || [],
        vertices: verticesArray,
        joints: jointsArray,
        frameStride: vertexCount * 3,
        jointStride: jointsArray ? jointCount * 3 : 0,
        mesh,
        geometry,
        positionAttribute,
        skeleton,
        skeletonAttribute,
        skeletonEdges,
        offset: new THREE.Vector3(0, 0, 0),
        rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
        color: baseColor.clone(),
        baseColor: baseColor.clone(),
        displayColor: this.formatColor(baseColor),
        opacity: 1.0,
        visible: true,
        playable: true,
        showSkeleton: isSkeletonOnly, // Enable skeleton display for skeleton-only sequences (they have no mesh)
        lastRenderedFrame: -1,
        speedMultiplier: 1.0,
        projectedFrames: projectedFrameList || null,
        projectedFramesBuffer,
        projectedFramesShape: projectedShape ? projectedShape.slice() : null,
        projectedImageSize: Array.isArray(sequenceData.projected_image_size)
          ? sequenceData.projected_image_size.map(value => Number(value))
          : (Array.isArray(sequenceData.imageSize) ? sequenceData.imageSize.map(value => Number(value)) : null),
        projectionDirty: !(projectedFrameList || projectedFramesBuffer)
      };
  
      const sceneReady = await this.ensureSceneReady();
      if (!sceneReady) {
        console.error('Unable to prepare scene for SMPL sequence.');
        return;
      }
  
      if (mesh && !this.scene.children.includes(mesh)) {
        this.scene.add(mesh);
      }
      if (skeleton && !this.scene.children.includes(skeleton)) {
        skeleton.visible = sequence.showSkeleton;
        this.scene.add(skeleton);
        skeleton.frustumCulled = false;
      }

      // Store camera parameters from sequence data for video plane positioning
      // Note: We only need cam_R and cam_T for extrinsics (intrinsicMat is optional for plane positioning)
      if (sequenceData.cam_R && sequenceData.cam_T) {
        // Store intrinsics if available
        if (sequenceData.intrinsicMat) {
          const intrinsics = this.normalizeMatrix3x3(sequenceData.intrinsicMat);
          if (intrinsics) {
            this.cameraIntrinsics = intrinsics;
          }
          const distortion = this.flattenNumericArray(sequenceData.distortion);
          if (distortion) {
            this.cameraDistortion = distortion;
          } else if (sequenceData.distortion === null) {
            this.cameraDistortion = null;
          }
          const imageSize = this.normalizeImageSize(sequenceData.imageSize);
          if (imageSize) {
            this.cameraImageSize = imageSize;
          }
        }
        // Store camera extrinsics for video plane positioning
        if (!this.cameraExtrinsicsMap) {
          this.cameraExtrinsicsMap = {};
        }
        // Convert cam_T: check if it needs unit conversion from mm to meters
        let cam_T_converted = this.toPlainNumeric(sequenceData.cam_T);
        let cam_T_magnitude = 0;
        let unit_conversion_applied = false;
        
        if (cam_T_converted) {
          // Calculate magnitude of cam_T to detect if it's in mm (typically > 100 for mm, < 10 for meters)
          if (Array.isArray(cam_T_converted)) {
            if (Array.isArray(cam_T_converted[0])) {
              // Per-frame: [[x,y,z], [x,y,z], ...]
              const first = cam_T_converted[0];
              cam_T_magnitude = Math.sqrt(first[0]*first[0] + first[1]*first[1] + first[2]*first[2]);
            } else {
              // Single frame: [x, y, z]
              cam_T_magnitude = Math.sqrt(cam_T_converted[0]*cam_T_converted[0] + 
                                         cam_T_converted[1]*cam_T_converted[1] + 
                                         cam_T_converted[2]*cam_T_converted[2]);
            }
          }
          
          // If magnitude suggests millimeters (> 50), convert to meters
          if (cam_T_magnitude > 50) {
            unit_conversion_applied = true;
            if (Array.isArray(cam_T_converted[0])) {
              // Per-frame
              cam_T_converted = cam_T_converted.map(frame => 
                frame.map(val => val / 1000)
              );
            } else {
              // Single frame
              cam_T_converted = cam_T_converted.map(val => val / 1000);
            }
          }
        }
        
        this.cameraExtrinsicsMap[sequenceId] = {
          cam_R: this.toPlainNumeric(sequenceData.cam_R),
          cam_T: cam_T_converted
        };
        this.videoPlaneWidthLockedByUser = false;
        this.videoPlaneBaseWidth = null;
        this.videoPlaneDistanceLockedByUser = false;
        this.videoPlaneFrameCache = null;
        console.log('Stored camera extrinsics for sequence:', sequenceId, {
          hasCam_R: !!sequenceData.cam_R,
          hasCam_T: !!sequenceData.cam_T,
          cam_R_type: Array.isArray(sequenceData.cam_R) ? 'array' : typeof sequenceData.cam_R,
          cam_T_type: Array.isArray(sequenceData.cam_T) ? 'array' : typeof sequenceData.cam_T,
          cam_T_magnitude_original: cam_T_magnitude.toFixed(2),
          unit_conversion_applied
        });
        
        // Update video plane if it's visible and video is loaded
        if (this.videoPlaneSettings.visible && this.videoFile) {
          this.$nextTick(() => {
            this.updateVideoPlaneGeometry();
            this.updateVideoPlaneTransform();
          });
        }
      } else {
        console.warn('Missing camera extrinsics in sequence data:', {
          hasCam_R: !!sequenceData.cam_R,
          hasCam_T: !!sequenceData.cam_T,
          sequenceId: sequenceId
        });
      }

      this.smplSequences.push(sequence);
      this.refreshSequenceProjectionValidity(sequence);
      if (!this.activeSubject || this.activeSubject.type !== 'smpl') {
        this.setActiveSubject('smpl', sequence.id);
      }

      if (sequence.mesh) {
      sequence.mesh.visible = sequence.visible;
      }
      if (sequence.skeleton) {
        // For skeleton-only sequences, show skeleton if visible
        sequence.skeleton.visible = sequence.visible && sequence.showSkeleton;
        console.log('Skeleton visibility set:', {
          visible: sequence.visible,
          showSkeleton: sequence.showSkeleton,
          finalVisible: sequence.skeleton.visible,
          isSkeletonOnly,
          skeletonExists: !!sequence.skeleton
        });
      }
  
      if (this.frames.length === 0 || timeArray.length > this.frames.length) {
        this.frames = [...timeArray];
        this.frameRate = fps;
        this.frame = 0;
        if (this.frames.length > 0) {
          this.updateDisplayedTime(0);
        } else {
          this.time = '0.000';
        }
      }
  
      this.updateSmplSequenceFrame(sequence, 0, true);
  
      if (sequence.mesh) {
      if (sequence.mesh.parent) {
        sequence.mesh.parent.updateMatrixWorld(true);
      }
      sequence.mesh.updateMatrixWorld(true);
      }
  
      if (sequence.skeleton) {
        if (sequence.skeleton.parent) {
        sequence.skeleton.parent.updateMatrixWorld(true);
        }
        sequence.skeleton.updateMatrixWorld(true);
      }
  
      if (this.animations.length === 0 && this.smplSequences.length === 1) {
        this.centerCameraOnSmplSequence(sequence);
      }
  
      if (!this.animateLoopStarted) {
        this.animate();
      }
  
      if (!this.playing) {
        this.animateOneFrame();
      } else if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
      if (this.syncMode !== 'none') {
        this.$nextTick(() => this.applySyncMode());
      }
    },
    encodeFloat32ToBase64(float32Array) {
      if (!float32Array || float32Array.length === 0) return '';
      const bytes = new Uint8Array(float32Array.buffer);
      let binaryString = '';
      for (let i = 0; i < bytes.length; i++) {
        binaryString += String.fromCharCode(bytes[i]);
      }
      return btoa(binaryString);
    },
    
    decodeBase64ToFloat32(base64String) {
      if (!base64String) return null;
      const binaryString = atob(base64String);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      return new Float32Array(bytes.buffer);
    },
    generateTimeArray(frameCount, fps) {
      const timeArray = [];
      if (!frameCount || frameCount <= 0) return timeArray;
      const step = fps ? 1 / fps : 1 / this.frameRate;
      for (let i = 0; i < frameCount; i++) {
        timeArray.push(i * step);
      }
      return timeArray;
    },
    getFrameSeconds(frameIndex) {
      const framesLength = Array.isArray(this.frames) ? this.frames.length : 0;
      const safeRate = Number.isFinite(this.frameRate) && this.frameRate > 0 ? this.frameRate : 60;
      if (framesLength === 0) {
        return Number.isFinite(frameIndex) ? frameIndex / safeRate : 0;
      }
      const clampedIndex = Number.isFinite(frameIndex)
        ? Math.min(Math.max(Math.round(frameIndex), 0), framesLength - 1)
        : Math.min(Math.max(this.frame, 0), framesLength - 1);
      const raw = this.frames[clampedIndex];
      if (typeof raw === 'number' && Number.isFinite(raw)) {
        return raw;
      }
      const parsed = parseFloat(raw);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
      return clampedIndex / safeRate;
    },
    updateDisplayedTime(frameIndex = null) {
      const index = frameIndex == null ? this.frame : frameIndex;
      const seconds = this.getFrameSeconds(index);
      this.time = seconds.toFixed(3);
    },
    updateSmplSequenceFrame(sequence, frameIndex, force = false) {
      if (!sequence || frameIndex < 0) return;
      const clampedFrame = Math.min(frameIndex, Math.max(sequence.frameCount - 1, 0));
      if (!force && sequence.lastRenderedFrame === clampedFrame) {
        return;
      }
  
      // Update mesh vertices if mesh exists
      if (sequence.mesh && sequence.vertices && sequence.vertexCount > 0) {
    const start = clampedFrame * sequence.frameStride;
    const end = start + sequence.frameStride;
    const positions = sequence.vertices.subarray(start, end);
        if (sequence.positionAttribute && sequence.positionAttribute.array !== positions) {
      sequence.positionAttribute.array = positions;
      sequence.positionAttribute.count = sequence.vertexCount;
    }
        if (sequence.positionAttribute) {
    sequence.positionAttribute.needsUpdate = true;
        }
    if (sequence.geometry && sequence.geometry.attributes && sequence.geometry.attributes.position !== sequence.positionAttribute) {
      sequence.geometry.setAttribute('position', sequence.positionAttribute);
    }
    if (sequence.mesh) {
      sequence.mesh.rotation.copy(sequence.rotation);
      if (sequence.offset) {
        sequence.mesh.position.set(sequence.offset.x, sequence.offset.y, sequence.offset.z);
      }
    }
      }
      
      // Update skeleton position and joints
    if (sequence.skeleton) {
      sequence.skeleton.rotation.copy(sequence.rotation);
      if (sequence.offset) {
        sequence.skeleton.position.set(sequence.offset.x, sequence.offset.y, sequence.offset.z);
      }
    }

      // Update skeleton joints if skeleton exists and joints data is available
      if (sequence.skeleton && sequence.joints && sequence.skeletonAttribute && sequence.skeletonEdges) {
      const jointStart = clampedFrame * sequence.jointStride;
        if (jointStart + sequence.jointStride <= sequence.joints.length) {
      const jointPositions = sequence.joints.subarray(jointStart, jointStart + sequence.jointStride);
        const skeletonArray = sequence.skeletonAttribute.array;
        let offset = 0;
        for (const [parent, child] of sequence.skeletonEdges) {
            if (parent < sequence.jointCount && child < sequence.jointCount) {
          const pIndex = parent * 3;
          const cIndex = child * 3;
              if (pIndex + 2 < jointPositions.length && cIndex + 2 < jointPositions.length) {
          skeletonArray[offset++] = jointPositions[pIndex];
          skeletonArray[offset++] = jointPositions[pIndex + 1];
          skeletonArray[offset++] = jointPositions[pIndex + 2];
          skeletonArray[offset++] = jointPositions[cIndex];
          skeletonArray[offset++] = jointPositions[cIndex + 1];
          skeletonArray[offset++] = jointPositions[cIndex + 2];
              }
            }
        }
        sequence.skeletonAttribute.needsUpdate = true;
        }
      }
  
      sequence.lastRenderedFrame = clampedFrame;
    },
    toggleSmplSequenceVisibility(sequenceId) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence) return;
      sequence.visible = !sequence.visible;
      if (sequence.mesh) {
        sequence.mesh.visible = sequence.visible;
      }
      if (sequence.skeleton) {
        sequence.skeleton.visible = sequence.visible && sequence.showSkeleton;
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    setSmplSequencePlayable(sequenceId, value) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence) return;
      sequence.playable = value;
    },
    setSmplSequenceColor(sequenceId, colorValue) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence) return;
  
      let targetColor;
      if (colorValue === 'original' && sequence.baseColor) {
        targetColor = sequence.baseColor.clone();
      } else {
        targetColor = new THREE.Color(colorValue);
      }
  
      sequence.color = targetColor.clone();
      if (sequence.mesh && sequence.mesh.material) {
        sequence.mesh.material.color.copy(targetColor);
        sequence.mesh.material.needsUpdate = true;
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    updateSmplSequenceColor(sequenceId, colorValue) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence) return;
  
      // Handle both string colors and Vuetify color objects
      let targetColor;
      if (typeof colorValue === 'string') {
        targetColor = new THREE.Color(colorValue);
      } else if (colorValue.hex) {
        targetColor = new THREE.Color(colorValue.hex);
      } else {
        targetColor = new THREE.Color(colorValue.r / 255, colorValue.g / 255, colorValue.b / 255);
      }
  
      sequence.color = targetColor.clone();
      if (sequence.mesh && sequence.mesh.material) {
        sequence.mesh.material.color.copy(targetColor);
        sequence.mesh.material.needsUpdate = true;
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    updateSmplOpacity(sequenceId, opacity) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence) return;
      
      sequence.opacity = opacity;
      if (sequence.mesh && sequence.mesh.material) {
        sequence.mesh.material.opacity = opacity;
        sequence.mesh.material.transparent = opacity < 1;
        sequence.mesh.material.needsUpdate = true;
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    toggleSmplSkeleton(sequenceId) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence || !sequence.skeleton) return;
      sequence.showSkeleton = !sequence.showSkeleton;
      sequence.skeleton.visible = sequence.visible && sequence.showSkeleton;
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
      if (this.isActiveSubject('smpl', sequenceId)) {
        this.drawProjectedSkeleton();
      }
    },
    setActiveSubject(type, identifier) {
      if (type === 'smpl') {
        const sequence = this.smplSequences.find(seq => seq.id === identifier);
        if (!sequence) {
          return;
        }
        this.activeSubject = { type: 'smpl', id: identifier };
        this.refreshSequenceProjectionValidity(sequence);
        this.$nextTick(() => this.drawProjectedSkeleton());
        return;
      }
      if (type === 'animation') {
        if (typeof identifier === 'number' && this.animations[identifier]) {
          this.activeSubject = { type: 'animation', index: identifier };
        }
      }
    },
    isActiveSubject(type, identifier) {
      if (!this.activeSubject) return false;
      if (this.activeSubject.type !== type) return false;
      if (type === 'smpl') {
        return this.activeSubject.id === identifier;
      }
      if (type === 'animation') {
        return this.activeSubject.index === identifier;
      }
      return false;
    },
    resolveActiveSubject() {
      if (this.activeSubject) {
        if (this.activeSubject.type === 'smpl') {
          const sequence = this.smplSequences.find(seq => seq.id === this.activeSubject.id);
          if (sequence) {
            return { type: 'smpl', sequence };
          }
        } else if (this.activeSubject.type === 'animation') {
          const animation = this.animations[this.activeSubject.index];
          if (animation) {
            return { type: 'animation', animation, index: this.activeSubject.index };
          }
        }
      }
      if (this.smplSequences.length > 0) {
        const first = this.smplSequences[0];
        this.activeSubject = { type: 'smpl', id: first.id };
        return { type: 'smpl', sequence: first };
      }
      if (this.animations.length > 0) {
        this.activeSubject = { type: 'animation', index: 0 };
        return { type: 'animation', animation: this.animations[0], index: 0 };
      }
      return null;
    },
    centerCameraOnSmplSequence(sequence) {
      if (!sequence || !sequence.mesh || !this.camera || !this.controls) return;
  
      // Ensure mesh has updated its geometry bounds
      sequence.mesh.geometry.computeBoundingBox();
      
      // Force update matrix to ensure bounding box is calculated in world space
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
  
      const fov = this.camera.fov * (Math.PI / 180);
      const distance = Math.max(Math.abs(maxDim / Math.sin(fov / 2)) * 1.5, 1.0);
      const direction = new THREE.Vector3(1, 1, 1).normalize();
      const position = center.clone().add(direction.multiplyScalar(distance));
  
      this.camera.position.copy(position);
      this.camera.lookAt(center);
      this.controls.target.copy(center);
      this.controls.update();
  
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    removeSmplSequence(sequenceId) {
      const index = this.smplSequences.findIndex(seq => seq.id === sequenceId);
      if (index === -1) return;
  
      const sequence = this.smplSequences[index];
      if (sequence.mesh) {
        this.scene.remove(sequence.mesh);
        sequence.mesh.geometry.dispose();
        if (Array.isArray(sequence.mesh.material)) {
          sequence.mesh.material.forEach(mat => mat.dispose && mat.dispose());
        } else if (sequence.mesh.material && sequence.mesh.material.dispose) {
          sequence.mesh.material.dispose();
        }
      }
    if (sequence.skeleton) {
      this.scene.remove(sequence.skeleton);
      sequence.skeleton.geometry.dispose();
      sequence.skeleton.material.dispose();
    }

    this.smplSequences.splice(index, 1);

    if (this.animations.length === 0 && this.smplSequences.length === 0) {
      this.frames = [];
      this.frame = 0;
      this.time = '0.000';
    }
    if (this.activeSubject && this.activeSubject.type === 'smpl' && this.activeSubject.id === sequenceId) {
      if (this.smplSequences.length > 0) {
        const fallback = this.smplSequences[Math.min(index, this.smplSequences.length - 1)];
        this.setActiveSubject('smpl', fallback.id);
      } else {
        this.activeSubject = null;
        this.clearProjectionCanvas();
      }
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
    this.drawProjectedSkeleton();
    },
    updateSmplOffset(sequenceId, axis, value) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence || !sequence.offset) return;
      const numericValue = parseFloat(value);
      if (!Number.isFinite(numericValue)) {
        return;
      }
      sequence.offset[axis] = numericValue;
      if (sequence.mesh) {
        sequence.mesh.position.set(sequence.offset.x, sequence.offset.y, sequence.offset.z);
      }
      if (sequence.skeleton) {
        sequence.skeleton.position.set(sequence.offset.x, sequence.offset.y, sequence.offset.z);
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    this.refreshSequenceProjectionValidity(sequence);
    this.drawProjectedSkeleton();
  },
  handleSubjectNudge(code, event) {
    if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code)) {
      return false;
    }
    event.preventDefault();
    const baseStep = (event.ctrlKey || event.metaKey) ? 0.05 : 0.02;
    switch (code) {
      case 'ArrowUp':
        this.nudgeActiveSubject('y', baseStep);
        return true;
      case 'ArrowDown':
        this.nudgeActiveSubject('y', -baseStep);
        return true;
      case 'ArrowLeft':
        this.nudgeActiveSubject('x', -baseStep);
        return true;
      case 'ArrowRight':
        this.nudgeActiveSubject('x', baseStep);
        return true;
      default:
        return false;
    }
  },
  nudgeActiveSubject(axis, delta) {
    const subject = this.resolveActiveSubject();
    if (!subject || subject.type !== 'smpl') {
      return false;
    }
    const sequence = subject.sequence;
    if (!sequence) {
      return false;
    }
    if (!sequence.offset) {
      sequence.offset = new THREE.Vector3(0, 0, 0);
    }
    const nextValue = parseFloat(((sequence.offset[axis] || 0) + delta).toFixed(4));
    this.updateSmplOffset(sequence.id, axis, nextValue);
    return true;
  },
  debouncedUpdateSmplOffset(sequenceId, axis, value) {
    if (this.offsetUpdateTimers[`smpl_${sequenceId}_${axis}`]) {
      clearTimeout(this.offsetUpdateTimers[`smpl_${sequenceId}_${axis}`]);
    }
      this.offsetUpdateTimers[`smpl_${sequenceId}_${axis}`] = setTimeout(() => {
        this.updateSmplOffset(sequenceId, axis, value);
      }, 100);
    },
    updateSmplRotation(sequenceId, axis, value) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence || !sequence.rotation) return;
      const radians = (parseFloat(value) * Math.PI) / 180;
      sequence.rotation[axis] = radians;
      if (sequence.lastRenderedFrame >= 0) {
        this.updateSmplSequenceFrame(sequence, sequence.lastRenderedFrame, true);
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
      this.refreshSequenceProjectionValidity(sequence);
      this.drawProjectedSkeleton();
    },
    debouncedUpdateSmplRotation(sequenceId, axis, value) {
      const key = `smpl_${sequenceId}_${axis}`;
      if (this.rotationUpdateTimers[key]) {
        clearTimeout(this.rotationUpdateTimers[key]);
      }
      this.rotationUpdateTimers[key] = setTimeout(() => {
        this.updateSmplRotation(sequenceId, axis, value);
      }, 100);
    },
    openSmplRotationDialog(sequenceId) {
      this.$set(this.smplRotationDialogs, sequenceId, true);
    },
    resetSmplRotation(sequenceId) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence || !sequence.rotation) return;
      sequence.rotation.set(0, 0, 0, 'XYZ');
      if (sequence.mesh) {
        sequence.mesh.rotation.set(0, 0, 0);
      }
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
      this.refreshSequenceProjectionValidity(sequence);
      this.drawProjectedSkeleton();
    },
    updateAnimationSpeed(index) {
      // Just ensure the speedMultiplier is valid
      if (!this.animations[index]) return;
      if (!this.animations[index].speedMultiplier || this.animations[index].speedMultiplier < 0.1) {
        this.animations[index].speedMultiplier = 0.1;
      } else if (this.animations[index].speedMultiplier > 5) {
        this.animations[index].speedMultiplier = 5;
      }
    },
    updateSmplSpeed(sequenceId) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence) return;
      // Ensure the speedMultiplier is valid
      if (!sequence.speedMultiplier || sequence.speedMultiplier < 0.1) {
        sequence.speedMultiplier = 0.1;
      } else if (sequence.speedMultiplier > 5) {
        sequence.speedMultiplier = 5;
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
  
        // Remove from all arrays simultaneously to maintain sync
        this.animations.splice(index, 1);
        this.colors.splice(index, 1);
        this.displayColors.splice(index, 1);
        this.alphaValues.splice(index, 1);
        this.rgbValues.splice(index, 1);
  
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

        // Clear force arrows for the deleted animation
        if (this.forcesDatasets[index]) {
            this.clearForceArrowsForAnimation(index);
        }

        // Reindex force datasets
        const oldForcesDatasets = { ...this.forcesDatasets };
        this.forcesDatasets = {};
        Object.keys(oldForcesDatasets).forEach(key => {
            const oldIndex = parseInt(key);
            if (oldIndex === index) {
                // Already cleared by clearForceArrowsForAnimation
                return;
            }
            // Calculate new index (same logic as timelapse)
            let newIndex = oldIndex;
            if (oldIndex > index) {
                newIndex = oldIndex - 1;
            }
            if (newIndex >= 0 && newIndex < this.animations.length) {
                this.forcesDatasets[newIndex] = oldForcesDatasets[oldIndex];
                // Update associatedAnimationIndex in the dataset
                if (this.forcesDatasets[newIndex]) {
                    this.forcesDatasets[newIndex].associatedAnimationIndex = newIndex;
                }
            }
        });

        // Reindex force arrows
        this.forceArrows.forEach(arrowGroup => {
            if (arrowGroup.userData && typeof arrowGroup.userData.animationIndex !== 'undefined') {
                const oldIndex = arrowGroup.userData.animationIndex;
                if (oldIndex === index) {
                    // This arrow belongs to deleted animation - should have been cleared
                    return;
                }
                // Update animation index
                if (oldIndex > index) {
                    arrowGroup.userData.animationIndex = oldIndex - 1;
                }
            }
        });

        // Reindex forcesVisible
        const oldForcesVisible = { ...this.forcesVisible };
        this.forcesVisible = {};
        Object.keys(oldForcesVisible).forEach(key => {
            const oldIndex = parseInt(key);
            if (oldIndex === index) return; // Skip deleted animation
            let newIndex = oldIndex;
            if (oldIndex > index) {
                newIndex = oldIndex - 1;
            }
            if (newIndex >= 0 && newIndex < this.animations.length) {
                this.$set(this.forcesVisible, String(newIndex), oldForcesVisible[key]);
            }
        });

        // Reindex forceColors and forceDisplayColors
        if (this.forceColors && typeof this.forceColors === 'object' && !Array.isArray(this.forceColors)) {
            const oldForceColors = { ...this.forceColors };
            this.forceColors = {};
            Object.keys(oldForceColors).forEach(key => {
                const oldIndex = parseInt(key);
                if (oldIndex === index) return;
                let newIndex = oldIndex;
                if (oldIndex > index) {
                    newIndex = oldIndex - 1;
                }
                if (newIndex >= 0 && newIndex < this.animations.length) {
                    this.$set(this.forceColors, newIndex, oldForceColors[oldIndex]);
                }
            });
        }
        // Same for forceDisplayColors if it exists
        if (this.forceDisplayColors && typeof this.forceDisplayColors === 'object' && !Array.isArray(this.forceDisplayColors)) {
            const oldForceDisplayColors = { ...this.forceDisplayColors };
            this.forceDisplayColors = {};
            Object.keys(oldForceDisplayColors).forEach(key => {
                const oldIndex = parseInt(key);
                if (oldIndex === index) return;
                let newIndex = oldIndex;
                if (oldIndex > index) {
                    newIndex = oldIndex - 1;
                }
                if (newIndex >= 0 && newIndex < this.animations.length) {
                    this.$set(this.forceDisplayColors, newIndex, oldForceDisplayColors[oldIndex]);
                }
            });
        }

        // Reindex markersDatasets
        const oldMarkersDatasets = { ...this.markersDatasets };
        this.markersDatasets = {};
        Object.keys(oldMarkersDatasets).forEach(key => {
            const oldIndex = parseInt(key);
            if (oldIndex === index) return; // Delete markers for removed animation
            let newIndex = oldIndex;
            if (oldIndex > index) {
                newIndex = oldIndex - 1;
            }
            if (newIndex >= 0 && newIndex < this.animations.length) {
                this.markersDatasets[newIndex] = oldMarkersDatasets[oldIndex];
            }
        });

        // Reindex markersVisible
        const oldMarkersVisible = { ...this.markersVisible };
        this.markersVisible = {};
        Object.keys(oldMarkersVisible).forEach(key => {
            const oldIndex = parseInt(key);
            if (oldIndex === index) return;
            let newIndex = oldIndex;
            if (oldIndex > index) {
                newIndex = oldIndex - 1;
            }
            if (newIndex >= 0 && newIndex < this.animations.length) {
                this.$set(this.markersVisible, String(newIndex), oldMarkersVisible[key]);
            }
        });

        // Reindex marker spheres
        if (this.markerSpheres && Array.isArray(this.markerSpheres)) {
            this.markerSpheres.forEach(sphere => {
                if (sphere.userData && typeof sphere.userData.animationIndex !== 'undefined') {
                    const oldIndex = sphere.userData.animationIndex;
                    if (oldIndex === index) {
                        // Remove marker spheres for deleted animation
                        if (this.scene && this.scene.children.includes(sphere)) {
                            this.scene.remove(sphere);
                        }
                        if (sphere.geometry) sphere.geometry.dispose();
                        if (sphere.material) {
                            if (Array.isArray(sphere.material)) {
                                sphere.material.forEach(mat => mat.dispose && mat.dispose());
                            } else if (sphere.material.dispose) {
                                sphere.material.dispose();
                            }
                        }
                    } else if (oldIndex > index) {
                        // Update animation index
                        sphere.userData.animationIndex = oldIndex - 1;
                    }
                }
            });
            // Remove marker spheres for deleted animation from array
            this.markerSpheres = this.markerSpheres.filter(sphere => {
                if (sphere.userData && sphere.userData.animationIndex === index) {
                    return false; // Remove spheres for deleted animation
                }
                return true;
            });
        }

        // Update selectedAnimationForForces if it references the deleted animation
        if (this.selectedAnimationForForces === index) {
            // Find the first available animation with forces, or default to 0
            const availableIndex = Object.keys(this.forcesDatasets).length > 0 
                ? Math.min(...Object.keys(this.forcesDatasets).map(k => parseInt(k)))
                : 0;
            this.selectedAnimationForForces = availableIndex < this.animations.length ? availableIndex : 0;
        } else if (this.selectedAnimationForForces > index) {
            // Decrement if the selected index is after the deleted one
            this.selectedAnimationForForces = this.selectedAnimationForForces - 1;
        }

        // Update selectedAnimationForMarkers if it references the deleted animation
        if (this.selectedAnimationForMarkers === index) {
            // Find the first available animation with markers, or default to 0
            const availableIndex = Object.keys(this.markersDatasets).length > 0 
                ? Math.min(...Object.keys(this.markersDatasets).map(k => parseInt(k)))
                : 0;
            this.selectedAnimationForMarkers = availableIndex < this.animations.length ? availableIndex : 0;
        } else if (this.selectedAnimationForMarkers !== null && this.selectedAnimationForMarkers > index) {
            // Decrement if the selected index is after the deleted one
            this.selectedAnimationForMarkers = this.selectedAnimationForMarkers - 1;
        }
  
        // Rebuild meshes and text sprites with correct indices
        this.reindexSubjects(index);
  
        if (this.animations.length > 0) {
            this.frames = this.animations[0].data.time;
            if (this.animations.length > 1) {
                this.syncAllAnimations();
            }
        } else {
            // Reset to initial state when no animations remain
            this.frames = [];
            this.frame = 0;
            this.time = '0.000';
            this.trial = null;
            this.playing = false;
            this.frameAccumulator = 0;
  
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
  
        // Save settings after deletion
        this.saveSettings();
    },
    reindexSubjects(deletedIndex) {
        // Reindex all mesh keys and text sprites after subject deletion
        const oldMeshes = { ...this.meshes };
        const oldTextSprites = { ...this.textSprites };
  
        // Clear existing meshes and text sprites
        this.meshes = {};
        this.textSprites = {};
  
        // Reindex meshes
        Object.keys(oldMeshes).forEach(key => {
            const match = key.match(/^anim(\d+)_(.+)$/);
            if (match) {
                const oldIndex = parseInt(match[1]);
                const meshName = match[2];
  
                // Calculate new index based on deleted index
                // If oldIndex < deletedIndex: newIndex = oldIndex (no change)
                // If oldIndex > deletedIndex: newIndex = oldIndex - 1 (decrement by 1)
                let newIndex = oldIndex;
                if (oldIndex > deletedIndex) {
                    newIndex = oldIndex - 1;
                }
                // Skip if this was the deleted index
                if (oldIndex === deletedIndex) {
                    return;
                }
  
                // Validate newIndex is within bounds
                if (newIndex >= 0 && newIndex < this.animations.length) {
                    const newKey = `anim${newIndex}_${meshName}`;
                    this.meshes[newKey] = oldMeshes[key];
  
                    // Update mesh color to match current animation color
                    const mesh = this.meshes[newKey];
                    if (mesh && this.colors[newIndex]) {
                        mesh.traverse((child) => {
                            if (child instanceof THREE.Mesh) {
                                child.material.color.copy(this.colors[newIndex]);
                                child.material.needsUpdate = true;
                            }
                        });
                    }
                }
            }
        });
  
        // Reindex text sprites
        Object.keys(oldTextSprites).forEach(key => {
            const match = key.match(/^text_(\d+)$/);
            if (match) {
                const oldIndex = parseInt(match[1]);
  
                // Calculate new index based on deleted index
                // If oldIndex < deletedIndex: newIndex = oldIndex (no change)
                // If oldIndex > deletedIndex: newIndex = oldIndex - 1 (decrement by 1)
                let newIndex = oldIndex;
                if (oldIndex > deletedIndex) {
                    newIndex = oldIndex - 1;
                }
                // Skip if this was the deleted index
                if (oldIndex === deletedIndex) {
                    return;
                }
  
                // Validate newIndex is within bounds
                if (newIndex >= 0 && newIndex < this.animations.length) {
                    const newKey = `text_${newIndex}`;
                    this.textSprites[newKey] = oldTextSprites[key];
  
                    // Update text sprite content and color
                    this.updateTextSpriteColor(newIndex, this.formatColor(this.colors[newIndex]));
                }
            }
        });
    },
    loadSampleFiles(sampleSet = 'STS', subjectsFilter = null, loadVideo = false) { // Default to 'STS' if no set is provided
        console.log(`loadSampleFiles called for set: ${sampleSet}, subjects filter: ${subjectsFilter}, loadVideo: ${loadVideo}`);
  
        // Validate sample set name, default to 'STS' if invalid
        const validSets = ['squat', 'walk', 'STS', 'rmasb', 'walk_ts'];
        if (!validSets.includes(sampleSet)) {
            console.warn(`Invalid sample set "${sampleSet}" provided. Defaulting to 'STS'.`);
            sampleSet = 'STS';
        }
  
        // Define available subjects and their corresponding sample files
        const availableSubjects = {
            'mocap': `/samples/${sampleSet}/sample_mocap.json`,
            'mono': `/samples/${sampleSet}/sample_mono.json`,
            'wham': `/samples/${sampleSet}/sample_wham.json`
        };

        // Filter subjects based on URL parameter if provided
        let sampleFiles;
        if (subjectsFilter && subjectsFilter.length > 0) {
            // Parse comma-separated subjects and filter to valid ones
            const requestedSubjects = subjectsFilter
                .split(',')
                .map(s => s.trim().toLowerCase())
                .filter(s => Object.prototype.hasOwnProperty.call(availableSubjects, s));
            
            if (requestedSubjects.length > 0) {
                sampleFiles = requestedSubjects.map(s => availableSubjects[s]);
                console.log(`Filtered to subjects: ${requestedSubjects.join(', ')}`);
            } else {
                console.warn(`No valid subjects in filter "${subjectsFilter}". Loading all subjects.`);
                sampleFiles = Object.values(availableSubjects);
            }
        } else {
            // No filter, load all subjects
            sampleFiles = Object.values(availableSubjects);
        }
  
        // Add GRF.mot for walk sample set
        if (sampleSet === 'walk') {
            sampleFiles.push(`/samples/${sampleSet}/GRF.mot`);
        }
  
        console.log('Attempting to fetch potential sample files:', sampleFiles);
  
        // Show loading indicator
        this.trialLoading = true;
  
        // Clear existing animations before loading new ones
        this.animations = [];
        this.clearExistingObjects(); // Clear meshes and sprites from previous loads
  
        // First, try to fetch param.json for offsets
        const paramUrl = `/samples/${sampleSet}/param.json`;
        const paramPromise = fetch(paramUrl)
            .then(response => {
                if (!response.ok) {
                    console.log(`No param.json found for ${sampleSet}, using default offsets`);
                    return null;
                }
                return response.json();
            })
            .catch(error => {
                console.log(`Error fetching param.json for ${sampleSet}:`, error);
                return null;
            });

        // Fetch all potential sample files, handling individual failures
        Promise.all([paramPromise, ...sampleFiles.map(url => {
          const isMotOrTrc = url.endsWith('.mot') || url.endsWith('.trc');
          return fetch(url)
              .then(response => {
                  if (!response.ok) {
                      // Log warning but don't throw error, return null to indicate failure
                      console.warn(`Sample file not found or failed to load: ${url} (${response.status})`);
                      return null;
                  }
                  // If response is OK, parse based on file type
                  if (isMotOrTrc) {
                    return response.blob().then(blob => ({ blob, url }));
                  }
                  return response.json().then(data => ({ data, url }));
              })
              .catch(error => {
                  // Catch network or other fetch errors
                  console.warn(`Error fetching sample file ${url}:`, error);
                  return null; // Indicate failure
              })
        })]) // Close the map, then close the array, then close Promise.all
        .then(results => {
            // First result is paramData, rest are sample files
            const paramData = results[0];
            const sampleResults = results.slice(1);
            
            // Extract offsets from param.json if available
            let mocapOffsets = { x: 0, y: 0, z: 0 };
            if (paramData && paramData.mocap) {
                mocapOffsets = {
                    x: paramData.mocap.x_offset || 0,
                    y: paramData.mocap.y_offset || 0,
                    z: paramData.mocap.z_offset || 0
                };
                console.log('Loaded mocap offsets from param.json:', mocapOffsets);
            }
            
            // Filter out null results (failed fetches)
            const successfulResults = sampleResults.filter(r => r !== null);
  
            console.log(`Successfully loaded ${successfulResults.length} sample files.`);
  
            // If no files were loaded successfully, show an error or message
            if (successfulResults.length === 0) {
                console.error('No valid sample files found for set:', sampleSet);
                alert(`Could not load any sample files for the set: ${sampleSet}. Please check the /public/samples/${sampleSet} folder.`);
                this.trialLoading = false;
                return; // Stop processing
            }
  
            // Load video if requested
            if (loadVideo) {
                const videoUrl = `/samples/${sampleSet}/video.mp4`;
                fetch(videoUrl)
                    .then(response => {
                        if (!response.ok) {
                            console.warn(`Video file not found: ${videoUrl}`);
                            return null;
                        }
                        return response.blob();
                    })
                    .then(blob => {
                        if (blob) {
                            // Clean up previous video URL if it exists
                            if (this.videoUrl) {
                                URL.revokeObjectURL(this.videoUrl);
                            }
                            // Create File object from blob
                            const videoFile = new File([blob], `video.mp4`, { type: 'video/mp4' });
                            this.videoFile = videoFile;
                            this.videoUrl = URL.createObjectURL(videoFile);
                            this.videoMinimized = false; // Ensure video starts in full size
                            
                            // Reset video plane settings to defaults (show video plane = false)
                            this.videoPlaneSettings.visible = false;
                            this.videoPlaneSettings.followCamera = true;
                            
                            console.log('Sample video loaded:', videoUrl);
                            
                            // Force a redraw
                            this.$nextTick(() => {
                                console.log('Video container should be visible now');
                                this.drawProjectedSkeleton();
                            });
                            
                            this.videoOverlayMode = true;
                            this.saveSettings();
                        }
                    })
                    .catch(error => {
                        console.warn(`Error loading sample video: ${error}`);
                    });
            }
  
            // Process the successfully loaded files
            successfulResults.forEach(async ({ data, blob, url }) => {
                // Get the filename from the URL
                const fileName = url.split('/').pop();
  
                if (blob) { // Handle .mot and .trc files
                  const file = new File([blob], fileName);
                  if (fileName.endsWith('.mot')) {
                    await this.processForceFile(file);
                  } else if (fileName.endsWith('.trc')) {
                    this.markersFile = file;
                    await this.loadMarkersFile();
                  }
                  return;
                }
  
                // Calculate FPS for this specific file
                const fileFps = this.calculateFrameRate(data.time);
  
                // Determine offset based on file type (apply mocap offsets only to mocap files)
                const isMocapFile = fileName.includes('mocap');
                const fileOffset = isMocapFile 
                    ? new THREE.Vector3(mocapOffsets.x, mocapOffsets.y, mocapOffsets.z)
                    : new THREE.Vector3(0, 0, 0);
                
                if (isMocapFile && (mocapOffsets.x !== 0 || mocapOffsets.y !== 0 || mocapOffsets.z !== 0)) {
                    console.log(`Applying offsets to ${fileName}:`, fileOffset);
                }
  
                // Create animation data with better names
                this.animations.push({
                    data: data,
                    offset: fileOffset,
                    rotation: new THREE.Euler(0, 0, 0, 'XYZ'),
                    fileName: fileName,
                    trialName: fileName.replace('sample_', '').replace('.json', ''),
                    visible: true,  // Ensure visibility is true by default
                    playable: true, // Add playable property, default to true
                    calculatedFps: fileFps // Store calculated FPS
                });
  
                // Extract marker data from sample JSON file for plotting
                this.extractMarkerDataFromJson(data, this.animations.length - 1, fileName);
  
                // Set up the trial and frames from the *first successfully loaded* animation
                if (this.animations.length === 1) {
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
        });
  
        // Ensure all color arrays are synchronized after initializing alpha values
        this.ensureColorArraysSync();
  
        this.animations.forEach((animation, index) => {
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
            this.updateDisplayedTime(0);
        } else {
            this.time = "0.000";
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
      console.log(`[updateBackgroundColor] Setting background color to ${color}`);
      this.backgroundColor = color;
  
      if (this.scene) {
        this.scene.background = new THREE.Color(color);
        if (this.renderer) {
          this.renderer.setClearColor(new THREE.Color(color));
          this.renderer.render(this.scene, this.camera);
        }
      }
  
      this.saveSettings(); // Explicitly save
    },
    updateGroundColor(color) {
        this.groundColor = color;
        if (this.groundMesh && this.groundMesh.material) {
            const isTransparent = this.groundOpacity < 1.0;
            // If not using texture, just set the color
            if (!this.useGroundTexture) {
                this.groundMesh.material.color = new THREE.Color(color);
                this.groundMesh.material.opacity = this.groundOpacity;
                this.groundMesh.material.transparent = isTransparent;
                this.groundMesh.material.depthWrite = !isTransparent;
            } else {
                // If using texture, create a new material with both texture and color
                const oldMaterial = this.groundMesh.material;
                const newMaterial = new THREE.MeshPhongMaterial({
                    map: this.groundTexture,
                    side: THREE.DoubleSide,
                    color: new THREE.Color(color),
                    opacity: this.groundOpacity,
                    transparent: isTransparent,
                    depthWrite: !isTransparent
                });

                this.groundMesh.material = newMaterial;

                // Dispose of old material
                if (oldMaterial) oldMaterial.dispose();
            }

            this.renderer.render(this.scene, this.camera);
        }
        this.saveSettings(); // Explicitly save
    },
    updateGroundOpacity(opacity) {
        this.groundOpacity = opacity;
        if (this.groundMesh && this.groundMesh.material) {
            // Update the material's opacity and transparency
            const isTransparent = opacity < 1.0;
            this.groundMesh.material.opacity = opacity;
            this.groundMesh.material.transparent = isTransparent;
            this.groundMesh.material.depthWrite = !isTransparent; // Disable depth write for transparent ground to fix view-angle issues

            this.renderer.render(this.scene, this.camera);
        }
        this.saveSettings(); // Explicitly save
    },

    updateGroundPosition() {
        if (this.groundMesh) {
            this.groundMesh.position.y = this.groundPositionY;
            if (this.renderer && this.scene && this.camera) {
                this.renderer.render(this.scene, this.camera);
            }
        }
        this.saveSettings();
    },
    toggleGroundTexture() {
        this.useGroundTexture = !this.useGroundTexture;

        if (this.groundMesh) {
            const oldMaterial = this.groundMesh.material;
            const isTransparent = this.groundOpacity < 1.0;

            if (this.useGroundTexture) {
                // Use textured material with either checkerboard or grid
                const textureToUse = this.useCheckerboard ? this.groundTexture : this.gridTexture;
                this.groundMesh.material = new THREE.MeshPhongMaterial({
                    map: textureToUse,
                    side: THREE.DoubleSide,
                    color: new THREE.Color(this.groundColor),
                    opacity: this.groundOpacity,
                    transparent: isTransparent,
                    depthWrite: !isTransparent
                });
            } else {
                // Use plain colored material
                this.groundMesh.material = new THREE.MeshPhongMaterial({
                    color: new THREE.Color(this.groundColor),
                    side: THREE.DoubleSide,
                    opacity: this.groundOpacity,
                    transparent: isTransparent,
                    depthWrite: !isTransparent
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
            const isTransparent = this.groundOpacity < 1.0;
            const newMaterial = new THREE.MeshPhongMaterial({
                map: this.useCheckerboard ? this.groundTexture : this.gridTexture,
                side: THREE.DoubleSide,
                color: new THREE.Color(this.groundColor),
                opacity: this.groundOpacity,
                transparent: isTransparent,
                depthWrite: !isTransparent
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
    toggleLights() {
        this.enableLights = !this.enableLights;
        
        // Update light intensities
        // When disabled, turn off directional/hemisphere/spot lights but boost ambient for uniform lighting
        if (this.lights.hemisphere) {
            this.lights.hemisphere.intensity = this.enableLights 
                ? (this.lights.hemisphereOriginalIntensity || 0.8) 
                : 0;
        }
        if (this.lights.directionals && this.lights.directionals.length > 0) {
            this.lights.directionals.forEach(light => {
                light.intensity = this.enableLights 
                    ? (this.lights.directionalOriginalIntensity || 0.5) 
                    : 0;
            });
        }
        if (this.lights.spotlight) {
            this.lights.spotlight.intensity = this.enableLights 
                ? (this.lights.spotlightOriginalIntensity || 1) 
                : 0;
        }
        // Boost ambient light when directional lights are disabled for uniform illumination
        if (this.lights.ambient) {
            this.lights.ambient.intensity = this.enableLights 
                ? (this.lights.ambientOriginalIntensity || 0.6) 
                : 2.0; // High ambient light for uniform color when directional lights are off
        }
        
        // No material conversion needed - keep using MeshPhongMaterial
        // The uniform ambient lighting will provide even illumination without shading
        
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
        
        this.saveSettings();
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
  
        // Set to high resolution for screenshot (4x)
        const scale = 4;
        const width = originalWidth * scale;
        const height = originalHeight * scale;
  
        // Helper to create an offscreen renderer
        const createOffscreenRenderer = (transparent = false) => {
            const renderer = new THREE.WebGLRenderer({
                antialias: true,
                alpha: transparent,
                preserveDrawingBuffer: true
            });
            renderer.setSize(width, height, false);
            renderer.setClearColor(transparent ? 0x000000 : originalClearColor, transparent ? 0 : originalClearAlpha);
            return renderer;
        };
  
        // Determine which captures to create based on user selection
        let captures = [];
        if (this.captureMode === 'both' || this.captureMode === 'normal') {
            captures.push({
                name: 'mocap-capture.png',
                background: originalBackground,
                showGround: originalGroundVisibility,
                transparent: false
            });
        }
        if (this.captureMode === 'both' || this.captureMode === 'transparent') {
            captures.push({
                name: 'mocap-capture-transparent.png',
                background: null,
                showGround: false,
                transparent: true
            });
        }
  
        // Save camera state
        const originalAspect = this.camera.aspect;
        const originalProjectionMatrix = this.camera.projectionMatrix.clone();
  
        // Force camera aspect ratio update for screenshot
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
  
        // Create download links for the selected version(s)
        captures.forEach(capture => {
            // Set background (null for transparent)
            this.scene.background = capture.background;
            // Set ground visibility
            if (this.groundMesh) {
                this.groundMesh.visible = capture.showGround;
            }
            // Use offscreen renderer for all captures
            const offscreenRenderer = createOffscreenRenderer(capture.transparent);
            offscreenRenderer.render(this.scene, this.camera);
            try {
                const dataURL = offscreenRenderer.domElement.toDataURL('image/png');
                // Create and trigger download
                const link = document.createElement('a');
                link.href = dataURL;
                link.download = capture.name;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } catch (e) {
                alert('Screenshot failed: ' + e.message);
            }
            offscreenRenderer.dispose();
        });
  
        // Restore original settings
        this.scene.background = originalBackground;
        if (this.groundMesh) {
            this.groundMesh.visible = originalGroundVisibility;
        }
        this.camera.aspect = originalAspect;
        this.camera.projectionMatrix.copy(originalProjectionMatrix);
        this.renderer.setClearColor(originalClearColor, originalClearAlpha);
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
            const jsonFileName = `${this.osimFile.name.replace('.osim', '')}.json`;
            const jsonFile = new File([jsonBlob], jsonFileName, { type: 'application/json' });
            
            // Store the converted JSON data for later download
            this.$set(this.convertedJsonDataMap, jsonFileName, JSON.parse(JSON.stringify(data)));
            
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
            // console.log('Processing converted JSON file...');
            this.handleFileUpload(fakeEvent);
            
            // Clear the selected files after successful conversion
            this.osimFile = null;
            this.motFile = null;
            
            // console.log('Conversion completed. Scene state:', {
            //   scene: !!this.scene,
            //   animations: this.animations.length,
            //   frames: this.frames ? this.frames.length : 0
            // });
            
            // Give more time for scene initialization and ensure it's properly set up
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Force scene initialization if it still doesn't exist
            if (!this.scene) {
              // console.log('Scene still not initialized after conversion, forcing initialization...');
              this.$nextTick(() => {
                this.initScene();
              });
              // Wait a bit more for the scene to initialize
              await new Promise(resolve => setTimeout(resolve, 300));
              
              // Check again and log the final state (commented out to reduce console spam)
              // console.log('Final scene state after forced initialization:', {
              //   scene: !!this.scene,
              //   renderer: !!this.renderer,
              //   camera: !!this.camera,
              //   animations: this.animations.length,
              //   frames: this.frames ? this.frames.length : 0
              // });
            }
  
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
          // Expand the section when enabling timelapse mode
          this.showTimelapseDetails = true;
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
  
      restoreTimelapseFromShare(timelapseData) {
        // Enable timelapse mode
        this.timelapseMode = true;
        this.timelapseInterval = timelapseData.interval || 5;
        this.timelapseOpacity = timelapseData.opacity !== undefined ? timelapseData.opacity : 0.3;
        
        // Clear any existing timelapse meshes
        this.clearTimelapse();
        
        // Reset counter
        this.timelapseCounter = 1;
        
        // Restore each timelapse mesh
        if (timelapseData.meshes && Array.isArray(timelapseData.meshes)) {
          timelapseData.meshes.forEach((meshData) => {
            const { frame, animIndex, body, geom, position, rotation, scale } = meshData;
            
            // Get the original mesh to clone from
            const originalMesh = this.meshes[`anim${animIndex}_${body}${geom}`];
            if (!originalMesh) {
              console.warn(`Could not find original mesh for timelapse: anim${animIndex}_${body}${geom}`);
              return;
            }
            
            // Create the timelapse mesh
            const meshId = this.timelapseCounter++;
            const meshKey = `timelapse_${meshId}`;
            
            const clone = originalMesh.clone();
            
            // Set position, rotation, and scale from stored data
            clone.position.set(position[0], position[1], position[2]);
            clone.quaternion.set(rotation[0], rotation[1], rotation[2], rotation[3]);
            clone.scale.set(scale[0], scale[1], scale[2]);
            
            // Apply timelapse opacity
            clone.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                const material = child.material.clone();
                material.transparent = true;
                material.opacity = this.timelapseOpacity;
                child.material = material;
              }
            });
            
            // Add to scene
            this.scene.add(clone);
            
            // Store metadata
            this.timelapseMeshes[meshKey] = {
              mesh: clone,
              frame: frame,
              animIndex: animIndex,
              body: body,
              geom: geom,
              id: meshId
            };
            
            // Update timelapse groups
            if (!this.timelapseGroups[animIndex]) {
              this.$set(this.timelapseGroups, animIndex, []);
            }
            if (!this.timelapseGroups[animIndex].includes(frame)) {
              this.timelapseGroups[animIndex].push(frame);
              this.timelapseGroups[animIndex].sort((a, b) => a - b);
            }
            
            this.timelapseFrameCount++;
          });
        }
        
        // Re-render the scene
        if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
        }
        
        console.log(`Restored ${this.timelapseFrameCount} timelapse meshes from shared data`);
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
        this.disposeVideoPlane();
    },
    clearConversionError() {
        this.conversionError = null;
        // Also make sure files are cleared when error is dismissed
        this.osimFile = null;
        this.motFile = null;
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
          this.drawProjectedSkeleton();
        });

        this.videoOverlayMode = true;
        this.saveSettings();
      }
    },
  
  handleVideoMetadata() {
      if (this.videoPreviewElement) {
        this.videoDuration = this.videoPreviewElement.duration;
        if (this.videoPreviewElement.videoWidth && this.videoPreviewElement.videoHeight) {
          this.cameraImageSize = {
            width: this.videoPreviewElement.videoWidth,
            height: this.videoPreviewElement.videoHeight
          };
        }
        console.log('Video duration:', this.videoDuration);
        
        // Trigger video plane creation/update now that video is ready
        if (this.videoPlaneSettings.visible && this.cameraExtrinsicsMap && Object.keys(this.cameraExtrinsicsMap).length > 0) {
          this.$nextTick(() => {
            this.ensureVideoPlane();
          });
        }
  
      // Estimate video frame rate - most common values are 30 or 60 fps
      // If the animation fps is much different than video, it could cause sync issues
      if (this.videoFile && this.videoFile.name) {
        // Try to extract fps from video name if it's included (like video_30fps.mp4)
        const fpsMatch = this.videoFile.name.match(/(\d+)fps/i);
        if (fpsMatch && fpsMatch[1]) {
          this.videoFrameRate = parseInt(fpsMatch[1], 10);
          console.log(`Detected video frame rate from filename: ${this.videoFrameRate}fps`);
        } else {
          // Default estimate based on common values
          this.videoFrameRate = 30;
          console.log(`Using default video frame rate: ${this.videoFrameRate}fps`);
        }
  
        // If animation frame rate is drastically different, log a warning
        if (Math.abs(this.frameRate - this.videoFrameRate) > 10) {
          console.warn(`Animation frame rate (${this.frameRate}fps) differs significantly from video (${this.videoFrameRate}fps). This may cause sync issues.`);
        }
      }
  
      // Set initial video position based on current frame
      if (this.frames.length > 0) {
        const totalFrames = this.frames.length - 1;
        const videoTimePosition = (this.frame / totalFrames) * this.videoDuration;
        this.videoPreviewElement.currentTime = videoTimePosition;
      }
      
      // Set video playback rate to match current playSpeed
      if (this.videoPreviewElement && typeof this.videoPreviewElement.playbackRate !== 'undefined') {
        this.videoPreviewElement.playbackRate = this.playSpeed;
        console.log(`Video playback rate set to: ${this.playSpeed}x on metadata load`);
      }
      
      if (this.videoPlaneSettings.visible) {
        this.$nextTick(() => this.ensureVideoPlane());
      }
      }
    },
  
  handleVideoTimeUpdate() {
    // Only sync if playing and not during a scrubbing operation
    if (this.playing && this.videoPreviewElement && this.frames.length > 0 && this.videoDuration > 0) {
      // Get current video time
      const videoTime = this.videoPreviewElement.currentTime;
  
      // Calculate what frame we should be on based on video time
      const frameProgress = videoTime / this.videoDuration;
      const totalFrames = this.frames.length - 1;
      const targetFrame = Math.round(frameProgress * totalFrames);
  
      // If we're more than 1 frame off, sync the animation
      if (Math.abs(targetFrame - this.frame) > 1) {
        console.log(`Video sync: Adjusting animation from frame ${this.frame} to ${targetFrame}`);
        // Update frame without calling onNavigate to avoid recursive sync
        const clampedTarget = Math.min(Math.max(targetFrame, 0), totalFrames);
        this.frame = clampedTarget;
        this.updateDisplayedTime(clampedTarget);
        this.frameAccumulator = 0;
  
        // Render the updated frame
        this.animateOneFrame();
      }

      this.$nextTick(() => this.drawProjectedSkeleton());
    }
  },

  toggleVideoOverlay() {
    this.videoOverlayMode = !this.videoOverlayMode;
    this.saveSettings();
    if (this.videoOverlayMode) {
      this.$nextTick(() => this.drawProjectedSkeleton());
    } else {
      this.clearProjectionCanvas();
    }
  },

  onVideoOverlayOpacityInput(value) {
    const clamped = Math.min(Math.max(Number(value) || 0, 0), 100);
    const normalized = parseFloat((clamped / 100).toFixed(2));
    if (this.videoOverlayOpacity !== normalized) {
      this.videoOverlayOpacity = normalized;
      this.saveSettings();
      if (this.videoOverlayMode) {
        this.drawProjectedSkeleton();
      }
    }
  },

  onVideoPlaneOpacityInput(value) {
    const clamped = Math.min(Math.max(Number(value) || 0, 10), 100);
    const normalized = parseFloat((clamped / 100).toFixed(2));
    if (this.videoPlaneSettings.opacity !== normalized) {
      this.videoPlaneSettings.opacity = normalized;
    }
  },

  // ---------------------------------------------------------------------------
  // Video plane helper utilities
  // ---------------------------------------------------------------------------

  toPlainNumeric(value) {
    if (value === null || value === undefined) {
      return null;
    }
    if (typeof value === 'number') {
      return Number.isFinite(value) ? value : null;
    }
    if (typeof value === 'string' && value.trim() !== '') {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : null;
    }
    if (Array.isArray(value)) {
      return value.map(item => this.toPlainNumeric(item));
    }
    if (ArrayBuffer.isView(value) && typeof value.length === 'number') {
      return Array.from(value, item => this.toPlainNumeric(item));
    }
    return value;
  },

  flattenNumericArray(value) {
    if (value === null || value === undefined) {
      return null;
    }
    let elements;
    if (Array.isArray(value)) {
      elements = value.flat(Infinity);
    } else if (ArrayBuffer.isView(value) && typeof value.length === 'number') {
      elements = Array.from(value);
    } else {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) {
        return [parsed];
      }
      return null;
    }
    const numeric = elements
      .map(element => Number(element))
      .filter(element => Number.isFinite(element));
    return numeric.length ? numeric : null;
  },

  normalizeMatrix3x3(value) {
    if (!value) {
      return null;
    }
    const plain = this.toPlainNumeric(value);
    const isMatrix = matrix =>
      Array.isArray(matrix) &&
      matrix.length === 3 &&
      matrix.every(
        row =>
          Array.isArray(row) &&
          row.length === 3 &&
          row.every(cell => Number.isFinite(Number(cell)))
      );
    if (isMatrix(plain)) {
      return plain.map(row => row.map(cell => Number(cell)));
    }
    if (Array.isArray(plain) && plain.length === 9) {
      const numeric = plain.map(cell => Number(cell));
      if (numeric.every(cell => Number.isFinite(cell))) {
        return [
          [numeric[0], numeric[1], numeric[2]],
          [numeric[3], numeric[4], numeric[5]],
          [numeric[6], numeric[7], numeric[8]]
        ];
      }
    }
    return null;
  },

  normalizeImageSize(value) {
    if (!value) {
      return null;
    }
    if (typeof value === 'object' && !Array.isArray(value) && value.width !== undefined && value.height !== undefined) {
      const width = Number(value.width);
      const height = Number(value.height);
      return Number.isFinite(width) && Number.isFinite(height)
        ? { width, height }
        : null;
    }
    const flatten = Array.isArray(value)
      ? value.flat(Infinity)
      : (ArrayBuffer.isView(value) && typeof value.length === 'number'
          ? Array.from(value)
          : null);
    if (flatten) {
      const numbers = flatten
        .map(entry => Number(entry))
        .filter(entry => Number.isFinite(entry));
      if (numbers.length >= 2) {
        return { width: numbers[0], height: numbers[1] };
      }
    }
    return null;
  },

  extractCameraRotationFrame(raw, frameIndex = 0) {
    if (!raw) {
      return null;
    }
    const clampIndex = (length) => Math.min(Math.max(frameIndex, 0), Math.max(0, length - 1));
    const isMatrix = matrix =>
      Array.isArray(matrix) &&
      matrix.length === 3 &&
      matrix.every(
        row =>
          Array.isArray(row) &&
          row.length === 3 &&
          row.every(cell => Number.isFinite(Number(cell)))
      );
    let value = this.toPlainNumeric(raw);
    if (!value) {
      return null;
    }
    while (Array.isArray(value) && value.length === 1 && !isMatrix(value[0])) {
      value = value[0];
    }
    if (isMatrix(value)) {
      return value.map(row => row.map(cell => Number(cell)));
    }
    if (Array.isArray(value)) {
      const candidate = value[clampIndex(value.length)];
      if (candidate !== undefined) {
        let frameValue = candidate;
        while (Array.isArray(frameValue) && frameValue.length === 1 && !isMatrix(frameValue[0])) {
          frameValue = frameValue[0];
        }
        if (isMatrix(frameValue)) {
          return frameValue.map(row => row.map(cell => Number(cell)));
        }
      }
    }
    if (Array.isArray(value) && value.length === 9) {
      const numeric = value.map(cell => Number(cell));
      if (numeric.every(cell => Number.isFinite(cell))) {
        return [
          [numeric[0], numeric[1], numeric[2]],
          [numeric[3], numeric[4], numeric[5]],
          [numeric[6], numeric[7], numeric[8]]
        ];
      }
    }
    return null;
  },

  extractCameraTranslationFrame(raw, frameIndex = 0) {
    if (!raw) {
      return null;
    }
    const clampIndex = (length) => Math.min(Math.max(frameIndex, 0), Math.max(0, length - 1));
    const isVector = vec =>
      Array.isArray(vec) &&
      vec.length === 3 &&
      vec.every(component => Number.isFinite(Number(component)));
    let value = this.toPlainNumeric(raw);
    if (!value) {
      return null;
    }
    while (Array.isArray(value) && value.length === 1 && !isVector(value[0])) {
      value = value[0];
    }
    if (isVector(value)) {
      return value.map(component => Number(component));
    }
    if (Array.isArray(value)) {
      const candidate = value[clampIndex(value.length)];
      if (candidate !== undefined) {
        let frameValue = candidate;
        while (Array.isArray(frameValue) && frameValue.length === 1 && !isVector(frameValue[0])) {
          frameValue = frameValue[0];
        }
        if (isVector(frameValue)) {
          return frameValue.map(component => Number(component));
        }
      }
    }
    if (Array.isArray(value) && value.length === 3) {
      const numeric = value.map(component => Number(component));
      return numeric.every(component => Number.isFinite(component)) ? numeric : null;
    }
    return null;
  },

  resolveCameraExtrinsics() {
    if (!this.cameraExtrinsicsMap) {
      return null;
    }
    if (this.cameraExtrinsicsMap['standalone_intrinsics']) {
      return {
        key: 'standalone_intrinsics',
        extrinsics: this.cameraExtrinsicsMap['standalone_intrinsics']
      };
    }
    if (this.smplSequences && this.smplSequences.length > 0) {
      for (const sequence of this.smplSequences) {
        const entry = this.cameraExtrinsicsMap[sequence.id];
        if (entry) {
          return { key: sequence.id, extrinsics: entry };
        }
      }
    }
    return null;
  },

  getCameraPoseFromExtrinsics(extrinsics, frameIndex = 0) {
    if (!extrinsics || (!extrinsics.cam_R && !extrinsics.cam_T)) {
      return null;
    }
    const rotationArray = this.extractCameraRotationFrame(extrinsics.cam_R, frameIndex);
    const translationArray = this.extractCameraTranslationFrame(extrinsics.cam_T, frameIndex);
    if (!rotationArray || !translationArray) {
      return null;
    }

    // Coordinate convention: cam_R is world→camera, cam_T is camera center in world
    // X_w = R * X_c + t  (where t is camera center)
    const R_cam = new THREE.Matrix3().set(
      rotationArray[0][0], rotationArray[0][1], rotationArray[0][2],
      rotationArray[1][0], rotationArray[1][1], rotationArray[1][2],
      rotationArray[2][0], rotationArray[2][1], rotationArray[2][2]
    );

    // cam_T is already the camera center in world coordinates
    const cameraPosition = new THREE.Vector3(
      Number(translationArray[0]) || 0,
      Number(translationArray[1]) || 0,
      Number(translationArray[2]) || 0
    );

    // Camera axes in world coordinates: R @ [axis in camera coords]
    const cameraForward = new THREE.Vector3(0, 0, 1).applyMatrix3(R_cam).normalize();
    const cameraRight = new THREE.Vector3(1, 0, 0).applyMatrix3(R_cam).normalize();
    const cameraUp = new THREE.Vector3(0, -1, 0).applyMatrix3(R_cam).normalize(); // Y-axis flipped (image Y down, world Y up)
    const planeNormal = cameraForward.clone().negate();

    // Debug logging for camera position
    if (frameIndex === 0) {
      console.log('[Camera Pose Debug]', {
        cam_T: translationArray,
        cameraPosition: cameraPosition.toArray(),
        cameraPosition_magnitude: cameraPosition.length().toFixed(3),
        cameraForward: cameraForward.toArray(),
        cameraUp: cameraUp.toArray()
      });
    }

    return {
      R_cam,
      cameraPosition,
      cameraForward,
      cameraRight,
      cameraUp,
      planeNormal
    };
  },

  computeVideoPlaneFrame(distanceInput, frameIndex = 0) {
    const extrResult = this.resolveCameraExtrinsics();
    if (!extrResult) {
      this.videoPlaneFrameCache = null;
      return null;
    }
    const pose = this.getCameraPoseFromExtrinsics(extrResult.extrinsics, frameIndex);
    if (!pose) {
      this.videoPlaneFrameCache = null;
      return null;
    }

    const intrinsics = Array.isArray(this.cameraIntrinsics)
      ? this.cameraIntrinsics
      : this.normalizeMatrix3x3(this.cameraIntrinsics);

    const videoElement = this.videoPreviewElement;
    const fallbackWidth = videoElement?.videoWidth || 0;
    const fallbackHeight = videoElement?.videoHeight || 0;
    const normalizedSize = this.normalizeImageSize(this.cameraImageSize);
    const sliderDistanceMin = 0.05;
    const sliderDistanceMax = 50.0;
    const sliderWidthMax = 100.0;

    if (!intrinsics) {
      this.videoPlaneFrameCache = null;
      return null;
    }

    const fx = Number(intrinsics[0][0]) || 0;
    const fy = Number(intrinsics[1][1]) || 0;
    const cx = Number(intrinsics[0][2]) || 0;
    const cy = Number(intrinsics[1][2]) || 0;
    if (fx === 0 || fy === 0) {
      this.videoPlaneFrameCache = null;
      return null;
    }

    let widthPx = normalizedSize && Number.isFinite(Number(normalizedSize.width))
      ? Number(normalizedSize.width)
      : 0;
    let heightPx = normalizedSize && Number.isFinite(Number(normalizedSize.height))
      ? Number(normalizedSize.height)
      : 0;

    if (fallbackWidth && fallbackHeight) {
      widthPx = fallbackWidth;
      heightPx = fallbackHeight;
    } else {
      if (!widthPx && fallbackWidth) {
        widthPx = fallbackWidth;
      }
      if (!heightPx && fallbackHeight) {
        heightPx = fallbackHeight;
      }
    }

    if (!widthPx || !heightPx) {
      this.videoPlaneFrameCache = null;
      return null;
    }

    const safeFrameIndex = Math.max(0, Math.floor(Number.isFinite(frameIndex) ? frameIndex : 0));
    let subjectPoint = null;
    if (Array.isArray(this.smplSequences) && this.smplSequences.length > 0) {
      for (const seq of this.smplSequences) {
        if (!seq || !seq.joints || !seq.jointCount) {
          continue;
        }
        const jointStride = seq.jointStride || (seq.jointCount * 3);
        const totalFrames = jointStride > 0 ? Math.floor(seq.joints.length / jointStride) : 0;
        if (totalFrames <= 0) {
          continue;
        }
        const clampedFrame = Math.min(safeFrameIndex, totalFrames - 1);
        const jointIndex = 0; // pelvis/root
        const start = clampedFrame * jointStride + jointIndex * 3;
        if (start + 2 < seq.joints.length) {
          subjectPoint = new THREE.Vector3(
            seq.joints[start],
            seq.joints[start + 1],
            seq.joints[start + 2]
          );
          break;
        }
      }
    }
    if (!subjectPoint) {
      subjectPoint = pose.cameraPosition.clone().add(
        pose.cameraForward.clone().multiplyScalar(Math.max(1, Number(distanceInput) || 1))
      );
    }

    const cameraToSubject = subjectPoint.clone().sub(pose.cameraPosition);
    const subjectDepth = cameraToSubject.dot(pose.cameraForward);

    let effectiveDistance = Math.min(
      sliderDistanceMax,
      Math.max(sliderDistanceMin, Number(distanceInput) || 1)
    );
    if (Number.isFinite(subjectDepth) && subjectDepth > 0.05) {
      if (!this.videoPlaneDistanceLockedByUser) {
        // Place the plane at the actual subject depth for physical accuracy
        // This represents the camera's view plane at the distance where the subject was captured
        const autoDistance = Math.min(
          sliderDistanceMax,
          Math.max(sliderDistanceMin, subjectDepth)
        );
        effectiveDistance = autoDistance;
        if (!Number.isFinite(this.videoPlaneSettings.distance) ||
            Math.abs(this.videoPlaneSettings.distance - autoDistance) > 1e-3) {
          this.suppressVideoPlaneDistanceWatcher = true;
          this.videoPlaneSettings.distance = parseFloat(autoDistance.toFixed(3));
          this.$nextTick(() => {
            this.suppressVideoPlaneDistanceWatcher = false;
          });
        }
      }
    }

    // Debug logging for depth calculation
    if (safeFrameIndex === 0) {
      console.log('[Video Plane Debug]', {
        subjectPoint: subjectPoint.toArray(),
        cameraPosition: pose.cameraPosition.toArray(),
        cameraToSubject: cameraToSubject.toArray(),
        cameraToSubject_magnitude: cameraToSubject.length().toFixed(3),
        subjectDepth: subjectDepth.toFixed(3),
        effectiveDistance: effectiveDistance.toFixed(3),
        ratio: (effectiveDistance / subjectDepth).toFixed(3)
      });
    }

    // Place the image plane very close to the camera (represents camera sensor/viewfinder)
    // The SMPL will be at the full captured distance from this plane
    // Use a very small distance to avoid z-fighting but keep plane essentially at camera
    const imagePlaneDistance = 0.01; // meters from camera (essentially at camera position)
    
    // Calculate plane dimensions at this fixed distance
    const xLeft = (-cx) * imagePlaneDistance / fx;
    const xRight = (widthPx - cx) * imagePlaneDistance / fx;
    const yTop = (-cy) * imagePlaneDistance / fy;
    const yBottom = (heightPx - cy) * imagePlaneDistance / fy;

    const cornersCam = [
      new THREE.Vector3(xLeft, yTop, imagePlaneDistance),      // Top-left
      new THREE.Vector3(xRight, yTop, imagePlaneDistance),     // Top-right
      new THREE.Vector3(xLeft, yBottom, imagePlaneDistance),   // Bottom-left
      new THREE.Vector3(xRight, yBottom, imagePlaneDistance)   // Bottom-right
    ];

    const centerCam = cornersCam[0].clone().add(cornersCam[3]).multiplyScalar(0.5);
    const baseWidth = xRight - xLeft;
    const baseHeight = yBottom - yTop;

    // Calculate the "virtual" width at subject depth for proper scaling
    const virtualWidthAtSubject = baseWidth * (effectiveDistance / imagePlaneDistance);
    
    if (Number.isFinite(virtualWidthAtSubject) && virtualWidthAtSubject > 0) {
      this.videoPlaneBaseWidth = virtualWidthAtSubject;
      if (!this.videoPlaneWidthLockedByUser) {
        const currentWidth = Number(this.videoPlaneSettings.width);
        const autoWidth = Math.min(sliderWidthMax, Math.max(0.1, virtualWidthAtSubject));
        if (!Number.isFinite(currentWidth) || Math.abs(currentWidth - autoWidth) > 1e-3) {
          this.suppressVideoPlaneWidthWatcher = true;
          this.videoPlaneSettings.width = parseFloat(autoWidth.toFixed(3));
          this.$nextTick(() => {
            this.suppressVideoPlaneWidthWatcher = false;
          });
        }
      }
    }

    const targetWidth = Math.min(
      sliderWidthMax,
      Math.max(0.05, Number(this.videoPlaneSettings.width) || 1)
    );
    // Scale from actual baseWidth to targetWidth (since plane is at different distance)
    const scale = Number.isFinite(targetWidth) && baseWidth > 0
      ? Math.max(0.05, targetWidth / baseWidth)
      : 1;

    const centerX = centerCam.x;
    const centerY = centerCam.y;

    const localCorners = cornersCam.map(corner => new THREE.Vector3(
      (corner.x - centerX) * scale,
      (centerY - corner.y) * scale,
      0
    ));

    // Position the plane center in world space
    // Formula: P_plane = t_f + R @ [cx, cy, d] where t_f is camera center
    // Transform from camera space to world space: X_w = R * X_c + t
    const planeCenterWorld = centerCam.clone()
      .applyMatrix3(pose.R_cam)
      .add(pose.cameraPosition);

    // Debug: verify plane positioning and scaling
    if (safeFrameIndex === 0) {
      const cameraToPlaneVec = planeCenterWorld.clone().sub(pose.cameraPosition);
      const planeDistanceFromCamera = cameraToPlaneVec.dot(pose.cameraForward);
      const planeToSubjectVec = subjectPoint.clone().sub(planeCenterWorld);
      const subjectDistanceFromPlane = planeToSubjectVec.length();
      const subjectDepthFromPlane = planeToSubjectVec.dot(pose.cameraForward);
      console.log('[Plane Position Debug]', {
        imagePlaneDistance: imagePlaneDistance.toFixed(3),
        planeDistanceFromCamera: planeDistanceFromCamera.toFixed(3),
        subjectDepth: subjectDepth.toFixed(3),
        subjectDistanceFromPlane: subjectDistanceFromPlane.toFixed(3),
        subjectDepthFromPlane: subjectDepthFromPlane.toFixed(3),
        expectedSubjectDepthFromPlane: (subjectDepth - imagePlaneDistance).toFixed(3),
        baseWidth: baseWidth.toFixed(3),
        virtualWidthAtSubject: virtualWidthAtSubject.toFixed(3),
        scale: scale.toFixed(3),
        planeCenterWorld: planeCenterWorld.toArray(),
        subjectPoint: subjectPoint.toArray()
      });
    }

    const frame = {
      extrinsicsKey: extrResult.key,
      pose,
      effectiveDistance,
      cornersCam,
      localCorners,
      planeCenterWorld,
      cameraRight: pose.cameraRight.clone(),
      cameraUp: pose.cameraUp.clone(),
      planeNormal: pose.planeNormal.clone(),
      baseWidth,
      baseHeight,
      pixelSize: { width: widthPx, height: heightPx },
      intrinsics,
      principalPoint: { cx, cy },
      subjectDepth
    };

    this.videoPlaneFrameCache = frame;
    return frame;
  },

  buildVideoPlaneGeometry(frame) {
    if (!frame || !frame.localCorners || frame.localCorners.length !== 4) {
      return null;
    }
    const [topLeft, topRight, bottomLeft, bottomRight] = frame.localCorners;
    const positions = new Float32Array([
      topLeft.x, topLeft.y, 0,
      bottomLeft.x, bottomLeft.y, 0,
      topRight.x, topRight.y, 0,
      bottomLeft.x, bottomLeft.y, 0,
      bottomRight.x, bottomRight.y, 0,
      topRight.x, topRight.y, 0
    ]);
    const uvs = new Float32Array([
      0, 1,
      0, 0,
      1, 1,
      0, 0,
      1, 0,
      1, 1
    ]);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    geometry.computeVertexNormals();
    return geometry;
  },

  ensureVideoPlane() {
    if (!this.videoPlaneSettings.visible || !this.scene || !this.camera || !this.videoFile) {
      console.log('Video plane not ready:', {
        visible: this.videoPlaneSettings.visible,
        scene: !!this.scene,
        camera: !!this.camera,
        videoFile: !!this.videoFile
      });
      return;
    }
    const videoElement = this.videoPreviewElement;
    if (!videoElement || videoElement.readyState < 2) {
      console.log('Video element not ready:', {
        videoElement: !!videoElement,
        readyState: videoElement ? videoElement.readyState : 'N/A'
      });
      return;
    }
    console.log('Ensuring video plane is created and visible');

    if (!this.videoTexture) {
      this.videoTexture = new THREE.VideoTexture(videoElement);
      this.videoTexture.encoding = THREE.sRGBEncoding;
      this.videoTexture.generateMipmaps = false;
      this.videoTexture.minFilter = THREE.LinearFilter;
      this.videoTexture.magFilter = THREE.LinearFilter;
    }

    if (!this.videoPlane) {
      const geometry = new THREE.PlaneGeometry(1, 1);
      const material = new THREE.MeshBasicMaterial({
        map: this.videoTexture,
        transparent: true,
        opacity: this.videoPlaneSettings.opacity,
        side: THREE.DoubleSide,
        depthWrite: false
      });
      this.videoPlane = new THREE.Mesh(geometry, material);
      this.videoPlane.renderOrder = 1;
      this.videoPlane.frustumCulled = false;
      this.scene.add(this.videoPlane);
    } else if (this.videoPlane.material && this.videoPlane.material.map !== this.videoTexture) {
      this.videoPlane.material.map = this.videoTexture;
      this.videoPlane.material.needsUpdate = true;
    }

    this.updateVideoPlaneGeometry();
    this.updateVideoPlaneMaterial();
    this.updateVideoPlaneTransform();
  },

  updateVideoPlaneGeometry() {
    if (!this.videoPlane) {
      return;
    }
    const distance = Math.max(0.05, Number(this.videoPlaneSettings.distance) || 1);
    const frameIndex = Math.max(0, Math.floor(Number.isFinite(this.frame) ? this.frame : 0));
    const frame = this.computeVideoPlaneFrame(distance, frameIndex);
    if (frame) {
      const geometry = this.buildVideoPlaneGeometry(frame);
      if (geometry) {
        if (this.videoPlane.geometry) {
          this.videoPlane.geometry.dispose();
        }
        this.videoPlane.geometry = geometry;
        return;
      }
    }

    // Fallback geometry when camera information is unavailable
    const aspect = this.getVideoAspect();
    const width = Math.max(0.1, Number(this.videoPlaneSettings.width) || 3);
    const height = width / aspect;
    const geometry = new THREE.PlaneGeometry(width, height);
    if (this.videoPlane.geometry) {
      this.videoPlane.geometry.dispose();
    }
    this.videoPlane.geometry = geometry;
    this.videoPlaneFrameCache = null;
  },

  updateVideoPlaneMaterial() {
    if (!this.videoPlane) {
      return;
    }
    const material = this.videoPlane.material;
    if (material) {
      material.opacity = this.videoPlaneSettings.opacity;
      material.transparent = material.opacity < 0.999;
      material.depthWrite = false;
      material.needsUpdate = true;
    }
  },

  updateVideoPlaneTransform() {
    if (!this.videoPlane || !this.camera) {
      return;
    }
    const shouldBeVisible = !!(this.videoPlaneSettings.visible && this.videoFile);
    this.videoPlane.visible = shouldBeVisible;
    if (!shouldBeVisible) {
      return;
    }

    let distanceSetting = Math.max(0.05, Number(this.videoPlaneSettings.distance) || 1);
    const frameIndex = Math.max(0, Math.floor(Number.isFinite(this.frame) ? this.frame : 0));
    let frame = this.videoPlaneFrameCache;
    if (!frame || Math.abs(frame.distance - distanceSetting) > 1e-3) {
      frame = this.computeVideoPlaneFrame(distanceSetting, frameIndex);
      if (frame) {
        distanceSetting = frame.distance;
      }
    }

    if (frame) {
      this.videoPlane.position.copy(frame.planeCenterWorld);
      const planeMatrix = new THREE.Matrix4().makeBasis(
        frame.cameraRight.clone().normalize(),
        frame.cameraUp.clone().normalize(),
        frame.planeNormal.clone().normalize()
      );
      this.videoPlane.quaternion.setFromRotationMatrix(planeMatrix);
      this.videoPlane.updateMatrixWorld(true);
      this.videoPlaneExtrinsicsKey = `${frame.extrinsicsKey || 'camera'}_frame0`;
      this._lastAppliedPlaneDistance = distanceSetting;
      this.videoPlaneSettings.followCamera = false;
      return;
    }

    // Fallback: follow viewer camera if extrinsics are unavailable
    this.videoPlaneFrameCache = null;
    this.videoPlaneExtrinsicsKey = null;
    this._lastAppliedPlaneDistance = undefined;
    if (!this._videoPlaneCameraPosition) {
      this._videoPlaneCameraPosition = new THREE.Vector3();
      this._videoPlaneCameraDirection = new THREE.Vector3();
      this._videoPlaneTempVec = new THREE.Vector3();
    }
    const cameraPosition = this._videoPlaneCameraPosition;
    const cameraDirection = this._videoPlaneCameraDirection;
    this.camera.getWorldPosition(cameraPosition);
    this.camera.getWorldDirection(cameraDirection);

    if (this.videoPlaneSettings.followCamera) {
      const planePosition = this._videoPlaneTempVec;
      const fallbackDistance = Number(this.videoPlaneSettings.distance) || 0;
      planePosition.copy(cameraDirection).multiplyScalar(fallbackDistance);
      planePosition.add(cameraPosition);
      this.videoPlane.position.copy(planePosition);
    }

    this.videoPlane.lookAt(cameraPosition);
  },

  disposeVideoPlane() {
    if (this.videoPlane) {
      if (this.scene) {
        this.scene.remove(this.videoPlane);
      }
      if (this.videoPlane.geometry) {
        this.videoPlane.geometry.dispose();
      }
      const material = this.videoPlane.material;
      if (material) {
        if (Array.isArray(material)) {
          material.forEach(mat => mat.dispose && mat.dispose());
        } else if (material.dispose) {
          material.dispose();
        }
      }
      this.videoPlane = null;
    }
    if (this.videoTexture) {
      this.videoTexture.dispose();
      this.videoTexture = null;
    }
    this.videoPlaneFrameCache = null;
    this.videoPlaneBaseWidth = null;
    this.videoPlaneWidthLockedByUser = false;
    this.videoPlaneDistanceLockedByUser = false;
    this.suppressVideoPlaneWidthWatcher = false;
    this.suppressVideoPlaneDistanceWatcher = false;
    this._lastAppliedPlaneDistance = undefined;
    this.videoPlaneExtrinsicsKey = null;
  },

  getVideoAspect() {
    const videoElement = this.videoPreviewElement;
    if (videoElement && videoElement.videoWidth && videoElement.videoHeight) {
      const aspect = videoElement.videoWidth / videoElement.videoHeight;
      if (Number.isFinite(aspect) && aspect > 0) {
        return aspect;
      }
    }
    return 16 / 9;
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
    this.disposeVideoPlane();
    this.videoFile = null;
    this.videoUrl = null;
    this.videoDuration = 0;
    console.log('Video closed');

      // Reset position and size for next time
      this.videoPosition = { x: 20, y: 20 };
      this.videoSize = { width: 300, height: 'auto' };
      this.clearProjectionCanvas();
      this.saveSettings();
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
        } else if (event.data.type === 'setPlaySpeed') {
          // Handle playback speed setting
          if (typeof event.data.speed === 'number' && isFinite(event.data.speed)) {
            // Clamp speed between 0.1 and 4.0 to match keyboard shortcut limits
            const clampedSpeed = Math.max(0.1, Math.min(4.0, event.data.speed));
            this.playSpeed = clampedSpeed;
          }
        } else if (event.data.type === 'next') {
          // Navigate to next frame (equivalent to step-forward button)
          if (this.frames && this.frames.length > 0) {
            const nextFrame = Math.min(this.frames.length - 1, this.frame + 1);
            this.playing = false; // Stop playback when manually navigating
            this.onNavigate(nextFrame);
          }
        } else if (event.data.type === 'previous') {
          // Navigate to previous frame (equivalent to step-backward button)
          if (this.frames && this.frames.length > 0) {
            const prevFrame = Math.max(0, this.frame - 1);
            this.playing = false; // Stop playback when manually navigating
            this.onNavigate(prevFrame);
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

      if (event.shiftKey && this.handleSubjectNudge(event.code, event)) {
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
          if (settings.groundOpacity !== undefined) this.groundOpacity = settings.groundOpacity;
          if (settings.groundPositionY !== undefined) this.groundPositionY = settings.groundPositionY;
          if (settings.showGround !== undefined) this.showGround = settings.showGround;
          if (settings.useGroundTexture !== undefined) this.useGroundTexture = settings.useGroundTexture;
          if (settings.useCheckerboard !== undefined) this.useCheckerboard = settings.useCheckerboard;
          if (settings.playSpeed !== undefined) this.playSpeed = settings.playSpeed;
          if (settings.recordingFormat) this.recordingFormat = settings.recordingFormat;
          if (settings.videoBitrate) this.videoBitrate = settings.videoBitrate;
          if (settings.loopCount !== undefined) this.loopCount = settings.loopCount;
          if (settings.isLooping !== undefined) this.isLooping = settings.isLooping;
          if (settings.captureMode) this.captureMode = settings.captureMode;
                  // Marker settings removed
          if (settings.showSidebar !== undefined) this.showSidebar = settings.showSidebar;
          if (settings.videoPosition) this.videoPosition = settings.videoPosition;
          if (settings.videoSize) this.videoSize = settings.videoSize;
          if (settings.videoMinimized !== undefined) this.videoMinimized = settings.videoMinimized;
          if (settings.videoOverlayMode !== undefined) this.videoOverlayMode = settings.videoOverlayMode;
          if (settings.videoOverlayOpacity !== undefined) {
            const clampedOpacity = Math.min(Math.max(Number(settings.videoOverlayOpacity) || 0.65, 0.1), 1);
            this.videoOverlayOpacity = parseFloat(clampedOpacity.toFixed(2));
          }
          if (settings.videoPlaneSettings) {
            this.videoPlaneSettings = {
              ...this.videoPlaneSettings,
              ...settings.videoPlaneSettings
            };
          }
          // Force timelapseMode to false by default
          this.timelapseMode = false;
          if (settings.timelapseInterval) this.timelapseInterval = settings.timelapseInterval;
          if (settings.timelapseOpacity !== undefined) this.timelapseOpacity = settings.timelapseOpacity;
        if (settings.showTimelapseSettings !== undefined) this.showTimelapseSettings = settings.showTimelapseSettings;
          if (settings.recentSubjectColors) this.recentSubjectColors = settings.recentSubjectColors;
          if (settings.showCameraControls !== undefined) this.showCameraControls = settings.showCameraControls;
          if (settings.enableLights !== undefined) this.enableLights = settings.enableLights;
          if (settings.syncMode) this.syncMode = settings.syncMode;
          if (typeof settings.syncReferenceFrame === 'number') this.syncReferenceFrame = settings.syncReferenceFrame;

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
        groundOpacity: this.groundOpacity,
        groundPositionY: this.groundPositionY,
        showGround: this.showGround,
        useGroundTexture: this.useGroundTexture,
        useCheckerboard: this.useCheckerboard,
        playSpeed: this.playSpeed,
        recordingFormat: this.recordingFormat,
        videoBitrate: this.videoBitrate,
        loopCount: this.loopCount,
        isLooping: this.isLooping,
        captureMode: this.captureMode,
                  // Marker settings removed
        showSidebar: this.showSidebar,
        videoPosition: this.videoPosition,
        videoSize: this.videoSize,
        videoMinimized: this.videoMinimized,
        videoOverlayMode: this.videoOverlayMode,
        videoOverlayOpacity: this.videoOverlayOpacity,
        videoPlaneSettings: this.videoPlaneSettings,
        timelapseMode: this.timelapseMode,
        timelapseInterval: this.timelapseInterval,
        timelapseOpacity: this.timelapseOpacity,
      showTimelapseSettings: this.showTimelapseSettings,
        recentSubjectColors: this.recentSubjectColors, // Save recent colors
        showCameraControls: this.showCameraControls, // Save camera controls visibility
        enableLights: this.enableLights, // Save lighting state
        syncMode: this.syncMode,
        syncReferenceFrame: this.syncReferenceFrame,
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
  
      console.log(`[applyLoadedSceneSettings] Applying Background: ${this.backgroundColor}, Ground: ${this.groundColor}, ShowGround: ${this.showGround}, UseTexture: ${this.useGroundTexture}, UseChecker: ${this.useCheckerboard}`);
      // Background color
      this.updateBackgroundColor(this.backgroundColor);
  
      // Ground settings
      if (this.groundMesh) {
          this.groundMesh.visible = this.showGround;
          this.groundMesh.position.y = this.groundPositionY;
          this.updateGroundColor(this.groundColor); // Update color first
  
          // Apply texture settings
          const oldMaterial = this.groundMesh.material;
          const isTransparent = this.groundOpacity < 1.0;
          if (this.useGroundTexture) {
              const textureToUse = this.useCheckerboard ? this.groundTexture : this.gridTexture;
              if (!textureToUse && !this.useCheckerboard) {
                // Ensure grid texture is loaded if needed
                this.loadGridTexture();
              }
              this.groundMesh.material = new THREE.MeshPhongMaterial({
                  map: this.useCheckerboard ? this.groundTexture : this.gridTexture,
                  side: THREE.DoubleSide,
                  color: new THREE.Color(this.groundColor),
                  opacity: this.groundOpacity,
                  transparent: isTransparent,
                  depthWrite: !isTransparent
                            });
                        } else {
              this.groundMesh.material = new THREE.MeshPhongMaterial({
                  color: new THREE.Color(this.groundColor),
                  side: THREE.DoubleSide,
                  opacity: this.groundOpacity,
                  transparent: isTransparent,
                  depthWrite: !isTransparent
              });
          }
          if (oldMaterial && oldMaterial !== this.groundMesh.material) {
            oldMaterial.dispose();
          }
                    } else {
          console.warn('[applyLoadedSceneSettings] Ground mesh not ready when applying settings.');
          console.warn('[applyLoadedSceneSettings] Ground mesh not ready.');
      }
      
      // Apply lighting state
      if (this.lights.hemisphere) {
          this.lights.hemisphere.intensity = this.enableLights 
              ? (this.lights.hemisphereOriginalIntensity || 0.8) 
              : 0;
      }
      if (this.lights.directionals && this.lights.directionals.length > 0) {
          this.lights.directionals.forEach(light => {
              light.intensity = this.enableLights 
                  ? (this.lights.directionalOriginalIntensity || 0.5) 
                  : 0;
          });
      }
      if (this.lights.spotlight) {
          this.lights.spotlight.intensity = this.enableLights 
              ? (this.lights.spotlightOriginalIntensity || 1) 
              : 0;
      }
      // Boost ambient light when directional lights are disabled for uniform illumination
      if (this.lights.ambient) {
          this.lights.ambient.intensity = this.enableLights 
              ? (this.lights.ambientOriginalIntensity || 0.6) 
              : 2.0; // High ambient light for uniform color
      }
  
      // Marker settings that affect meshes
              // Marker functionality removed
      // Apply marker visibility (don't toggle, just update current frame visibility)
                  // Marker functionality removed
  
      // Re-render to apply all changes
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
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
        this.gridTexture.repeat.set(10, 10); // Adjust repeat to match plane size
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
        return this.handleFileUpload(fakeEvent);
    },

    connectLiveStream() {
      if (this.liveSocket) {
        this.disconnectLiveStream();
      }

      // Expand the section when connecting
      this.showLiveStreamDetails = true;

      try {
        this.liveStatus = 'connecting';
        const socket = new WebSocket(this.liveUrl);
        this.liveSocket = socket;

        socket.onopen = () => {
          this.liveStatus = 'connected';
          this.liveMode = true;
          this.showLiveStreamDetails = true; // Keep expanded when connected
          console.log('[live] Connected to', this.liveUrl);
        };

        socket.onclose = () => {
          console.log('[live] Disconnected');
          this.liveStatus = 'disconnected';
          this.liveMode = false;
          this.liveSocket = null;
          this.liveAnimationIndex = null;
        };

        socket.onerror = (err) => {
          console.error('[live] WebSocket error', err);
          this.liveStatus = 'error';
        };

        socket.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'init') {
              this.handleLiveInit(msg);
            } else if (msg.type === 'frame') {
              this.handleLiveFrame(msg);
            }
          } catch (e) {
            console.error('[live] Failed to parse message', e);
          }
        };
      } catch (e) {
        console.error('[live] Failed to connect', e);
        this.liveStatus = 'error';
      }
    },

    disconnectLiveStream() {
      if (this.liveSocket) {
        this.liveSocket.close();
      }
      this.liveSocket = null;
      this.liveStatus = 'disconnected';
      this.liveMode = false;
      this.liveAnimationIndex = null;
    },

    async handleLiveInit(msg) {
      console.log('[live] init', msg);

      const baseJson = {
        time: [0],
        bodies: {}
      };

      Object.entries(msg.bodies || {}).forEach(([name, bd]) => {
        baseJson.bodies[name] = {
          attachedGeometries: bd.attachedGeometries || [],
          scaleFactors: bd.scaleFactors || [1.0, 1.0, 1.0],
          rotation: [[0, 0, 0]],
          translation: [[0, 0, 0]]
        };
      });

      await this.loadJsonData(baseJson);

      const liveIndex = this.animations.length - 1;
      if (liveIndex < 0) {
        console.error('[live] No animation created from init');
        return;
      }

      this.liveAnimationIndex = liveIndex;
      const anim = this.animations[liveIndex];

      anim.data.time = [];
      Object.values(anim.data.bodies).forEach((bd) => {
        bd.rotation = [];
        bd.translation = [];
      });

      if (typeof msg.frameRate === 'number' && msg.frameRate > 0) {
        this.frameRate = msg.frameRate;
      }

      this.frames = anim.data.time;
      this.frame = 0;
      this.playing = false;
      this.updateDisplayedTime();
    },

    handleLiveFrame(msg) {
      if (this.liveAnimationIndex === null) {
        console.warn('[live] Frame received before init; ignoring');
        return;
      }

      const anim = this.animations[this.liveAnimationIndex];
      const data = anim.data;

      const t = typeof msg.time === 'number'
        ? msg.time
        : (data.time.length > 0 ? data.time[data.time.length - 1] : 0);
      data.time.push(t);

      Object.entries(msg.bodies || {}).forEach(([name, bodyMsg]) => {
        if (!data.bodies[name]) {
          return;
        }
        const bd = data.bodies[name];
        const rot = Array.isArray(bodyMsg.rotation) ? bodyMsg.rotation : [0, 0, 0];
        const trn = Array.isArray(bodyMsg.translation) ? bodyMsg.translation : [0, 0, 0];
        bd.rotation.push(rot);
        bd.translation.push(trn);
      });

      // If playback is paused, buffer frames but don't update the visible pose yet.
      if (!this.playing) {
        return;
      }

      this.frames = data.time;
      this.frame = this.frames.length - 1;
      this.updateDisplayedTime();
      this.animateOneFrame();
    },
  
    centerCameraOnSubject() {
      if (!this.scene || !this.camera || !this.controls) return;
  
      let targetPosition = new THREE.Vector3(0, 1, 0); // Default target near origin
      let foundSubject = false;
  
      // Priority 1: Use first animation's central body part
      if (this.animations.length > 0) {
        const firstAnim = this.animations[0];
        // Try common names for central body parts
        const centralBodyNames = ['pelvis', 'torso', 'midHip', 'hip'];
        let centralBodyKey = null;
  
        for (const name of centralBodyNames) {
            if (firstAnim.data.bodies[name]) {
                centralBodyKey = name;
                break;
            }
        }
  
        if (centralBodyKey && firstAnim.data.bodies[centralBodyKey].translation[this.frame]) {
            const bodyData = firstAnim.data.bodies[centralBodyKey];
            targetPosition.set(
                bodyData.translation[this.frame][0],
                bodyData.translation[this.frame][1],
                bodyData.translation[this.frame][2]
            );
            // Apply animation offset
            targetPosition.add(firstAnim.offset);
            foundSubject = true;
            console.log(`Centering on animation body: ${centralBodyKey}`);
        } else if (this.meshes) {
            // Fallback: Average position of first animation's meshes
            const meshKeys = this.getMeshKeysForAnimation(0);
            if (meshKeys.length > 0) {
                const center = new THREE.Vector3();
                let count = 0;
                meshKeys.forEach(key => {
                    if (this.meshes[key] && this.meshes[key].visible) {
                        center.add(this.meshes[key].position);
                        count++;
                    }
                });
                if (count > 0) {
                    targetPosition = center.divideScalar(count);
                    foundSubject = true;
                    console.log('Centering on average mesh position of first animation.');
                }
            }
        }
      }
  
      // Priority 2: Use markers if no animations exist
      if (!foundSubject && this.markerSpheres.length > 0) {
        // Find center of all marker positions at current frame
        const center = new THREE.Vector3();
        let count = 0;
  
        this.markerSpheres.forEach(sphere => {
          if (sphere.visible && sphere.position) {
            center.add(sphere.position);
            count++;
          }
        });
  
        if (count > 0) {
          targetPosition = center.divideScalar(count);
          foundSubject = true;
          console.log('Centering on marker cluster center.');
        }
      }
  
      // Set camera position relative to the target
      // Maintain current camera distance if possible, otherwise use default
      const offset = new THREE.Vector3();
      if (foundSubject) {
          offset.copy(this.camera.position).sub(this.controls.target);
      } else {
          // Reset to default view if no subject found
          console.log('No subject found, resetting to default view.');
          targetPosition.set(0, 1, 0);
          offset.set(3.33, 2.5, -2.30); // Corresponds to initial position relative to target (0,1,0)
      }
  
      // Keep a minimum distance to avoid being inside the model
      const minDistance = 1.0;
      if (offset.length() < minDistance) {
          offset.normalize().multiplyScalar(minDistance);
      }
  
      const newCameraPosition = new THREE.Vector3().copy(targetPosition).add(offset);
  
      // Apply the changes
      this.controls.target.copy(targetPosition);
      this.camera.position.copy(newCameraPosition);
      this.controls.update(); // Important to apply target and position changes
  
      // Render the scene
      if (this.renderer) {
          this.renderer.render(this.scene, this.camera);
      }
    },
    toggleLoadObjectDialog() {
      this.showLoadObjectDialog = !this.showLoadObjectDialog;
    },
    loadCustomObject() {
      if (!this.objFile) {
        alert('Please select an OBJ file');
            return;
        }
  
      // Create a URL for the uploaded file
      const fileURL = URL.createObjectURL(this.objFile);
  
      // Load the OBJ file using the existing objLoader
      objLoader.load(fileURL, (root) => {
        if (!this.scene) {
          URL.revokeObjectURL(fileURL);
          return;
        }
  
        // Set up the object properties
        root.position.set(
          parseFloat(this.objPosition.x),
          parseFloat(this.objPosition.y),
          parseFloat(this.objPosition.z)
        );
  
        // Set scale
        const scale = parseFloat(this.objScale);
        root.scale.set(scale, scale, scale);
  
        // Apply material to all meshes in the object
        root.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            // Create a material with the selected color
            child.material = new THREE.MeshPhongMaterial({
              color: new THREE.Color(this.objColor),
              shininess: 30,
              transparent: false,
              opacity: 1.0
            });
  
            // Enable shadows
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
  
        // Generate a unique key for this object
        const objKey = `custom_obj_${Date.now()}`;
  
        // Store the mesh in the meshes object
        this.meshes[objKey] = root;
  
        // Track this custom object
        this.customObjects.push({
          id: objKey,
          name: this.objFile.name,
          position: { ...this.objPosition },
          scale: this.objScale,
          color: this.objColor
        });
  
        // Add the object to the scene
        this.scene.add(root);
  
        // Render the scene
        this.renderer.render(this.scene, this.camera);
  
        // Clean up the URL
        URL.revokeObjectURL(fileURL);
  
        // Close the dialog
        this.showLoadObjectDialog = false;
  
        // Reset the file input
        this.objFile = null;
  
        // Log success
        console.log('Custom object loaded successfully', objKey);
      },
      // Progress callback
      (xhr) => {
        console.log((xhr.loaded / xhr.total * 100) + '% loaded');
      },
      // Error callback
      (error) => {
        console.error('Error loading the OBJ file', error);
        alert('Error loading the OBJ file: ' + error.message);
        URL.revokeObjectURL(fileURL);
      });
    },
    isObjectVisible(id) {
      // Check if the object exists in the meshes
      if (this.meshes[id]) {
        return this.meshes[id].visible;
      }
      return false;
    },
    toggleObjectVisibility(id) {
      // Toggle visibility of the custom object
      if (this.meshes[id]) {
        this.meshes[id].visible = !this.meshes[id].visible;
        // Force a render update
        this.renderer.render(this.scene, this.camera);
      }
    },
    removeCustomObject(id) {
      // Remove the object from the scene
      if (this.meshes[id]) {
        this.scene.remove(this.meshes[id]);
  
        // Remove from meshes object
        delete this.meshes[id];
  
        // Remove from customObjects array
        this.customObjects = this.customObjects.filter(obj => obj.id !== id);
  
        // Force a render update
        this.renderer.render(this.scene, this.camera);
  
        // Close the manager if no objects remain
        if (this.customObjects.length === 0) {
          this.showCustomObjectsManager = false;
        }
      }
    },
    handleModelFileSelect(event) {
      const files = event.target.files;
      if (files.length > 0) {
        const file = files[0];
        const fileURL = URL.createObjectURL(file);
        const fileExtension = file.name.split('.').pop().toLowerCase();
  
        // Function to handle loaded model
        const processModel = (model, type) => {
          // Generate a unique key for this object
          const objKey = `custom_obj_${Date.now()}`;
  
          // Create default object properties
          const newObject = {
            id: objKey,
            name: file.name,
            position: { x: 0, y: 0, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: 1,
            color: '#ffffff',
            opacity: 1.0,
            type: type,
            mesh: model
          };
  
          // For GLTF/GLB models that might come with their own materials
          const preserveMaterials = type === 'gltf' || type === 'glb';
  
          // Handle different model types
          if (type === 'stl') {
            // STL comes as geometry, needs to be converted to mesh
            const material = new THREE.MeshPhongMaterial({
              color: new THREE.Color(newObject.color),
              shininess: 30,
              transparent: false,
              opacity: 1.0
            });
            model = new THREE.Mesh(model, material);
            newObject.mesh = model;
          }
  
          // Apply material to all meshes unless it's a GLTF/GLB model
          if (!preserveMaterials) {
            model.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                child.material = new THREE.MeshPhongMaterial({
                  color: new THREE.Color(newObject.color),
                  shininess: 30,
                  transparent: false,
                  opacity: 1.0
                });
                child.castShadow = true;
                child.receiveShadow = true;
              }
            });
          }
  
          // AUTO-CENTER AND SCALE THE MODEL
          // Create a bounding box for the model
          const boundingBox = new THREE.Box3().setFromObject(model);
          const size = new THREE.Vector3();
          boundingBox.getSize(size);
  
          // Calculate the center of the object
          const center = new THREE.Vector3();
          boundingBox.getCenter(center);
  
          // Move object center to origin
          model.position.sub(center);
  
          // Calculate scale to make the object a reasonable size (target size in meters)
          const targetSize = 2.0; // Target size of the largest dimension in meters
          const maxDimension = Math.max(size.x, size.y, size.z);
          const scale = targetSize / maxDimension;
  
        // Apply scale
          model.scale.set(scale, scale, scale);
          newObject.scale = scale;
  
          // Place object on the ground (y=0)
          // First recalculate bounding box after scaling
          const newBoundingBox = new THREE.Box3().setFromObject(model);
          const newSize = new THREE.Vector3();
          newBoundingBox.getSize(newSize);
  
          // Position the bottom of the object at y=0 (ground level)
          const bottomY = newBoundingBox.min.y;
          model.position.y -= bottomY;
          newObject.position = {
            x: model.position.x,
            y: model.position.y,
            z: model.position.z
          };
  
          // Store the mesh
          this.meshes[objKey] = model;
  
          // Add to customObjects array
          this.customObjects.push(newObject);
  
          // Add to scene
          this.scene.add(model);
  
          // Render the scene
          this.renderer.render(this.scene, this.camera);
  
          // Clean up
          URL.revokeObjectURL(fileURL);
        };
  
        // Error handler
        const handleError = (error) => {
          console.error(`Error loading ${fileExtension.toUpperCase()} file:`, error);
          alert(`Error loading ${fileExtension.toUpperCase()} file: ${error.message}`);
          URL.revokeObjectURL(fileURL);
        };
  
        // Progress handler
        const handleProgress = (xhr) => {
          console.log((xhr.loaded / xhr.total * 100) + '% loaded');
        };
  
        // Choose loader based on file extension
        switch (fileExtension) {
          case 'obj':
            objLoader.load(fileURL,
              model => processModel(model, 'obj'),
              handleProgress,
              handleError
            );
            break;
  
          case 'gltf':
          case 'glb':
            gltfLoader.load(fileURL,
              gltf => processModel(gltf.scene, 'gltf'),
              handleProgress,
              handleError
            );
            break;
  
          case 'fbx':
            fbxLoader.load(fileURL,
              model => processModel(model, 'fbx'),
              handleProgress,
              handleError
            );
            break;
  
          case 'stl':
            stlLoader.load(fileURL,
              geometry => processModel(geometry, 'stl'),
              handleProgress,
              handleError
            );
            break;
  
          case 'dae':
            colladaLoader.load(fileURL,
              collada => processModel(collada.scene, 'dae'),
              handleProgress,
              handleError
            );
            break;
  
          default:
            alert('Unsupported file format');
            URL.revokeObjectURL(fileURL);
            break;
        }
  
        // Reset the input value
        event.target.value = '';
      }
    },
    updateObjectColor(id, colorHex) {
      const obj = this.customObjects.find(o => o.id === id);
      if (!obj) return;
  
      // Update the object's color property
      obj.color = colorHex;
  
      // Update the mesh material
      const mesh = this.meshes[id];
          if (mesh) {
            mesh.traverse((child) => {
              if (child instanceof THREE.Mesh) {
            child.material.color = new THREE.Color(colorHex);
                child.material.needsUpdate = true;
              }
            });
          }
  
      // Render the scene
          this.renderer.render(this.scene, this.camera);
    },
    updateObjectOpacity(id, value) {
      const obj = this.customObjects.find(o => o.id === id);
      if (!obj) return;
  
      // Update the object's opacity property
      obj.opacity = value;
  
      // Update the mesh material
      const mesh = this.meshes[id];
      if (mesh) {
        mesh.traverse((child) => {
              if (child instanceof THREE.Mesh) {
            child.material.opacity = value;
            child.material.transparent = value < 1;
            child.material.needsUpdate = true;
              }
            });
          }
  
      // Render the scene
      this.renderer.render(this.scene, this.camera);
    },
    updateObjectPosition(id, axis, value) {
      const obj = this.customObjects.find(o => o.id === id);
      if (!obj || !obj.mesh) return;
  
      obj.position[axis] = Number(value);
      obj.mesh.position[axis] = Number(value);
  
      this.renderer.render(this.scene, this.camera);
    },
    debouncedUpdateObjectPosition(id, axis, value) {
      // Clear any existing timer for this combination
      const timerKey = `${id}_position_${axis}`;
      if (this.objectUpdateTimers[timerKey]) {
        clearTimeout(this.objectUpdateTimers[timerKey]);
      }
  
      // Set a new timer to update after 150ms of no changes
      this.objectUpdateTimers[timerKey] = setTimeout(() => {
        this.updateObjectPosition(id, axis, value);
        delete this.objectUpdateTimers[timerKey];
      }, 150);
    },
    debouncedUpdateObjectRotation(id, axis, value) {
      // Clear any existing timer for this combination
      const timerKey = `${id}_rotation_${axis}`;
      if (this.objectUpdateTimers[timerKey]) {
        clearTimeout(this.objectUpdateTimers[timerKey]);
      }
  
      // Set a new timer to update after 150ms of no changes
      this.objectUpdateTimers[timerKey] = setTimeout(() => {
        this.updateObjectRotation(id, axis, value);
        delete this.objectUpdateTimers[timerKey];
      }, 150);
    },
    debouncedUpdateObjectScale(id, value) {
      // Clear any existing timer for this combination
      const timerKey = `${id}_scale`;
      if (this.objectUpdateTimers[timerKey]) {
        clearTimeout(this.objectUpdateTimers[timerKey]);
      }
  
      // Set a new timer to update after 150ms of no changes
      this.objectUpdateTimers[timerKey] = setTimeout(() => {
        this.updateObjectScale(id, value);
        delete this.objectUpdateTimers[timerKey];
      }, 150);
    },
    updateObjectScale(id, value) {
      const obj = this.customObjects.find(o => o.id === id);
      if (!obj || !obj.mesh) return;
  
      const scale = Number(value);
      obj.scale = scale;
      obj.mesh.scale.set(scale, scale, scale);
  
      this.renderer.render(this.scene, this.camera);
    },
    updateObjectRotation(id, axis, value) {
      const obj = this.customObjects.find(o => o.id === id);
      if (!obj || !obj.mesh) return;
  
      if (!obj.rotation) {
        obj.rotation = { x: 0, y: 0, z: 0 };
      }
  
      obj.rotation[axis] = Number(value);
      obj.mesh.rotation[axis] = THREE.Math.degToRad(Number(value));
  
          this.renderer.render(this.scene, this.camera);
    },
    centerCameraOnObject(id) {
      if (!this.scene || !this.camera || !this.controls) return;
  
      const mesh = this.meshes[id];
      if (!mesh) return;
  
      // Calculate bounding box
      const boundingBox = new THREE.Box3().setFromObject(mesh);
      const center = new THREE.Vector3();
      boundingBox.getCenter(center);
  
      // Calculate optimal distance based on bounding box size
      const size = new THREE.Vector3();
      boundingBox.getSize(size);
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = this.camera.fov * (Math.PI / 180);
      const distance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5; // 1.5 for some padding
  
      // Set camera position
      const direction = new THREE.Vector3(1, 1, 1).normalize();
      const position = center.clone().add(direction.multiplyScalar(distance));
  
      // Update camera and controls
      this.camera.position.copy(position);
      this.controls.target.copy(center);
      this.controls.update();
  
      // Render the scene
          this.renderer.render(this.scene, this.camera);
    },
  
    centerCameraOnAnimation(index) {
      if (!this.scene || !this.camera || !this.controls || !this.animations[index]) return;
  
      const animation = this.animations[index];
      const meshKeys = Object.keys(this.meshes).filter(key => key.startsWith(`anim${index}_`));
  
      if (meshKeys.length === 0) return;
  
      // Calculate combined bounding box of all meshes in the animation
      const boundingBox = new THREE.Box3();
      meshKeys.forEach(key => {
        const mesh = this.meshes[key];
        if (mesh && mesh.visible) {
          boundingBox.expandByObject(mesh);
        }
      });
  
      const center = new THREE.Vector3();
      boundingBox.getCenter(center);
  
      // Calculate optimal distance
      const size = new THREE.Vector3();
      boundingBox.getSize(size);
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = this.camera.fov * (Math.PI / 180);
      const distance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;
  
      // Set camera position
      const direction = new THREE.Vector3(1, 1, 1).normalize();
      const position = center.clone().add(direction.multiplyScalar(distance));
  
      // Update camera and controls
      this.camera.position.copy(position);
      this.controls.target.copy(center);
      this.controls.update();
  
      // Render the scene
          this.renderer.render(this.scene, this.camera);
    },
  
    centerModelToOrigin(index) {
      if (!this.animations[index]) return;
  
      const animation = this.animations[index];
      const meshKeys = Object.keys(this.meshes).filter(key => key.startsWith(`anim${index}_`));
  
      if (meshKeys.length === 0) return;
  
      // Calculate center from current mesh positions in world space
      const boundingBox = new THREE.Box3();
      let hasMeshes = false;
      
      meshKeys.forEach(key => {
        const mesh = this.meshes[key];
        if (mesh && mesh.visible) {
          // Update matrix world to get correct position
          mesh.updateMatrixWorld(true);
          // Get bounding box in world space
          const meshBox = new THREE.Box3().setFromObject(mesh);
          boundingBox.union(meshBox);
          hasMeshes = true;
        }
      });
      
      if (!hasMeshes) return;
      
      const center = new THREE.Vector3();
      boundingBox.getCenter(center);
      
      // Calculate the offset needed to move center to origin
      const currentOffset = animation.offset.clone();
      const requiredOffset = new THREE.Vector3(-center.x, -center.y, -center.z);
      
      // Adjust the offset to account for the current mesh positions
      animation.offset.copy(requiredOffset);
      
      // Update all mesh positions
      meshKeys.forEach(key => {
        const mesh = this.meshes[key];
        if (mesh) {
          // Get the base position from data
          const bodyKey = key.split('_')[1];
          if (bodyKey && animation.data.bodies[bodyKey]) {
            const body = animation.data.bodies[bodyKey];
            if (body.translation && body.translation[this.frame]) {
              const trans = body.translation[this.frame];
              const basePosition = new THREE.Vector3(trans[0], trans[1], trans[2]);
              basePosition.add(animation.offset);
              mesh.position.copy(basePosition);
            }
          }
        }
      });
  
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
  
    centerSmplModelToOrigin(sequenceId) {
      const sequence = this.smplSequences.find(seq => seq.id === sequenceId);
      if (!sequence || !sequence.mesh) return;
  
      // Calculate bounding box in world space
      sequence.mesh.updateMatrixWorld(true);
      const worldBoundingBox = new THREE.Box3().setFromObject(sequence.mesh);
      
      if (!worldBoundingBox || worldBoundingBox.isEmpty()) return;
  
      const center = new THREE.Vector3();
      worldBoundingBox.getCenter(center);
  
      // Calculate the offset needed to move the world center to origin
      const currentWorldPosition = sequence.mesh.position.clone();
      const requiredOffset = currentWorldPosition.clone().sub(center);
      
      // Update the offset property
      sequence.offset.copy(requiredOffset);
      
      // Update mesh position
      sequence.mesh.position.copy(requiredOffset);
      
      // Also update skeleton if it exists
      if (sequence.skeleton) {
        sequence.skeleton.position.copy(requiredOffset);
      }
  
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
  
    resetScene() {
      console.log('Resetting scene...');
  
      // Reset camera to default position
      if (this.camera) {
        this.camera.position.set(3.33, 3.5, -2.30);
        this.camera.lookAt(0, 1, 0);
      }
  
      // Reset controls
      if (this.controls) {
        this.controls.target.set(0, 1, 0);
        this.controls.update();
      }
  
      // Force render
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
  
      console.log('Scene reset complete');
    },

    clearScene() {
      console.log('Clearing scene...');

      if (!this.scene) {
        console.warn('Scene not initialized, cannot clear');
        return;
      }

      // Collect objects to preserve (scene infrastructure)
      const objectsToPreserve = new Set();
      
      // Preserve ground mesh
      if (this.groundMesh) {
        objectsToPreserve.add(this.groundMesh);
      }
      
      // Preserve axes group
      if (this.axesGroup) {
        objectsToPreserve.add(this.axesGroup);
      }
      
      // Preserve lights
      if (this.lights) {
        if (this.lights.hemisphere) {
          objectsToPreserve.add(this.lights.hemisphere);
        }
        if (this.lights.directionals && Array.isArray(this.lights.directionals)) {
          this.lights.directionals.forEach(light => {
            objectsToPreserve.add(light);
            if (light.target) {
              objectsToPreserve.add(light.target);
            }
          });
        }
        if (this.lights.spotlight) {
          objectsToPreserve.add(this.lights.spotlight);
        }
        if (this.lights.ambient) {
          objectsToPreserve.add(this.lights.ambient);
        }
      }

      // Remove all meshes from animations
      Object.keys(this.meshes).forEach(key => {
        const mesh = this.meshes[key];
        if (mesh && this.scene.children.includes(mesh) && !objectsToPreserve.has(mesh)) {
          this.scene.remove(mesh);
          // Dispose geometry and materials to free memory
          if (mesh.geometry) {
            mesh.geometry.dispose();
          }
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(mat => mat.dispose && mat.dispose());
          } else if (mesh.material && mesh.material.dispose) {
            mesh.material.dispose();
          }
        }
      });

      // Remove SMPL meshes and skeletons
      this.smplSequences.forEach(sequence => {
        if (sequence.mesh && this.scene.children.includes(sequence.mesh) && !objectsToPreserve.has(sequence.mesh)) {
          this.scene.remove(sequence.mesh);
          if (sequence.mesh.geometry) {
            sequence.mesh.geometry.dispose();
          }
          if (Array.isArray(sequence.mesh.material)) {
            sequence.mesh.material.forEach(mat => mat.dispose && mat.dispose());
          } else if (sequence.mesh.material && sequence.mesh.material.dispose) {
            sequence.mesh.material.dispose();
          }
        }
        if (sequence.skeleton && this.scene.children.includes(sequence.skeleton) && !objectsToPreserve.has(sequence.skeleton)) {
          this.scene.remove(sequence.skeleton);
          if (sequence.skeleton.geometry) {
            sequence.skeleton.geometry.dispose();
          }
          if (sequence.skeleton.material && sequence.skeleton.material.dispose) {
            sequence.skeleton.material.dispose();
          }
        }
      });

      // Remove measurement line
      if (this.measurementLine && this.scene.children.includes(this.measurementLine) && !objectsToPreserve.has(this.measurementLine)) {
        this.scene.remove(this.measurementLine);
        if (this.measurementLine.geometry) {
          this.measurementLine.geometry.dispose();
        }
        if (this.measurementLine.material && this.measurementLine.material.dispose) {
          this.measurementLine.material.dispose();
        }
        this.measurementLine = null;
      }

      // Remove force arrows
      if (this.forceArrows && Array.isArray(this.forceArrows)) {
        this.forceArrows.forEach(arrowGroup => {
          if (arrowGroup && this.scene.children.includes(arrowGroup) && !objectsToPreserve.has(arrowGroup)) {
            this.scene.remove(arrowGroup);
            if (arrowGroup.geometry) {
              arrowGroup.geometry.dispose();
            }
            if (arrowGroup.material && arrowGroup.material.dispose) {
              arrowGroup.material.dispose();
            }
          }
        });
      }

      // Remove video plane and dispose video resources
      if (this.videoPlane) {
        if (this.scene.children.includes(this.videoPlane) && !objectsToPreserve.has(this.videoPlane)) {
          this.scene.remove(this.videoPlane);
        }
        if (this.videoPlane.geometry) {
          this.videoPlane.geometry.dispose();
        }
        const material = this.videoPlane.material;
        if (material) {
          if (Array.isArray(material)) {
            material.forEach(mat => mat.dispose && mat.dispose());
          } else if (material.dispose) {
            material.dispose();
          }
        }
        this.videoPlane = null;
      }
      // Dispose video texture
      if (this.videoTexture) {
        this.videoTexture.dispose();
        this.videoTexture = null;
      }
      // Clear video URL and revoke object URL if it exists
      if (this.videoUrl) {
        URL.revokeObjectURL(this.videoUrl);
        this.videoUrl = null;
      }
      // Clear video file and related properties
      this.videoFile = null;
      this.videoDuration = 0;
      // Reset video position and size
      this.videoPosition = { x: 20, y: 20 };
      this.videoSize = { width: 300, height: 'auto' };
      // Clear projection canvas
      this.clearProjectionCanvas();

      // Remove text sprites
      Object.values(this.textSprites).forEach(sprite => {
        if (sprite && this.scene.children.includes(sprite) && !objectsToPreserve.has(sprite)) {
          this.scene.remove(sprite);
          if (sprite.material && sprite.material.map) {
            sprite.material.map.dispose();
          }
          if (sprite.material && sprite.material.dispose) {
            sprite.material.dispose();
          }
        }
      });

      // Remove timelapse meshes
      Object.values(this.timelapseMeshes).forEach(({mesh}) => {
        if (mesh && this.scene.children.includes(mesh) && !objectsToPreserve.has(mesh)) {
          this.scene.remove(mesh);
          if (mesh.geometry) {
            mesh.geometry.dispose();
          }
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(mat => mat.dispose && mat.dispose());
          } else if (mesh.material && mesh.material.dispose) {
            mesh.material.dispose();
          }
        }
      });

      // Remove any remaining markers/sprites by traversing scene
      const objectsToRemove = [];
      this.scene.traverse((object) => {
        if (!objectsToPreserve.has(object)) {
          // Check if it's a sprite or marker (not a light, ground, or axes)
          // Skip lights and their targets
          if (object instanceof THREE.Light || object instanceof THREE.Object3D && object.isLight) {
            return;
          }
          if (object instanceof THREE.Sprite || 
              (object instanceof THREE.Mesh && object !== this.groundMesh) ||
              (object instanceof THREE.Group && object !== this.axesGroup)) {
            objectsToRemove.push(object);
          }
        }
      });
      
      objectsToRemove.forEach(obj => {
        // Remove from scene (works even if nested in groups)
        if (obj.parent) {
          obj.parent.remove(obj);
        } else if (this.scene.children.includes(obj)) {
          this.scene.remove(obj);
        }
        // Dispose resources
        if (obj.geometry) {
          obj.geometry.dispose();
        }
        if (obj.material) {
          if (Array.isArray(obj.material)) {
            obj.material.forEach(mat => mat.dispose && mat.dispose());
          } else if (obj.material.dispose) {
            obj.material.dispose();
          }
        }
      });

      // Clear all data structures
      this.animations = [];
      this.smplSequences = [];
      this.meshes = {};
      this.customObjects = [];
      this.markersDatasets = {};
      this.forcesDatasets = {};
      this.forceArrows = [];
      this.textSprites = {};
      this.timelapseMeshes = {};
      
      // Reset frame data
      this.frames = [];
      this.frame = 0;
      this.time = 0;
      this.frameRate = 60;

      // Clear active subject
      this.activeSubject = null;

      // Render the scene
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }

      console.log('Scene cleared successfully');
    },
  
    testScene() {
      console.log('Testing scene with a simple cube...');
  
      if (!this.scene) {
        console.log('Scene not initialized, initializing...');
        this.$nextTick(() => {
        this.initScene();
        });
      }
  
      // Create a simple test cube
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const material = new THREE.MeshLambertMaterial({ color: 0xff0000 });
      const cube = new THREE.Mesh(geometry, material);
      cube.position.set(0, 1, 0);
  
      // Remove any existing test cube
      const existingCube = this.scene.getObjectByName('testCube');
      if (existingCube) {
        this.scene.remove(existingCube);
      }
  
      cube.name = 'testCube';
      this.scene.add(cube);
  
      // Reset camera to look at the cube
      if (this.camera) {
        this.camera.position.set(3.33, 3.5, -2.30);
        this.camera.lookAt(0, 1, 0);
      }
  
      if (this.controls) {
        this.controls.target.set(0, 1, 0);
        this.controls.update();
      }
  
      // Force render
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
  
      console.log('Test cube added to scene');
    },
  
    openImportDialog() {
      this.showImportDialog = true;
    },
    selectFileType(inputRef) {
      this.$refs[inputRef].click();
      this.showImportDialog = false; // Close the dialog after selecting
    },
    setAllAnimationsPlayable(playable) {
      this.animations.forEach(animation => {
        animation.playable = playable;
      });
      this.smplSequences.forEach(sequence => {
        sequence.playable = playable;
      });
      this.markersPlayable = playable;
    },
    setCameraView(viewType) {
      if (!this.camera || !this.controls) return;
  
      const distance = this.camera.position.distanceTo(this.controls.target);
      const currentTarget = this.controls.target.clone(); // Keep current target
  
      // Define new positions based on view type relative to the CURRENT target
      let newPosition = new THREE.Vector3();
      const offset = Math.max(distance, 1.0); // Ensure a minimum distance
      const isoFactor = offset / Math.sqrt(3); // Factor for isometric views
  
      switch(viewType) {
        case 'top':
          newPosition.set(currentTarget.x, currentTarget.y + offset, currentTarget.z);
          break;
        case 'bottom':
          newPosition.set(currentTarget.x, currentTarget.y - offset, currentTarget.z);
          break;
        case 'front':
          newPosition.set(currentTarget.x, currentTarget.y, currentTarget.z + offset);
          break;
        case 'back':
          newPosition.set(currentTarget.x, currentTarget.y, currentTarget.z - offset);
          break;
        case 'left':
          newPosition.set(currentTarget.x - offset, currentTarget.y, currentTarget.z);
          break;
        case 'right':
          newPosition.set(currentTarget.x + offset, currentTarget.y, currentTarget.z);
          break;
  
        // Handle Corner Views
        case 'frontTopRight':
          newPosition.set(currentTarget.x + isoFactor, currentTarget.y + isoFactor, currentTarget.z + isoFactor);
          break;
        case 'frontTopLeft':
          newPosition.set(currentTarget.x - isoFactor, currentTarget.y + isoFactor, currentTarget.z + isoFactor);
          break;
        case 'frontBottomRight':
          newPosition.set(currentTarget.x + isoFactor, currentTarget.y - isoFactor, currentTarget.z + isoFactor);
          break;
        case 'frontBottomLeft':
          newPosition.set(currentTarget.x - isoFactor, currentTarget.y - isoFactor, currentTarget.z + isoFactor);
          break;
        case 'backTopRight':
          newPosition.set(currentTarget.x + isoFactor, currentTarget.y + isoFactor, currentTarget.z - isoFactor);
          break;
        case 'backTopLeft':
          newPosition.set(currentTarget.x - isoFactor, currentTarget.y + isoFactor, currentTarget.z - isoFactor);
          break;
        case 'backBottomRight':
          newPosition.set(currentTarget.x + isoFactor, currentTarget.y - isoFactor, currentTarget.z - isoFactor);
          break;
        case 'backBottomLeft':
          newPosition.set(currentTarget.x - isoFactor, currentTarget.y - isoFactor, currentTarget.z - isoFactor);
          break;
  
        case 'default': // Added case for resetting to default view
        case 'isometric': {
          // Use the standard frontTopRight isometric view for 'default' or 'isometric'
          newPosition.set(currentTarget.x + isoFactor, currentTarget.y + isoFactor, currentTarget.z + isoFactor);
          break;
        }
        default:
          console.warn('Unknown view type:', viewType);
          return;
      }
  
      // *** Update controls target FIRST ***
      this.controls.target.copy(currentTarget);
  
      // Apply new position
      this.camera.position.copy(newPosition);
  
      // *** Update controls state AFTER position and target are set ***
      this.controls.update();
  
      // Re-render the scene
      if (this.renderer) {
        this.renderer.render(this.scene, this.camera);
      }
    },
  
    resetCameraView() {
      if (!this.camera || !this.controls) return;

      const initialPosition = new THREE.Vector3(3.33, 3.5, -2.30);
      const initialTarget = new THREE.Vector3(0, 1, 0);

      // *** Update controls target FIRST ***
      this.controls.target.copy(initialTarget);

      // Apply new position
      this.camera.position.copy(initialPosition);

      // *** Update controls state AFTER position and target are set ***
      this.controls.update();

      // Re-render the scene
      if (this.renderer) {
        this.renderer.render(this.scene, this.camera);
      }
    },

    alignCameraWithCapture(behindPlane = true, distanceBehind = null) {
      if (!this.camera || !this.controls) {
        console.warn('Camera or controls not initialized');
        return;
      }

      const extrResult = this.resolveCameraExtrinsics();
      if (!extrResult) {
        console.warn('No camera extrinsics available');
        return;
      }

      const pose = this.getCameraPoseFromExtrinsics(extrResult.extrinsics, 0);
      if (!pose) {
        console.warn('Failed to compute camera pose');
        return;
      }

      // Get intrinsics to calculate proper viewing distance
      const intrinsics = Array.isArray(this.cameraIntrinsics)
        ? this.cameraIntrinsics
        : this.normalizeMatrix3x3(this.cameraIntrinsics);
      
      // Calculate viewing distance from intrinsics if not provided
      let computedDistance = distanceBehind;
      if (behindPlane && computedDistance === null && intrinsics) {
        // Get image dimensions
        const videoElement = this.videoPreviewElement;
        const normalizedSize = this.normalizeImageSize(this.cameraImageSize);
        const widthPx = normalizedSize?.width || videoElement?.videoWidth || 1920;
        const heightPx = normalizedSize?.height || videoElement?.videoHeight || 1080;
        
        const fx = Number(intrinsics[0][0]) || 1000;
        const fy = Number(intrinsics[1][1]) || 1000;
        
        // Image plane distance from capture camera (from computeVideoPlaneFrame)
        const imagePlaneDistance = 0.01; // meters
        
        // Calculate physical dimensions of image plane at imagePlaneDistance
        const planeWidth = (widthPx * imagePlaneDistance) / fx;
        const planeHeight = (heightPx * imagePlaneDistance) / fy;
        
        // To see the full image plane with correct perspective, the viewer should be
        // positioned at a distance where the plane subtends the same angle as the original FOV
        // This distance equals the image plane distance (to maintain same perspective)
        // But we add a small offset to be "behind" the plane for the window effect
        computedDistance = imagePlaneDistance + 0.2; // 20cm behind image plane
        
        console.log('Computed viewing distance from intrinsics:', {
          fx: fx.toFixed(2),
          fy: fy.toFixed(2),
          imageDimensions: [widthPx, heightPx],
          planeWidth: planeWidth.toFixed(3),
          planeHeight: planeHeight.toFixed(3),
          imagePlaneDistance: imagePlaneDistance.toFixed(3),
          viewerDistanceBehind: computedDistance.toFixed(3)
        });
      } else if (computedDistance === null) {
        computedDistance = 0.5; // Default fallback
      }

      // Find SMPL subject position (same logic as in computeVideoPlaneFrame)
      let subjectPoint = null;
      if (Array.isArray(this.smplSequences) && this.smplSequences.length > 0) {
        for (const seq of this.smplSequences) {
          if (!seq || !seq.joints || !seq.jointCount) {
            continue;
          }
          const jointStride = seq.jointStride || (seq.jointCount * 3);
          const totalFrames = jointStride > 0 ? Math.floor(seq.joints.length / jointStride) : 0;
          if (totalFrames <= 0) {
            continue;
          }
          const jointIndex = 0; // pelvis/root
          const start = jointIndex * 3;
          if (start + 2 < seq.joints.length) {
            subjectPoint = new THREE.Vector3(
              seq.joints[start],
              seq.joints[start + 1],
              seq.joints[start + 2]
            );
            break;
          }
        }
      }

      if (!subjectPoint) {
        subjectPoint = new THREE.Vector3(0, 0, 0);
      }

      let cameraPos;
      if (behindPlane) {
        // Position viewer camera BEHIND the image plane (away from SMPL)
        // Distance computed from intrinsics to maintain correct perspective
        const backwardDirection = pose.cameraForward.clone().negate();
        cameraPos = pose.cameraPosition.clone().add(
          backwardDirection.multiplyScalar(computedDistance)
        );
        console.log('Positioning camera behind image plane', {
          captureCamera: pose.cameraPosition.toArray(),
          viewerCamera: cameraPos.toArray(),
          distanceBehind: computedDistance.toFixed(3),
          computedFromIntrinsics: distanceBehind === null
        });
      } else {
        // Position at capture camera location
        cameraPos = pose.cameraPosition.clone();
        console.log('Positioning camera at capture location', {
          cameraPosition: cameraPos.toArray()
        });
      }

      // Position camera
      this.camera.position.copy(cameraPos);
      
      // Look at the subject (through the plane)
      this.controls.target.copy(subjectPoint);
      
      // Update controls
      this.controls.update();

      // Re-render
      if (this.renderer) {
        this.renderer.render(this.scene, this.camera);
      }

      console.log('Camera aligned - looking at SMPL through image plane', {
        cameraPosition: cameraPos.toArray(),
        lookingAt: subjectPoint.toArray()
      });
    },
  
  
    toggleAxes() {
      this.showAxes = !this.showAxes;
      if (this.axesGroup) {
        this.axesGroup.visible = this.showAxes;
        this.renderer.render(this.scene, this.camera);
      }
  },
  async openFileBrowser() {
    // If already converting files, don't allow another file selection
    if (this.converting) return;
  
    // Create a hidden file input if it doesn't exist
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.multiple = true;
            fileInput.accept = '.json,.trc,.osim,.mot,video/mp4,video/webm';
  
    // Handle the file selection
    fileInput.onchange = async (event) => {
      const files = Array.from(event.target.files);
  
      if (files.length === 0) return;
  
      // Use the same logic as handleDrop for consistency
      const fakeDropEvent = {
        preventDefault: () => {},
        dataTransfer: { files: files }
      };
  
      await this.handleDrop(fakeDropEvent);
    };
  
    // Trigger file selection dialog
    fileInput.click();
  },
  
  // Plotting methods
  openPlottingDialog() {
    this.showPlottingDialog = true;
    this.$nextTick(() => {
      this.initializePlotChart();
    });
  },
  
  async initializePlotChart() {
    if (!this.$refs.plotChart) {
      console.warn('plotChart ref not found');
      return;
    }
  
    console.log('Initializing plot chart:', {
      canvasElement: this.$refs.plotChart,
      canvasSize: {
        width: this.$refs.plotChart.offsetWidth,
        height: this.$refs.plotChart.offsetHeight
      }
    });
  
    const Chart = await import('chart.js/auto');
  
    this.plotChart = new Chart.default(this.$refs.plotChart, {
      type: 'line',
      data: this.plotData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: this.plotSettings.showLegend,
            labels: {
              color: '#ffffff',
              font: {
                size: 12
              }
            }
          },
          title: {
            display: true,
            text: this.getPlotTitle(),
            color: '#ffffff',
            font: {
              size: 16,
              weight: 'bold'
            }
          }
        },
        scales: {
          x: {
            display: true,
            title: {
              display: true,
              text: 'Time (s)',
              color: '#ffffff',
              font: {
                size: 14,
                weight: 'bold'
              }
            },
            grid: {
              display: this.plotSettings.showGrid,
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#ffffff',
              font: {
                size: 12
              }
            }
          },
          y: {
            display: true,
            title: {
              display: true,
              text: this.getYAxisLabel(),
              color: '#ffffff',
              font: {
                size: 14,
                weight: 'bold'
              }
            },
            grid: {
              display: this.plotSettings.showGrid,
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#ffffff',
              font: {
                size: 12
              }
            }
          }
        },
        animation: {
          duration: 0
        },
        interaction: {
          intersect: false
        },
        backgroundColor: '#1e1e1e'
      }
    });
  
    console.log('Chart created successfully:', {
      chartExists: !!this.plotChart,
      canvasSize: {
        width: this.$refs.plotChart.offsetWidth,
        height: this.$refs.plotChart.offsetHeight
      },
      chartData: this.plotChart.data
    });
  
    // Update plot data immediately after chart initialization
    await this.updatePlotData();
  },
  
  getPlotTitle() {
    if (!this.selectedPlotType) return 'Data Plot';
  
    const plotType = this.plotTypes.find(type => type.value === this.selectedPlotType);
    return plotType ? plotType.label : 'Data Plot';
  },
  
  getYAxisLabel() {
    if (!this.selectedPlotType) return 'Value';
  
    switch (this.selectedPlotType) {
      case 'marker_position':
        return 'Position (m)';
      case 'force_magnitude':
      case 'force_components':
        return 'Force (N)';
      case 'marker_distance':
        return 'Distance (m)';
      case 'joint_angles':
        return 'Angle (deg)';
      case 'pelvis_translations':
        return 'Translation (m)';
      default:
        return 'Value';
    }
  },
  
  async updatePlotType() {
    this.selectedVariables = [];
    this.selectedMarkers = [];
    await this.updatePlotData();
  },
  
  async updateSelectedVariables() {
    await this.updatePlotData();
  },
  
  async updateSelectedMarkers() {
    await this.updatePlotData();
  },
  
  generateSampleData() {
    // Generate sample data for testing
    const sampleData = {
      labels: Array.from({length: 100}, (_, i) => i * 0.1),
      datasets: [{
        label: 'Sample Data',
        data: Array.from({length: 100}, (_, i) => Math.sin(i * 0.1) * 10 + Math.random() * 2),
        borderColor: '#FF6384',
        backgroundColor: '#FF638420',
        fill: false,
        tension: 0.1
      }]
    };
  
    return sampleData;
  },
  
  async updatePlotAnimation() {
    await this.updatePlotData();
  },
  
  async updatePlotData() {
    console.log('updatePlotData called', {
      selectedPlotType: this.selectedPlotType,
      selectedVariables: this.selectedVariables,
      selectedMarkers: this.selectedMarkers,
      animations: this.animations.length,
      markersDatasets: Object.keys(this.markersDatasets)
    });
  
    if (!this.selectedPlotType || this.selectedVariables.length === 0) {
      this.plotData = { labels: [], datasets: [] };
      if (this.plotChart) {
        this.plotChart.data = this.plotData;
        this.plotChart.update();
      }
      return;
    }
  
    // For marker-based plots, use marker data time
    let timeData = [];
    if (this.selectedPlotType === 'marker_position' || this.selectedPlotType === 'marker_distance') {
      const markersData = this.markersDatasets[this.selectedPlotAnimation];
      if (markersData && markersData.times) {
        timeData = markersData.times;
      }
    } else {
      // For other plots, use animation data time
      const animation = this.animations[this.selectedPlotAnimation];
      if (animation && animation.data && animation.data.time) {
        timeData = animation.data.time;
      }
    }
  
    if (timeData.length === 0) {
      console.warn('No time data available, using sample data');
      const sampleData = this.generateSampleData();
      this.plotData = sampleData;
  
      if (this.plotChart) {
        this.plotChart.data = this.plotData;
        this.plotChart.update();
      }
      return;
    }
  
    // Initialize plot time range if not set
    if (this.plotTimeRange[1] === 10) {
      this.plotTimeRange = [0, Math.max(...timeData)];
    }
  
    const filteredTimeData = timeData.filter(time =>
      time >= this.plotTimeRange[0] && time <= this.plotTimeRange[1]
    );
  
    this.plotData.labels = filteredTimeData;
    this.plotData.datasets = this.generateDatasets(filteredTimeData);
  
    console.log('Generated plot data:', {
      labels: this.plotData.labels.length,
      datasets: this.plotData.datasets.length,
      firstDataset: this.plotData.datasets[0]
    });
  
    // Ensure chart is initialized before updating
    if (!this.plotChart) {
      console.log('Chart not found, initializing...');
      await this.initializePlotChart();
    }
  
    if (this.plotChart) {
      console.log('Updating chart with data:', {
        labelsLength: this.plotData.labels.length,
        datasetsLength: this.plotData.datasets.length,
        chartExists: !!this.plotChart
      });
  
      this.plotChart.data = this.plotData;
      this.plotChart.update();
  
      console.log('Chart updated successfully');
    } else {
      console.warn('plotChart not found - chart not updated');
    }
  },
  
  generateDatasets(timeData) {
    const datasets = [];
  
    switch (this.selectedPlotType) {
      case 'marker_position':
        datasets.push(...this.generateMarkerPositionDatasets(timeData));
        break;
      case 'force_magnitude':
        datasets.push(...this.generateForceMagnitudeDatasets(timeData));
        break;
      case 'force_components':
        datasets.push(...this.generateForceComponentDatasets(timeData));
        break;
      case 'marker_distance':
        datasets.push(...this.generateMarkerDistanceDatasets(timeData));
        break;
      case 'joint_angles':
        datasets.push(...this.generateJointAngleDatasets(timeData));
        break;
      case 'pelvis_translations':
        datasets.push(...this.generatePelvisTranslationDatasets(timeData));
        break;
    }
  
    return datasets;
  },
  
  generateMarkerPositionDatasets(timeData) {
    const datasets = [];
    const markersData = this.markersDatasets[this.selectedPlotAnimation];
  
    if (!markersData || this.selectedMarkers.length === 0) return datasets;
  
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
    let colorIndex = 0;
  
    this.selectedMarkers.forEach(markerName => {
      if (!markersData.data[markerName]) return;
  
      this.selectedVariables.forEach(variable => {
        const data = [];
        const markerData = markersData.data[markerName][variable];
  
        if (markerData && markersData.times) {
          for (let i = 0; i < timeData.length; i++) {
            // Find the closest time index in the marker data
            const targetTime = timeData[i];
            let closestIndex = 0;
            let minDiff = Math.abs(markersData.times[0] - targetTime);
  
            for (let j = 1; j < markersData.times.length; j++) {
              const diff = Math.abs(markersData.times[j] - targetTime);
              if (diff < minDiff) {
                minDiff = diff;
                closestIndex = j;
              }
            }
  
            if (markerData[closestIndex] !== undefined) {
              data.push(markerData[closestIndex]);
            } else {
              data.push(null);
            }
          }
        }
  
        datasets.push({
          label: `${markerName} ${variable.toUpperCase()}`,
          data: data,
          borderColor: colors[colorIndex % colors.length],
          backgroundColor: colors[colorIndex % colors.length] + '20',
          fill: false,
          tension: 0.1
        });
  
        colorIndex++;
      });
    });
  
    return datasets;
  },
  
  generateForceMagnitudeDatasets(timeData) {
    const datasets = [];
    const forcesData = this.forcesDatasets[this.selectedPlotAnimation];
  
    console.log('generateForceMagnitudeDatasets called:', {
      selectedPlotAnimation: this.selectedPlotAnimation,
      forcesData: forcesData ? 'present' : 'missing',
      timeDataLength: timeData.length,
      selectedVariables: this.selectedVariables
    });
  
    if (!forcesData) {
      console.warn('No forces data available for animation', this.selectedPlotAnimation);
      return datasets;
    }
  
    console.log('Forces data details:', {
      timeRange: [Math.min(...forcesData.time), Math.max(...forcesData.time)],
      columns: Object.keys(forcesData.data),
      firstFewTimes: forcesData.time.slice(0, 5)
    });
  
    const colors = ['#FF6384', '#36A2EB', '#FFCE56'];
    let colorIndex = 0;
  
    this.selectedVariables.forEach(variable => {
      const data = [];
  
      for (let i = 0; i < timeData.length; i++) {
        const targetTime = timeData[i];
  
        // Find closest time index using more robust algorithm
        let closestIndex = 0;
        let minDiff = Math.abs(forcesData.time[0] - targetTime);
  
        for (let j = 1; j < forcesData.time.length; j++) {
          const diff = Math.abs(forcesData.time[j] - targetTime);
          if (diff < minDiff) {
            minDiff = diff;
            closestIndex = j;
          }
        }
  
        const timeIndex = closestIndex;
        if (i < 5) { // Log first few time matches
          console.log(`Time matching [${i}]:`, {
            targetTime,
            closestForceTime: forcesData.time[closestIndex],
            minDiff,
            timeIndex: closestIndex
          });
        }
  
        if (minDiff < 0.1) { // Allow up to 0.1 second difference
          let magnitude = 0;
  
          switch (variable) {
            case 'left_magnitude': {
              const leftFx = forcesData.data['L_ground_force_vx']?.[timeIndex] || 0;
              const leftFy = forcesData.data['L_ground_force_vy']?.[timeIndex] || 0;
              const leftFz = forcesData.data['L_ground_force_vz']?.[timeIndex] || 0;
              magnitude = Math.sqrt(leftFx * leftFx + leftFy * leftFy + leftFz * leftFz);
              break;
            }
            case 'right_magnitude': {
              const rightFx = forcesData.data['R_ground_force_vx']?.[timeIndex] || 0;
              const rightFy = forcesData.data['R_ground_force_vy']?.[timeIndex] || 0;
              const rightFz = forcesData.data['R_ground_force_vz']?.[timeIndex] || 0;
              magnitude = Math.sqrt(rightFx * rightFx + rightFy * rightFy + rightFz * rightFz);
              break;
            }
            case 'total_magnitude': {
              const totalFx = (forcesData.data['L_ground_force_vx']?.[timeIndex] || 0) +
                            (forcesData.data['R_ground_force_vx']?.[timeIndex] || 0);
              const totalFy = (forcesData.data['L_ground_force_vy']?.[timeIndex] || 0) +
                            (forcesData.data['R_ground_force_vy']?.[timeIndex] || 0);
              const totalFz = (forcesData.data['L_ground_force_vz']?.[timeIndex] || 0) +
                            (forcesData.data['R_ground_force_vz']?.[timeIndex] || 0);
              magnitude = Math.sqrt(totalFx * totalFx + totalFy * totalFy + totalFz * totalFz);
  
              if (i < 5) { // Log first few values
                console.log(`Total magnitude calculation [${i}]:`, {
                  targetTime,
                  timeIndex,
                  totalFx,
                  totalFy,
                  totalFz,
                  magnitude
                });
              }
              break;
            }
          }
  
          data.push(magnitude);
        } else {
          data.push(null);
        }
      }
  
      const variableLabel = this.availableVariables.find(v => v.value === variable)?.label || variable;
      const dataset = {
        label: variableLabel,
        data: data,
        borderColor: colors[colorIndex % colors.length],
        backgroundColor: colors[colorIndex % colors.length] + '20',
        fill: false,
        tension: 0.1
      };
  
      console.log(`Generated force dataset for ${variable}:`, {
        label: dataset.label,
        dataLength: data.length,
        firstFewValues: data.slice(0, 5),
        nonNullCount: data.filter(d => d !== null).length
      });
  
      datasets.push(dataset);
      colorIndex++;
    });
  
    console.log('Final force datasets:', datasets.length, 'datasets generated');
    return datasets;
  },
  
  generateForceComponentDatasets(timeData) {
    const datasets = [];
    const forcesData = this.forcesDatasets[this.selectedPlotAnimation];
  
    if (!forcesData) return datasets;
  
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
    let colorIndex = 0;
  
    this.selectedVariables.forEach(variable => {
      const data = [];
      const columnMap = {
        'left_fx': 'L_ground_force_vx',
        'left_fy': 'L_ground_force_vy',
        'left_fz': 'L_ground_force_vz',
        'right_fx': 'R_ground_force_vx',
        'right_fy': 'R_ground_force_vy',
        'right_fz': 'R_ground_force_vz'
      };
  
      const columnName = columnMap[variable];
      if (!columnName || !forcesData.data[columnName]) return;
  
      for (let i = 0; i < timeData.length; i++) {
        const timeIndex = forcesData.time.findIndex(t => Math.abs(t - timeData[i]) < 0.001);
        if (timeIndex !== -1) {
          data.push(forcesData.data[columnName][timeIndex] || 0);
        } else {
          data.push(null);
        }
      }
  
      const variableLabel = this.availableVariables.find(v => v.value === variable)?.label || variable;
      datasets.push({
        label: variableLabel,
        data: data,
        borderColor: colors[colorIndex % colors.length],
        backgroundColor: colors[colorIndex % colors.length] + '20',
        fill: false,
        tension: 0.1
      });
  
      colorIndex++;
    });
  
    return datasets;
  },
  
  generateMarkerDistanceDatasets(timeData) {
    const datasets = [];
    const markersData = this.markersDatasets[this.selectedPlotAnimation];
  
    if (!markersData || this.selectedMarkers.length < 2) return datasets;
  
    const data = [];
    const marker1 = this.selectedMarkers[0];
    const marker2 = this.selectedMarkers[1];
  
    if (!markersData.data[marker1] || !markersData.data[marker2]) return datasets;
  
    for (let i = 0; i < timeData.length; i++) {
      const targetTime = timeData[i];
      let closestIndex = 0;
      let minDiff = Math.abs(markersData.times[0] - targetTime);
  
      for (let j = 1; j < markersData.times.length; j++) {
        const diff = Math.abs(markersData.times[j] - targetTime);
        if (diff < minDiff) {
          minDiff = diff;
          closestIndex = j;
        }
      }
  
      const x1 = markersData.data[marker1].x[closestIndex];
      const y1 = markersData.data[marker1].y[closestIndex];
      const z1 = markersData.data[marker1].z[closestIndex];
      const x2 = markersData.data[marker2].x[closestIndex];
      const y2 = markersData.data[marker2].y[closestIndex];
      const z2 = markersData.data[marker2].z[closestIndex];
  
      if (x1 !== undefined && y1 !== undefined && z1 !== undefined &&
          x2 !== undefined && y2 !== undefined && z2 !== undefined) {
        const distance = Math.sqrt(
          Math.pow(x2 - x1, 2) +
          Math.pow(y2 - y1, 2) +
          Math.pow(z2 - z1, 2)
        );
        data.push(distance);
      } else {
        data.push(null);
      }
    }
  
    datasets.push({
      label: `Distance: ${marker1} - ${marker2}`,
      data: data,
      borderColor: '#FF6384',
      backgroundColor: '#FF638420',
      fill: false,
      tension: 0.1
    });
  
    return datasets;
  },
  
  generateJointAngleDatasets(timeData) {
    const datasets = [];
    const animation = this.animations[this.selectedPlotAnimation];
  
    if (!animation || !animation.data) return datasets;
  
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
    let colorIndex = 0;
  
    this.selectedVariables.forEach(variable => {
      if (!animation.data[variable]) return;
  
      const data = [];
      for (let i = 0; i < timeData.length; i++) {
        const timeIndex = animation.data.time.findIndex(t => Math.abs(t - timeData[i]) < 0.001);
        if (timeIndex !== -1) {
          // Convert radians to degrees for display
          const angleRad = animation.data[variable][timeIndex];
          const angleDeg = angleRad * (180 / Math.PI);
          data.push(angleDeg);
        } else {
          data.push(null);
        }
      }
  
      const variableLabel = this.availableVariables.find(v => v.value === variable)?.label || variable;
      datasets.push({
        label: variableLabel,
        data: data,
        borderColor: colors[colorIndex % colors.length],
        backgroundColor: colors[colorIndex % colors.length] + '20',
        fill: false,
        tension: 0.1
      });
  
      colorIndex++;
    });
  
    return datasets;
  },
  
  generatePelvisTranslationDatasets(timeData) {
    const datasets = [];
    const animation = this.animations[this.selectedPlotAnimation];
  
    if (!animation || !animation.data) return datasets;
  
    const colors = ['#FF6384', '#36A2EB', '#FFCE56'];
    let colorIndex = 0;
  
    this.selectedVariables.forEach(variable => {
      if (!animation.data[variable]) return;
  
      const data = [];
      for (let i = 0; i < timeData.length; i++) {
        const timeIndex = animation.data.time.findIndex(t => Math.abs(t - timeData[i]) < 0.001);
        if (timeIndex !== -1) {
          data.push(animation.data[variable][timeIndex]);
        } else {
          data.push(null);
        }
      }
  
      const variableLabel = this.availableVariables.find(v => v.value === variable)?.label || variable;
      datasets.push({
        label: variableLabel,
        data: data,
        borderColor: colors[colorIndex % colors.length],
        backgroundColor: colors[colorIndex % colors.length] + '20',
        fill: false,
        tension: 0.1
      });
  
      colorIndex++;
    });
  
    return datasets;
  },
  
  getAvailableJointAngles() {
    const animation = this.animations[this.selectedPlotAnimation];
    if (!animation || !animation.data) return [];
  
    const angleColumns = Object.keys(animation.data).filter(key =>
      key.includes('_r') || key.includes('_l') || key.includes('_angle')
    );
  
    return angleColumns.map(column => ({
      label: column.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: column
    }));
  },
  
  updatePlotInRealTime() {
    if (!this.plotUpdatesEnabled || !this.plotChart || !this.plotSettings.showCurrentTime) {
      return;
    }
  
    const currentTime = this.time;
  
    // Update vertical line annotation for current time
    if (this.plotChart.options.plugins.annotation) {
      this.plotChart.options.plugins.annotation.annotations.currentTime.value = currentTime;
    } else {
      this.plotChart.options.plugins.annotation = {
        annotations: {
          currentTime: {
            type: 'line',
            xMin: currentTime,
            xMax: currentTime,
            borderColor: '#FF0000',
            borderWidth: 2,
            label: {
              content: 'Current Time',
              enabled: true,
              position: 'top'
            }
          }
        }
      };
    }
  
    this.plotChart.update('none');
  },
  
  togglePlotUpdates() {
    this.plotUpdatesEnabled = !this.plotUpdatesEnabled;
  },
  
  exportPlot() {
    if (!this.plotChart) return;
  
    const link = document.createElement('a');
    link.download = `plot_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
    link.href = this.plotChart.toBase64Image();
    link.click();
  },
  
  // Dialog drag and resize methods
  startDragPlotDialog(event) {
    event.preventDefault();
    this.isDraggingPlotDialog = true;
  
    const clientX = event.clientX || event.touches[0].clientX;
    const clientY = event.clientY || event.touches[0].clientY;
  
    this.plotDragOffset = {
      x: clientX - this.plottingDialogPosition.x,
      y: clientY - this.plottingDialogPosition.y
    };
  
    document.addEventListener('mousemove', this.onDragPlotDialog);
    document.addEventListener('mouseup', this.stopDragPlotDialog);
    document.addEventListener('touchmove', this.onDragPlotDialog);
    document.addEventListener('touchend', this.stopDragPlotDialog);
  },
  
  onDragPlotDialog(event) {
    if (!this.isDraggingPlotDialog) return;
  
    const clientX = event.clientX || event.touches[0].clientX;
    const clientY = event.clientY || event.touches[0].clientY;
  
    this.plottingDialogPosition = {
      x: Math.max(0, Math.min(window.innerWidth - 300, clientX - this.plotDragOffset.x)),
      y: Math.max(0, Math.min(window.innerHeight - 100, clientY - this.plotDragOffset.y))
    };
  },
  
  stopDragPlotDialog() {
    this.isDraggingPlotDialog = false;
    document.removeEventListener('mousemove', this.onDragPlotDialog);
    document.removeEventListener('mouseup', this.stopDragPlotDialog);
    document.removeEventListener('touchmove', this.onDragPlotDialog);
    document.removeEventListener('touchend', this.stopDragPlotDialog);
  },
  
  startResizePlotDialog(event) {
    event.preventDefault();
    event.stopPropagation();
  
    this.isResizingPlotDialog = true;
  
    const clientX = event.clientX || event.touches[0].clientX;
    const clientY = event.clientY || event.touches[0].clientY;
  
    this.plotResizeStartPosition = { x: clientX, y: clientY };
    this.plotResizeStartSize = { ...this.plottingDialogSize };
  
    document.addEventListener('mousemove', this.onResizePlotDialog);
    document.addEventListener('mouseup', this.stopResizePlotDialog);
    document.addEventListener('touchmove', this.onResizePlotDialog);
    document.addEventListener('touchend', this.stopResizePlotDialog);
  },
  
  onResizePlotDialog(event) {
    if (!this.isResizingPlotDialog) return;
  
    const clientX = event.clientX || event.touches[0].clientX;
    const clientY = event.clientY || event.touches[0].clientY;
  
    const deltaX = clientX - this.plotResizeStartPosition.x;
    const deltaY = clientY - this.plotResizeStartPosition.y;
  
    this.plottingDialogSize = {
      width: Math.max(600, this.plotResizeStartSize.width + deltaX),
      height: Math.max(400, this.plotResizeStartSize.height + deltaY)
    };
  
    // Update chart size
    this.$nextTick(() => {
      if (this.plotChart) {
        this.plotChart.resize();
      }
    });
  },
  
  stopResizePlotDialog() {
    this.isResizingPlotDialog = false;
    document.removeEventListener('mousemove', this.onResizePlotDialog);
    document.removeEventListener('mouseup', this.stopResizePlotDialog);
    document.removeEventListener('touchmove', this.onResizePlotDialog);
    document.removeEventListener('touchend', this.stopResizePlotDialog);
  }
  }
  }
  </script>
  
  <style scoped>
  .viewer-container {
  height: 100vh;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }
  
  /* Fix for settings dialogs z-index */
  :deep(.v-dialog) {
  z-index: 99999 !important;
  }
  
  /* Ensure settings buttons are clickable */
  .settings-text-btn {
  position: relative;
  z-index: 2;
  }
  
  /* Fix for color picker UI */
  :deep(.v-color-picker) {
  .v-color-picker__canvas {
    cursor: crosshair;
    position: relative;
    width: 100%;
    height: 100%;
  
    &-dot {
      position: absolute;
      top: 0;
      left: 0;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 1px solid white;
      box-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
      transform: translate(-50%, -50%);
    }
  }
  }
  
  #mocap {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: visible;
  }
  
  /* Ensure camera controls are positioned correctly */
  #mocap :deep(.camera-controls-container) {
  position: absolute;
  bottom: 80px; /* Position above the timeline controls */
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  }
  
  .controls-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: rgba(0, 0, 0, 0.7);
  padding: 0 10px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  z-index: 5; /* Ensure controls are above viewer content */
  }
  
  .left,
  .right {
  position: absolute;
  top: 10px;
  bottom: 70px; /* Position above controls container (60px height + 10px margin) */
  width: 330px;
  background: rgba(28, 28, 30, 0.9); /* Dark semi-transparent */
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  padding: 15px;
  z-index: 10; /* Ensure sidebars are above the viewer */
  overflow-y: auto; /* Allow scrolling within sidebars */
  overflow-x: hidden; /* Prevent horizontal scrolling */
  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  }
  
  .left::-webkit-scrollbar,
  .right::-webkit-scrollbar {
  width: 6px;
  }
  .left::-webkit-scrollbar-thumb,
  .right::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  }
  .left::-webkit-scrollbar-track,
  .right::-webkit-scrollbar-track {
  background: transparent;
  }
  
  .left {
  left: 10px;
  }
  
  .left.hidden {
  transform: translateX(-110%);
  opacity: 0;
  pointer-events: none;
  }
  
  
  
  .right {
  right: 10px;
  }
  
  .right.hidden {
  transform: translateX(110%);
  opacity: 0;
  pointer-events: none;
  }
  
  /* Ensure content stays contained in sidebars */
  .left .left-content,
  .right .right-content {
  flex-grow: 1;
  min-height: 100%;
  position: relative;
  overflow-y: visible;
  }
  
  /* Fix for titles and headers to stay within sidebar */
  .left h2,
  .right h2,
  .left .text-subtitle-2,
  .right .text-subtitle-2 {
  position: relative;
  }
  
  .left-sidebar-toggle,
  .sidebar-toggle {
  position: absolute;
  top: 15px; /* Align with sidebar top */
  z-index: 11; /* Above sidebars */
  background: rgba(40, 40, 40, 0.8);
  border-radius: 50%;
  transition: transform 0.3s ease-in-out;
  }
  
  .left-sidebar-toggle {
  left: 15px; /* Position near left sidebar */
  }
  
  .left-sidebar-toggle.sidebar-open {
  transform: translateX(340px); /* Move with sidebar (width + padding/margin) */
  }
  
  .sidebar-toggle {
  right: 15px; /* Position near right sidebar */
  }
  
  .sidebar-toggle.sidebar-open {
  transform: translateX(-340px); /* Move with sidebar (width + padding/margin) */
  }

  /* GitHub link button */
  .github-link-btn {
    position: absolute;
    bottom: 80px;
    left: 15px;
    z-index: 11;
    background: rgba(40, 40, 40, 0.8) !important;
    border-radius: 50%;
    transition: all 0.2s ease;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    display: flex !important;
    align-items: center;
    justify-content: center;
  }

  .github-link-btn .github-icon {
    width: 20px;
    height: 20px;
    fill: rgba(255, 255, 255, 0.9) !important;
    display: block;
  }

  .github-link-btn:hover .github-icon {
    fill: white !important;
  }

  .github-link-btn:hover {
    background: rgba(60, 60, 60, 0.9) !important;
    transform: scale(1.1);
  }

  /* GitHub logo in popup */
  .github-logo-popup {
    width: 48px;
    height: 48px;
    fill: rgba(255, 255, 255, 0.9);
  }

  /* Legend and Controls specific styles */
  .left .left-content, .right .right-content /* Define a content wrapper if needed */ {
  flex-grow: 1;
  /* Potentially add overflow-y: auto here if header/footer is fixed */
  }
  
  .legend {
  flex-grow: 1;
  position: relative;
  width: 100%;
  }
  
  .legend-item {
  position: relative;
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  overflow: hidden;
  box-sizing: border-box;
  }
  
  /* Ensure control button rows are contained */
  .legend-item .d-flex.align-center.ml-8 {
    max-width: 100%;
    box-sizing: border-box;
  }
  
  .legend-item .d-flex.align-center.ml-8 .v-btn {
    flex-shrink: 0;
  }
  
  .legend-item.active-subject {
  border: 1px solid rgba(0, 255, 255, 0.35);
  background: rgba(0, 255, 255, 0.08);
  }
  
  .legend-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  }
  
  .color-box {
  width: 24px;
  height: 24px;
        border-radius: 4px;
        margin-top: 4px;
  flex-shrink: 0;
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
  
  .file-name,
  .fps-info {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2px;
  }

  .color-box.selectable {
  cursor: pointer;
  }

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
  
  .offset-controls {
  .v-text-field {
    input {
      color: rgba(255, 255, 255, 0.7) !important;
      text-align: center;
    }
    .v-input__slot {
      padding: 0 4px !important;
    }
  }
  }
  
  .drop-zone {
    width: calc(100% - 40px);
    height: auto;
    min-height: 400px;
    max-height: calc(100vh - 120px);
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    border: 3px dashed rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    margin: 20px;
    padding: 20px;
    transition: all 0.3s ease;
    position: relative;
    z-index: 1;
  }
  
  .drop-zone:hover {
        border-color: rgba(255, 255, 255, 0.4);
        background: rgba(255, 255, 255, 0.08);
  }
  
  .welcome-section {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
  
  .custom-btn {
  border-radius: 8px !important;
  font-weight: 500 !important;
  letter-spacing: 0.025em !important;
  text-transform: none !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.2s ease !important;
  font-family: inherit !important;
  }
  
  
  .import-dialog {
  .v-card {
    background-color: #1E1E1E;
    color: #FFFFFF;
    border-radius: 12px;
    overflow: hidden;
  }
  
  .v-card-title {
    background-color: #282828;
    font-size: 1.6rem;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .v-card-text {
    color: #FFFFFF;
    padding: 30px;
  }
  
  .v-card-actions {
    background-color: #282828;
    padding: 12px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  }
  
  .share-dialog {
  .v-card {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    overflow: hidden;
  }
  
  .v-card-title {
    background-color: #282828 !important;
    color: #FFFFFF !important;
    font-size: 1.6rem;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .v-card-text {
    color: #FFFFFF !important;
    padding: 30px;
    background-color: #1E1E1E !important;
  }
  
  .v-card-actions {
    background-color: #282828 !important;
    padding: 12px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .v-text-field input {
    color: #FFFFFF !important;
  }
  
  .v-text-field .v-label {
    color: rgba(255, 255, 255, 0.7) !important;
  }
  
  .v-expansion-panels {
    background-color: transparent !important;
  }
  
  .v-expansion-panel {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #FFFFFF !important;
  }
  
  .v-expansion-panel-header {
    color: #FFFFFF !important;
  }
  
  .v-expansion-panel-content {
    background-color: rgba(255, 255, 255, 0.02) !important;
  }
  
  .v-btn {
    color: #FFFFFF !important;
  }
  
  .v-alert {
    background-color: rgba(255, 193, 7, 0.1) !important;
    border: 1px solid rgba(255, 193, 7, 0.3) !important;
    color: #FFC107 !important;
  }
  
  .v-tabs {
    background-color: transparent !important;
  }
  
  .v-tab {
    color: rgba(255, 255, 255, 0.7) !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
    margin-right: 8px !important;
    border-radius: 4px !important;
  }
  
  .v-tab--active {
    color: #FFFFFF !important;
    background-color: rgba(33, 150, 243, 0.3) !important;
  }
  
  .v-tabs-slider {
    display: none !important;
  }
  
  .v-tabs-items {
    background-color: transparent !important;
  }
  
  .v-tab-item {
    background-color: transparent !important;
  }
  }
  
  .import-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
  
  .import-item {
    background-color: #282828;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    border: 1px solid rgba(255, 255, 255, 0.1);
  
    &:hover {
      background-color: #333333;
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
  
    .v-icon {
      font-size: 36px;
      margin-bottom: 12px;
      display: block;
      margin: 0 auto 12px;
    }
  
    .import-item-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 4px;
    }
  
    .import-item-subtitle {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.7);
    }
  }
  
  .disabled {
    opacity: 0.6;
    cursor: not-allowed;
  
    &:hover {
      transform: none;
      background-color: #282828;
      box-shadow: none;
    }
  }
  }
  
  .v-tooltip__content {
  background: rgba(50, 50, 50, 0.9) !important;
  border-radius: 4px;
  font-size: 12px;
  }
  
  .color-sample {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .color-preview {
  width: 24px !important;
  height: 24px !important;
  min-width: 24px !important;
  border-radius: 4px !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  }
  
  .color-picker {
  background: #1E1E1E !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  }
  
  .color-picker .v-btn {
  margin: 2px;
  padding: 0;
  min-width: 32px !important;
  width: 32px !important;
  height: 32px !important;
  }
  
  .color-picker .color-sample {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .ground-controls {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  }
  
  .ground-controls .v-btn {
  justify-content: flex-start;
  padding-left: 8px;
  text-transform: none;
  letter-spacing: normal;
  }
  
  .playable-checkbox {
  min-width: 40px;
  max-width: 40px;
  overflow: hidden;
  }
  
  .playable-checkbox :deep(.v-input--selection-controls__input) {
  margin-right: 0;
  }
  
  @keyframes pulse-red {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
  }
  
  .pulse-recording {
  animation: pulse-red 1.5s infinite;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  }
  
  .recording-summary {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 6px 8px;
  }
  
  .recording-settings-dialog {
  background-color: #222222 !important;
  color: #FFFFFF;
  }
  
  .info-box {
  background-color: rgba(25, 118, 210, 0.1);
  border-left: 3px solid #1976D2;
  border-radius: 4px;
  }
  
  .settings-text-btn {
  font-size: 12px !important;
  letter-spacing: 0.5px !important;
  text-transform: none !important;
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
  padding: 0 12px !important;
  height: 28px !important;
  min-width: 70px !important;
  }
  
  .settings-text-btn:hover {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.7) !important;
  }
  
  .camera-controls-wrapper {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  pointer-events: auto;
  }
  
  /* Beautiful Loading UI */
  .conversion-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg,
    rgba(15, 23, 42, 0.95) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(51, 65, 85, 0.95) 100%);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  color: white;
  text-align: center;
  padding: 40px;
  }
  
  .conversion-overlay .v-progress-circular {
  margin-bottom: 32px;
  filter: drop-shadow(0 4px 8px rgba(79, 70, 229, 0.4));
  }
  
  .conversion-overlay .text-h6 {
  font-size: 1.75rem !important;
  font-weight: 600 !important;
  line-height: 1.4 !important;
  margin-bottom: 16px;
  background: linear-gradient(45deg, #e2e8f0, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .conversion-overlay .text-subtitle-1 {
  font-size: 1.1rem !important;
  font-weight: 400 !important;
  color: rgba(255, 255, 255, 0.8) !important;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
  opacity: 0.9;
  }
  
  @keyframes pulse-glow {
  0%, 100% {
    filter: drop-shadow(0 4px 8px rgba(79, 70, 229, 0.4));
  }
  50% {
    filter: drop-shadow(0 6px 16px rgba(79, 70, 229, 0.6));
  }
  }
  
  .conversion-overlay .v-progress-circular {
  animation: pulse-glow 2s ease-in-out infinite;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
  .conversion-overlay {
    padding: 20px;
  }
  
  .conversion-overlay .text-h6 {
    font-size: 1.5rem !important;
  }
  
  .conversion-overlay .text-subtitle-1 {
    font-size: 1rem !important;
  }
  }
  
  /* Scene overlay for conversion loading */
  .conversion-overlay-scene {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  }
  
  .conversion-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
  background: rgba(30, 41, 59, 0.9);
  border-radius: 16px;
  border: 1px solid rgba(79, 70, 229, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
  
  .conversion-content .v-progress-circular {
  margin-bottom: 24px;
  filter: drop-shadow(0 4px 8px rgba(79, 70, 229, 0.4));
  }
  
  .conversion-content .text-h6 {
  font-size: 1.5rem !important;
  font-weight: 600 !important;
  line-height: 1.4 !important;
  margin-bottom: 12px;
  color: white !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .conversion-content .text-subtitle-1 {
  font-size: 1rem !important;
  font-weight: 400 !important;
  color: rgba(255, 255, 255, 0.8) !important;
  line-height: 1.5;
  }
  
  /* Responsive adjustments for scene overlay */
  @media (max-width: 768px) {
  .conversion-content {
    padding: 24px;
    margin: 20px;
  }
  
  .conversion-content .text-h6 {
    font-size: 1.25rem !important;
  }
  
  .conversion-content .text-subtitle-1 {
    font-size: 0.9rem !important;
  }
  }
  
  /* Sample Selection Dialog Styles */
  .sample-selection-dialog .v-dialog {
  background: rgba(30, 30, 30, 0.95);
  backdrop-filter: blur(10px);
  }
  
  .sample-selection-dialog-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .sample-option-col {
  padding: 8px !important;
  }
  
  .sample-option-card {
  height: 160px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  }
  
  .sample-option-card.full-width-sample {
  height: auto;
  }
  
  .sample-option-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3) !important;
  border-color: rgba(33, 150, 243, 0.5) !important;
  background: rgba(33, 150, 243, 0.1) !important;
  }
  
  .sample-option-card .v-icon {
  transition: all 0.3s ease;
  }
  
  .sample-option-card:hover .v-icon {
  transform: scale(1.1);
  color: #2196F3 !important;
  }
  
  .sample-option-card .text-h6 {
  font-weight: 600;
  }
  
  /* Plotting dialog styles */
  .plotting-dialog {
  background: transparent !important;
  box-shadow: none !important;
  }
  
  .plotting-dialog-card {
  background: #1e1e1e !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  }
  
  .plot-controls-panel {
  background: #2a2a2a !important;
  border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  }
  
  .plot-display-panel {
  background: #1e1e1e !important;
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-input--selection-controls {
  margin-top: 0 !important;
  }
  
  .plotting-dialog .v-input--selection-controls .v-input__slot {
  margin-bottom: 0 !important;
  }
  
  .plotting-dialog .v-select--chips .v-chip {
  margin: 2px !important;
  }
  
  /* Dark theme styles for plotting dialog form controls */
  .plotting-dialog .v-select {
  background: rgba(255, 255, 255, 0.05) !important;
  border-radius: 4px !important;
  }
  
  .plotting-dialog .v-input {
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-input input {
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-input .v-label {
  color: rgba(255, 255, 255, 0.7) !important;
  }
  
  .plotting-dialog .v-select__selections {
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-select__selection {
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-chip {
  background: rgba(33, 150, 243, 0.2) !important;
  color: #ffffff !important;
  border: 1px solid rgba(33, 150, 243, 0.3) !important;
  }
  
  .plotting-dialog .v-checkbox {
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-checkbox .v-label {
  color: #ffffff !important;
  }
  
  .plotting-dialog .v-range-slider {
  color: #2196F3 !important;
  }
  
  .plotting-dialog .text-caption {
  color: rgba(255, 255, 255, 0.8) !important;
  }
  
  .plotting-dialog .text-subtitle-2 {
  color: #ffffff !important;
  }
  
  .plotting-dialog .text--disabled {
  color: rgba(255, 255, 255, 0.5) !important;
  }
  
  .plotting-dialog .v-icon {
  color: rgba(255, 255, 255, 0.7) !important;
  }
  
  .plotting-dialog .text-h6 {
  color: rgba(255, 255, 255, 0.8) !important;
  }
  
  .plotting-header {
  border-top-left-radius: 12px !important;
  border-top-right-radius: 12px !important;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
  }
  
  .resize-handle {
  opacity: 0.5;
  transition: opacity 0.2s ease;
  }
  
  .resize-handle:hover {
  opacity: 1;
  }
  
  /* ... rest of existing styles ... */
  </style>