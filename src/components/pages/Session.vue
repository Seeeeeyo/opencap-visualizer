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
          @timeupdate="handleVideoTimeUpdate"
          :loop="isLooping"
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
            
            <!-- Add Import Button Here -->
            <v-btn color="#4B5563" class="mb-4 white--text custom-btn" block @click="openImportDialog" :disabled="converting">
              <v-icon left>mdi-import</v-icon>
              Import
            </v-btn>
            

            
            <!-- Getting Started Section (shown when no files are loaded) -->
            <div v-if="animations.length === 0 && !converting && Object.keys(markersDatasets).length === 0" class="getting-started-section mb-4">
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
                      Add forces, video, or 3D models
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
                </ul>
              </v-card>
            </div>
            
            <!-- Legend -->
            <div class="legend flex-grow-1 mb-4">
              <!-- Add animation control buttons -->
              <div class="d-flex align-center mb-4" v-if="animations.length > 0">
                <div class="text-subtitle-2 mr-2">Animations</div>
                <v-spacer></v-spacer>
                <v-btn x-small text color="primary" @click="setAllAnimationsPlayable(true)" class="mr-1">
                  <v-icon x-small left>mdi-play-circle</v-icon>
                  All
                </v-btn>
                <v-btn x-small text color="grey" @click="setAllAnimationsPlayable(false)">
                  <v-icon x-small left>mdi-pause-circle</v-icon>
                  None
                </v-btn>
              </div>
              
              <!-- Animation Files List -->
              <div v-for="(animation, index) in animations" :key="`animation-${index}`" class="legend-item mb-4">
                <div class="d-flex mb-2">
                  <div class="color-box" :style="{ backgroundColor: formatColor(colors[index]) }"></div>
                  <div class="ml-2" style="flex-grow: 1; min-width: 0;">
                    <v-text-field v-model="animation.trialName" dense hide-details class="trial-name-input" />
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
                </div>
                
                <!-- Buttons row - add checkbox here -->
                <div class="d-flex align-center ml-8" style="min-width: 300px;">
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



              <!-- Forces Visualization Section -->
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
                  
                  <v-btn icon small class="mr-2" @click="clearForceArrowsForAnimation(animationIndex)">
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                </div>
                
                <!-- Divider -->
                <v-divider class="mt-4" style="opacity: 0.2"></v-divider>
              </div>

              <!-- Custom Objects List -->
              <div v-for="obj in customObjects" :key="obj.id" class="legend-item mb-4">
                <div class="d-flex mb-2">
                  <div class="color-box" :style="{ backgroundColor: obj.color }"></div>
                  <div class="ml-2" style="flex-grow: 1;">
                    <v-text-field v-model="obj.name" dense hide-details class="trial-name-input" />
                    <div class="file-name text-caption">{{ obj.name }}</div>
                  </div>
                </div>
                
                <!-- Buttons row -->
                <div class="d-flex align-center ml-8" style="min-width: 300px;">
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
            
            <!-- Standalone Marker Visualization Section (when no animations exist) -->
            <template v-if="animations.length === 0 && Object.keys(markersDatasets).length > 0">
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
            
            <!-- Clear All Markers Button (only show when there are multiple marker files) -->
            <div v-if="animations.length === 0 && Object.keys(markersDatasets).length > 1" class="mb-4">
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
            <template v-if="animations.length > 0">
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
        <div v-if="trial || (markerSpheres.length > 0) || (animations.length > 0) || trialLoading || converting || conversionError" class="d-flex flex-column h-100">
          <div id="mocap" ref="mocap" class="flex-grow-1 position-relative">
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
              <div style="flex: 0.1; min-width: 10px; margin-right: 5px; display: flex; align-items: center;">
                <v-text-field type="number" :step="0.01" :value="formattedTime" dark style="flex: 1;" @input="onChangeTime" />
                <span class="ml-1 white--text">(s)</span>
              </div>
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
          
          <div class="text-center drop-zone" :class="{ 'opacity-reduced': converting }" @click="openFileBrowser">
            <!-- Welcome Documentation Section -->
            <div v-if="!converting && !conversionError" class="welcome-section pa-6 text-center" style="max-width: 800px;">
              <div class="mb-6">
                <v-icon size="48" color="primary" class="mb-3">mdi-human-handsup</v-icon>
                <h1 class="text-h4 white--text mb-2">Welcome to OpenCap Visualizer</h1>
                <p class="text-subtitle-1 grey--text">
                  Visualize and analyze human motion capture data in 3D
                </p>
              </div>
              
              <v-row class="mb-6">
                <v-col cols="12" md="6">
                  <v-card dark class="pa-4 h-100" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="32" color="indigo" class="mb-3">mdi-file-document-outline</v-icon>
                    <h3 class="text-h6 mb-3">Supported File Types</h3>
                    <div class="text-left">
                      <div class="mb-2">
                        <v-chip small color="indigo" dark class="mr-2">JSON</v-chip>
                        <span class="text-caption">Pre-processed motion data</span>
                      </div>

                                           <div class="mb-2">
                         <v-chip small color="orange" dark class="mr-2">OSIM + MOT</v-chip>
                         <span class="text-caption">OpenSim models & motion</span>
                       </div>
                       <div class="mb-2">
                         <v-chip small color="red" dark class="mr-2">Forces</v-chip>
                         <span class="text-caption">Ground reaction forces (.mot)</span>
                       </div>
                       <div class="mb-2">
                         <v-chip small color="purple" dark class="mr-2">TRC</v-chip>
                         <span class="text-caption">Motion capture marker files</span>
                       </div>
                       <div class="mb-2">
                         <v-chip small color="cyan" dark class="mr-2">MP4/WebM</v-chip>
                         <span class="text-caption">Video files for sync</span>
                       </div>
                    </div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-card dark class="pa-4 h-100" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="32" color="green" class="mb-3">mdi-play-circle-outline</v-icon>
                    <h3 class="text-h6 mb-3">Quick Start</h3>
                                       <div class="text-left">
                       <ol class="text-caption pl-4">
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
              
              <v-row class="mb-6">
                <v-col cols="12" md="4">
                  <v-card dark class="pa-4 h-100" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="24" color="blue" class="mb-2">mdi-mouse-move-up</v-icon>
                    <h4 class="text-subtitle-1 mb-2">Navigation</h4>
                    <div class="text-caption text-left">
                      <div class="mb-1">• Left click + drag to orbit</div>
                      <div class="mb-1">• Right click + drag to pan</div>
                      <div class="mb-1">• Scroll wheel to zoom</div>
                    </div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-card dark class="pa-4 h-100" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="24" color="purple" class="mb-2">mdi-palette</v-icon>
                    <h4 class="text-subtitle-1 mb-2">Customization</h4>
                    <div class="text-caption text-left">
                      <div class="mb-1">• Change colors & transparency</div>
                      <div class="mb-1">• Show/hide body parts</div>
                      <div class="mb-1">• Adjust playback speed</div>
                    </div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-card dark class="pa-4 h-100" style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <v-icon size="24" color="red" class="mb-2">mdi-record-circle</v-icon>
                    <h4 class="text-subtitle-1 mb-2">Export</h4>
                    <div class="text-caption text-left">
                      <div class="mb-1">• Record high-quality videos</div>
                      <div class="mb-1">• Capture screenshots</div>
                      <div class="mb-1">• Share visualizations</div>
                    </div>
                  </v-card>
                </v-col>
              </v-row>
            </div>
            
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
              <span class="text-caption">Supports .json, .trc, .osim, .mot, and video files</span>
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
            <v-btn color="#2563EB" class="mb-4 white--text custom-btn" block @click="openShareDialog" :disabled="!trial || animations.length === 0">
              <v-icon left>mdi-share-variant</v-icon>
              Share Visualization
            </v-btn>
            
            <v-btn color="#4B5563" class="mb-4 white--text custom-btn" block @click="showPlottingDialog = true" :disabled="!trial && animations.length === 0">
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
        <v-dialog v-model="showImportDialog" max-width="600" content-class="import-dialog">
          <v-card class="import-dialog-card">
            <v-card-title class="headline">Import Files </v-card-title>
            <v-card-text>
              <div class="import-grid">
                <!-- OpenSim -->
                <div class="import-item" @click="selectFileType('osimMotFileInput')">
                  <v-icon size="32">mdi-file-document-outline</v-icon>
                  <div class="import-item-title">OpenSim</div>
                  <div class="import-item-subtitle">.mot + .osim</div>
                </div>
                
                <!-- Forces -->
                <div class="import-item" @click="openForcesDialogFromImport">
                  <v-icon size="32">mdi-vector-line</v-icon>
                  <div class="import-item-title">Forces</div>
                  <div class="import-item-subtitle">.mot format</div>
                </div>
                
                <!-- Markers -->
                <div class="import-item" @click="openMarkersDialogFromImport">
                  <v-icon size="32">mdi-record-circle-outline</v-icon>
                  <div class="import-item-title">Markers</div>
                  <div class="import-item-subtitle">.trc format</div>
                </div>
                
                <!-- JSON Files -->
                <div class="import-item" @click="selectFileType('fileInput')">
                  <v-icon size="32">mdi-file</v-icon>
                  <div class="import-item-title">JSON Files</div>
                  <div class="import-item-subtitle">OpenCap Format</div>
                </div>
                
                <!-- Video -->
                <div class="import-item" @click="selectFileType('videoFileInput')">
                  <v-icon size="32">mdi-play-circle-outline</v-icon>
                  <div class="import-item-title">Video</div>
                  <div class="import-item-subtitle">MP4, WEBM</div>
                </div>
                
                <!-- 3D Model -->
                <div class="import-item" @click="selectFileType('objFileInput')">
                  <v-icon size="32">mdi-cube-outline</v-icon>
                  <div class="import-item-title">3D Model</div>
                  <div class="import-item-subtitle">GLTF, STL, FBX, OBJ</div>
                </div>
              </div>
       
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text @click="showImportDialog = false">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Add Forces Dialog -->
        <v-dialog v-model="showForcesDialog" max-width="500" content-class="forces-dialog">
          <v-card class="forces-dialog-card">
            <v-card-title class="headline">Import Ground Reaction Forces</v-card-title>
            <v-card-text>
              <div class="text-body-1 mb-4">
                Select a .mot forces file to visualize ground reaction forces at the subject's feet. 
                Forces will be automatically positioned at the foot segments of the selected animation.
              </div>
              
              <v-alert v-if="animations.length === 0" type="warning" text dense class="mb-4">
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
              
              <v-alert v-if="animations.length === 0" type="info" text dense class="mb-4">
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
        <v-dialog v-model="showSampleSelectionDialog" max-width="600" content-class="sample-selection-dialog">
          <v-card class="sample-selection-dialog-card">
            <v-card-title class="headline white--text">
              <v-icon left color="primary">mdi-play-circle</v-icon>
              Choose Sample Motion Set
            </v-card-title>
            <v-card-text class="white--text pt-8">
              <div class="text-body-2 mb-4">
                Select a motion capture set to explore the visualizer's capabilities:
              </div>
              
              <v-row>
                <v-col 
                  cols="12" 
                  md="4" 
                  v-for="sampleSet in availableSampleSets" 
                  :key="sampleSet.id"
                  class="sample-option-col"
                >
                  <v-card 
                    class="sample-option-card"
                    :class="{ 'sample-option-hover': true }"
                    @click="selectSampleSet(sampleSet.id)"
                    dark
                    outlined
                  >
                    <v-card-text class="pa-4 text-center">
                      <v-icon size="48" color="primary" class="mb-3">
                        {{ getSampleIcon(sampleSet.id) }}
                      </v-icon>
                      <div class="text-h6 mb-2">{{ sampleSet.name }}</div>
                      <div class="text-caption grey--text">{{ sampleSet.description }}</div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              
              <div class="text-caption grey--text mt-4 text-center">
                <v-icon small class="mr-1">mdi-information-outline</v-icon>
                Each set contains multiple motion capture files with different analysis methods capture methods (WHAM, OpenCap Monocular and OpenCap 2 cameras)
              </div>
            </v-card-text>
            
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text @click="showSampleSelectionDialog = false">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Share Dialog -->
        <v-dialog v-model="showShareDialog" max-width="600" content-class="share-dialog">
          <v-card class="share-dialog-card">
            <v-card-title class="headline white--text">Share Visualization</v-card-title>
            <v-card-text class="white--text pt-8">
              <div class="mb-4">
                <p class="text-body-2 mb-3">Share your visualization with others using a direct link:</p>
                
                <!-- Share Options Tabs -->
                <v-tabs v-model="shareMethod" background-color="transparent" color="primary" class="mb-4 mt-8">
                  <v-tab key="url">Share URL</v-tab>
                  <v-tab key="file">Share File</v-tab>
                </v-tabs>

                <v-tabs-items v-model="shareMethod">
                  <!-- URL Sharing -->
                  <v-tab-item key="url">
                    <v-text-field
                      v-model="shareUrl"
                      label="Share URL"
                      readonly
                      outlined
                      dense
                      class="mb-3 mt-6"
                      append-icon="mdi-content-copy"
                      @click:append="copyToClipboard(shareUrl)"
                      hide-details
                      :loading="loadingInitialShare"
                      :placeholder="loadingInitialShare ? 'Generating share URL...' : ''"
                      :append-icon-disabled="loadingInitialShare || !shareUrl"
                    />
                    
                    <div class="d-flex flex-wrap gap-2 mb-3">
                      <v-btn small color="green" @click="openInNewTab(shareUrl)" :disabled="loadingInitialShare || !shareUrl">
                        <v-icon left small>mdi-open-in-new</v-icon>
                        Open in New Tab
                      </v-btn>
                    </div>

                    <v-alert
                      v-if="shareUrl.includes('shareId=')"
                      type="info"
                      dense
                      text
                      class="mb-3"
                    >
                      <v-icon left small>mdi-information</v-icon>
                      Using compact share ID. This link works as long as you don't clear browser data.
                    </v-alert>
                    
                    <v-alert
                      v-else-if="shareUrlSize > 8000"
                      type="warning"
                      dense
                      text
                      class="mb-3"
                    >
                      <v-icon left small>mdi-alert</v-icon>
                      Large URL ({{ Math.round(shareUrlSize / 1000) }}KB). Consider using file sharing instead.
                    </v-alert>
                  </v-tab-item>

                  <!-- File Sharing -->
                  <v-tab-item key="file">
                    <p class="text-body-2 mb-3">Download a share file that others can import:</p>
                    
                    <v-text-field
                      v-model="shareFileName"
                      label="File name"
                      outlined
                      dense
                      suffix=".json"
                      class="mb-3"
                      hide-details
                    />
                    
                    <div class="d-flex flex-wrap gap-2 mb-3">
                      <v-btn small color="success" @click="downloadShareFile">
                        <v-icon left small>mdi-download</v-icon>
                        Download Share File
                      </v-btn>
                    </div>

                    <v-alert
                      type="info"
                      dense
                      text
                      class="mb-3"
                    >
                      <v-icon left small>mdi-information</v-icon>
                      Recipients can import this file using the "Import" button.
                    </v-alert>
                  </v-tab-item>
                </v-tabs-items>
                
                <!-- Share Settings -->
                <v-expansion-panels flat>
                  <v-expansion-panel>
                    <v-expansion-panel-header class="text-body-2">
                      <v-icon left small>mdi-cog</v-icon>
                      Advanced Settings
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <v-checkbox
                        v-model="shareSettings.includeCamera"
                        label="Include camera position"
                        dense
                        hide-details
                        class="mb-2"
                      />
                      <v-checkbox
                        v-model="shareSettings.includeColors"
                        label="Include custom colors"
                        dense
                        hide-details
                        class="mb-2"
                      />
                      <v-checkbox
                        v-model="shareSettings.includeCurrentFrame"
                        label="Start at current frame"
                        dense
                        hide-details
                        class="mb-3"
                      />
                      <v-btn small outlined @click="generateShareUrl" :loading="generatingShareUrl">
                        <v-icon left small>mdi-refresh</v-icon>
                        Update Share URL
                      </v-btn>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text @click="showShareDialog = false">Close</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

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
        <div class="scene-section mb-4 pa-3" style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
          <div class="section-title mb-3" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">Scene Settings</div>
          
          <!-- Scene settings row -->
          <div class="scene-settings">
            <!-- Background setting -->
            <div class="d-flex align-center mb-3">
              <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Background:</div>
              <v-menu offset-y :close-on-content-click="false">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn small v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: backgroundColor }"></v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex align-center">
                    <v-color-picker
                      v-model="backgroundColor"
                      :modes="['hex', 'rgba']"
                      show-swatches
                      :swatches="Array.isArray(backgroundColors) ? backgroundColors : []"
                      @input="updateBackgroundColor"
                      class="flex-grow-1"
                    ></v-color-picker>
                    <v-btn icon small @click="openEyeDropper('backgroundColor')" title="Pick color from screen" class="ml-2">
                      <v-icon>mdi-eyedropper-variant</v-icon>
                    </v-btn>
                  </div>
                </v-card>
              </v-menu>
            </div>
            
            <!-- Ground setting -->
            <div class="d-flex align-center mb-3">
              <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Ground:</div>
              <v-menu offset-y :close-on-content-click="false">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn small v-bind="attrs" v-on="on" class="color-preview" :style="{ backgroundColor: showGround ? groundColor : 'transparent', border: !showGround ? '1px dashed rgba(255,255,255,0.5)' : '1px solid rgba(255,255,255,0.3)' }"></v-btn>
                </template>
                <v-card class="color-picker pa-2">
                  <div class="d-flex align-center">
                    <v-color-picker
                      v-model="groundColor"
                      :modes="['hex', 'rgba']"
                      show-swatches
                      :swatches="Array.isArray(groundColors) ? groundColors : []"
                      @input="updateGroundColor"
                      :disabled="!showGround"
                      class="flex-grow-1"
                    ></v-color-picker>
                    <v-btn icon small @click="openEyeDropper('groundColor')" title="Pick color from screen" class="ml-2" :disabled="!showGround">
                      <v-icon>mdi-eyedropper-variant</v-icon>
                    </v-btn>
                  </div>
                  <v-divider class="my-2"></v-divider>
                  <div class="ground-controls pa-2">
                    <v-btn small text block @click="toggleGroundVisibility" class="mb-2">
                      <v-icon left small>{{ showGround ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      {{ showGround ? 'Hide Ground' : 'Show Ground' }}
                    </v-btn>
                    <v-btn small text block @click="toggleGroundTexture" :disabled="!showGround" class="mb-2">
                      <v-icon left small>{{ useGroundTexture ? 'mdi-texture-box' : 'mdi-checkbox-blank-outline' }}</v-icon>
                      {{ useGroundTexture ? 'Remove Texture' : 'Use Texture' }}
                    </v-btn>
                    <v-btn small text block @click="toggleCheckerboard" :disabled="!showGround || !useGroundTexture">
                      <v-icon left small>{{ useCheckerboard ? 'mdi-grid' : 'mdi-view-grid' }}</v-icon>
                      {{ useCheckerboard ? 'Use Grid' : 'Use Checkerboard' }}
                    </v-btn>
                    <div class="mt-3">
                      <div class="text-caption mb-2">
                        Transparency: {{ Math.round((1 - groundOpacity) * 100) }}%
                      </div>
                      <v-slider 
                        :value="(1 - groundOpacity) * 100"
                        @input="value => updateGroundOpacity(1 - value / 100)"
                        :min="0" 
                        :max="100" 
                        step="1" 
                        hide-details 
                        :disabled="!showGround"
                        dense
                        class="mt-0"
                      ></v-slider>
                    </div>
                  </div>
                </v-card>
              </v-menu>
            </div>
            
            <!-- Axes setting -->
            <div class="d-flex align-center mb-3">
              <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Axes:</div>
              <v-btn icon small @click="toggleAxes" title="Toggle Axes Visibility">
                <v-icon small :color="showAxes ? 'white' : 'grey'">{{ showAxes ? 'mdi-axis-arrow' : 'mdi-axis-arrow-lock' }}</v-icon>
              </v-btn>
            </div>
            
            <!-- Camera setting -->
            <div class="d-flex align-center">
              <div class="mr-2 text-caption" style="width: 80px; flex-shrink: 0;">Camera:</div>
              <v-btn icon small @click="toggleCameraControls" title="Toggle Camera Controls Visibility">
                <v-icon small :color="showCameraControls ? 'white' : 'grey'">{{ 'mdi-cube-scan' }}</v-icon>
              </v-btn>
            </div>
          </div>
        </div>

      <div class="mt-6"></div> <!-- Added vertical spacing -->

        <!-- Timelapse Controls -->
      <div class="timelapse-section mb-4 pa-3" style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
        <div class="section-title mb-3" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">Timelapse Mode</div>
        
        <!-- Timelapse toggle with settings button -->
        <div class="d-flex align-center mb-3">
          <v-switch
            v-model="timelapseMode"
            color="indigo"
            @change="toggleTimelapseMode"
            class="mr-auto mb-0 mt-0 pt-0"
            hide-details
            style="flex: 1;"
          ></v-switch>
          
          <v-btn 
            small
            outlined
            color="white"
            class="ml-2 settings-text-btn"
            @click="openTimelapseSettings($event)"
            :disabled="!timelapseMode"
          >
            Settings
          </v-btn>
            </div>
        
        <!-- Timelapse settings summary -->
        <div v-if="timelapseMode" class="d-flex align-center recording-summary">
          <div class="text-caption text-center" style="flex: 1;">
            <span class="font-weight-bold">Interval:</span> {{ timelapseInterval }} frames
          </div>
          <div class="text-caption text-center" style="flex: 1;">
            <span class="font-weight-bold">Opacity:</span> {{ Math.round(timelapseOpacity * 100) }}%
          </div>
        </div>
        
        <!-- Quick action buttons when timelapse mode is enabled -->
        <div v-if="timelapseMode" class="d-flex justify-space-between align-center mt-2">
          <v-btn small text @click="clearTimelapse" class="mt-1">
            Clear All
          </v-btn>
          <v-btn small text @click="showTimelapseManager = true" class="mt-1">
            Manage Models
          </v-btn>
        </div>
      </div>
      
      <!-- Timelapse Settings Dialog -->
      <v-dialog
        v-model="showTimelapseSettings"
        max-width="500"
      >
        <v-card class="recording-settings-dialog">
          <v-card-title>Timelapse Settings</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <div class="text-subtitle-2 mb-2">Frame Interval</div>
            <v-slider
              v-model="timelapseInterval"
              min="1"
              max="30"
              step="1"
              thumb-label
              thumb-size="24"
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
              </v-col>

              <v-col cols="12">
                <div class="text-subtitle-2 mb-2">Model Transparency</div>
            <v-slider
              :value="timelapseOpacity * 100"
              @input="value => timelapseOpacity = value / 100"
              min="0"
              max="100"
              step="1"
              thumb-label
              thumb-size="24"
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
              </v-col>
              
              <v-col cols="12">
                <div class="info-box pa-3 mt-2">
                  <div class="d-flex align-center mb-2">
                    <v-icon small color="info" class="mr-2">mdi-information-outline</v-icon>
                    <span class="subtitle-2">Timelapse Tips</span>
            </div>
                  <ul class="pl-4 mb-0 text-caption">
                    <li class="mb-1">Frame Interval determines how often timelapse captures are taken</li>
                    <li class="mb-1">Lower opacity values help distinguish between different timelapse frames</li>
                    <li>Use the Manage Models button to selectively delete timelapse frames</li>
                  </ul>
          </div>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" text @click="showTimelapseSettings = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

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
  
// Create a new axios instance without a base URL
const axiosInstance = axios.create();
  
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
  
  export default {
      name: 'Session',
      components: {
          VideoNavigation,
          SpeedControl,
          CameraControls // Register component
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
          showRecordingSettings: false, // Controls recording settings dialog
          showCaptureSettings: false, // Controls image capture settings dialog
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
              useGroundTexture: true,
              groundMesh: null,
              groundTexture: null,
              useCheckerboard: true,
              gridTexture: null,
              showGround: true,
              alphaValues: [], // Array to store alpha values for each animation
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
            showTimelapseSettings: false, // Controls timelapse settings dialog
              timelapseGroups: {}, // Organized by animation index and frame numbers
              timelapseCounter: null, // Use sequential counter for mesh IDs
              captureMode: 'both', // Options: 'both', 'normal', 'transparent'
              videoBitrate: 5000000, // Video recording bitrate in bits per second (5 Mbps default)
              conversionError: null, // Add this line to store API error message

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

              displayColors: [], // For v-color-picker visual representation
              showLoadObjectDialog: false, // Add this line to control the load object dialog
              objFile: null,
              objPosition: { x: 0, y: 0, z: 0 },
              objScale: 1,
              objColor: '#ffffff',
              customObjects: [], // Track loaded custom objects
              showCustomObjectsManager: false, // Dialog to manage custom objects
              showLeftSidebar: true, // Add this line to control left sidebar visibility
              showImportDialog: false, // Add this line to control the import dialog

              showAxes: false, // Add this line to control axes visibility
              axesGroup: null, // Add this line to store the axes group
              showCameraControls: false, // Add this line to control camera controls visibility
              animationDurationInSeconds: 0, // Duration for headless recording
              // Share functionality
              showShareDialog: false,
              shareUrl: '',
              shareUrlSize: 0,
              shareMethod: 0, // 0 for URL, 1 for file
              shareFileName: 'visualization-share',
              shareSettings: {
                  includeCamera: false, // Changed to false for smaller URLs
                  includeColors: false, // Changed to false for smaller URLs
                  includeSettings: false, // Removed entirely from getShareData
                  includeCurrentFrame: false
              },
              generatingShareUrl: false,
              loadingInitialShare: false,
              // Debounce timers for offset updates
              offsetUpdateTimers: {},
              objectUpdateTimers: {},
              
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
              // Forces visualization properties
              showForcesDialog: false,
              forcesFile: null,
              forcesDatasets: {}, // Object to store multiple force datasets by animation index
              forceArrows: [], // Array to store force arrow objects
              showForces: true,
              forceScale: 0.001, // Scale factor for force arrows
                    forceColors: {}, // Object to store colors per animation index
      forceDisplayColors: {}, // Object to store display colors for v-color-picker by animation index
              loadingForces: false,
              selectedAnimationForForces: 0,
              // Sample selection dialog
              showSampleSelectionDialog: false,
              availableSampleSets: [
                { id: 'STS', name: 'Sit-to-Stand', description: 'Sit-to-stand on chair' },
                { id: 'squat', name: 'Squats', description: 'Squat exercise movements' },
                { id: 'walk', name: 'Walking', description: 'Normal walking' },
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
        videoControlsDisabled() {
          return (!this.trial && this.markerSpheres.length === 0) || this.frames.length === 0
        },
        formattedTime() {
          // Round time to 2 decimal places for display
          return parseFloat(this.time).toFixed(2);
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
        console.log('🔧 Debug functions available: window.setBackgroundWhite(), window.setBackgroundBlack(), window.clearSettings(), window.toggleFog()');
        
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
        this.$nextTick(() => {
        this.initScene(); // initScene will now call applyLoadedSceneSettings
        });

        // Check for shared visualization first
        if (this.$route.query.share || this.$route.query.shareId) {
            console.log('Found shared visualization in URL');
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
            }
        }

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


    // Forces visualization methods
    openForcesDialog() {
      this.showForcesDialog = true;
    },

    
    // Get current force values for display in the sidebar
    getCurrentForceValues(animationIndex) {
      if (!this.forcesDatasets[animationIndex] || !this.frames || this.frame >= this.frames.length) {
        return null;
      }
      
      const forcesData = this.forcesDatasets[animationIndex];
      const currentTime = parseFloat(this.frames[this.frame]);
      
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
      
      // Extract force values for the current frame
      const result = {};
      
      // Check for right foot forces
      if (forcesData.data.R_ground_force_vx && forcesData.data.R_ground_force_vy && forcesData.data.R_ground_force_vz) {
        const fx = forcesData.data.R_ground_force_vx[closestIndex] || 0;
        const fy = forcesData.data.R_ground_force_vy[closestIndex] || 0;
        const fz = forcesData.data.R_ground_force_vz[closestIndex] || 0;
        const magnitude = Math.sqrt(fx * fx + fy * fy + fz * fz);
        
        result.R = { fx, fy, fz, magnitude };
      }
      
      // Check for left foot forces
      if (forcesData.data.L_ground_force_vx && forcesData.data.L_ground_force_vy && forcesData.data.L_ground_force_vz) {
        const fx = forcesData.data.L_ground_force_vx[closestIndex] || 0;
        const fy = forcesData.data.L_ground_force_vy[closestIndex] || 0;
        const fz = forcesData.data.L_ground_force_vz[closestIndex] || 0;
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
          
          // Check for force-related column names
          const forceKeywords = [
            'force', 'ground_force', 'grf',
            'force_vx', 'force_vy', 'force_vz',
            'force_px', 'force_py', 'force_pz',
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
        this.$toasted.warning('Please load an animation first before importing forces');
        return;
      }
      
      // Initialize force visibility state for this animation if not set
      if (typeof this.forcesVisible === 'undefined') {
        this.forcesVisible = {};
      }
      
      // Find the first animation without forces, starting from the most recently added
      let targetAnimationIndex = this.animations.length - 1; // Start with newest animation
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
      
      // Store forces data for the selected animation
      const animationIndex = this.selectedAnimationForForces;
      this.forcesDatasets[animationIndex] = {
        time: timeData,
        columns: columnHeaders,
        data: forceData,
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
      
      this.createForceArrows();
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
          
          // Check if force columns exist in the data
          const hasForceData = mapping.forceColumns.some(col => forcesData.data[col]);
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
      
      const currentTime = this.frames[frameIndex];
      console.log('updateForceArrows called for frame:', frameIndex, 'time:', currentTime);
      
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
        
        // Debug logging for COP positioning
        if (frameIndex === 0 || frameIndex % 30 === 0) {
          console.log(`COP debug - Animation ${animationIndex}:`, {
            copPosition: copPosition.toArray(),
            hasCopData,
            animationOffset: animation.offset
          });
        }
        
        // Update each force arrow in the group
        footForceGroup.children.forEach(arrowGroup => {
          const arrowData = arrowGroup.userData;
          if (!arrowData || !arrowData.forceColumns) return;
          
          // Calculate resultant force vector
          const forceVector = new THREE.Vector3(0, 0, 0);
          const forceColumns = arrowData.forceColumns;
          
          if (forceColumns.length >= 3) {
            const fx = forcesData.data[forceColumns[0]] ? 
                     forcesData.data[forceColumns[0]][forceFrameIndex] || 0 : 0;
            const fy = forcesData.data[forceColumns[1]] ? 
                     forcesData.data[forceColumns[1]][forceFrameIndex] || 0 : 0;
            const fz = forcesData.data[forceColumns[2]] ? 
                     forcesData.data[forceColumns[2]][forceFrameIndex] || 0 : 0;
            
            forceVector.set(fx, fy, fz);
          }
          
          // Calculate original force magnitude before scaling
          const originalMagnitude = forceVector.length();
          
          // Debug logging
          if (frameIndex === 0 || frameIndex % 30 === 0) { // Log every 30 frames to avoid spam
            console.log(`Force debug - Animation ${animationIndex}, Platform ${arrowData.platform}:`, {
              fx: forcesData.data[forceColumns[0]] ? forcesData.data[forceColumns[0]][forceFrameIndex] : 'missing',
              fy: forcesData.data[forceColumns[1]] ? forcesData.data[forceColumns[1]][forceFrameIndex] : 'missing', 
              fz: forcesData.data[forceColumns[2]] ? forcesData.data[forceColumns[2]][forceFrameIndex] : 'missing',
              magnitude: originalMagnitude,
              frameIndex: forceFrameIndex
            });
          }
          
          // Update arrow visibility based on original force magnitude (lowered threshold for debugging)
          arrowGroup.visible = originalMagnitude > 0.1; // Show if force > 0.1N (was 1.0N)
          
          if (frameIndex === 0 || frameIndex % 30 === 0) {
            console.log(`Arrow visibility - Animation ${animationIndex}, Platform ${arrowData.platform}: visible=${arrowGroup.visible}, magnitude=${originalMagnitude}`);
          }
          
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
      const targetAnimationIndex = this.selectedAnimationForMarkers || 0;
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
       const lines = content.trim().split('\n');
       
       // Parse header information
       const header = {};
       let dataStartIndex = 0;
       
       // Find the header end and data start
       for (let i = 0; i < lines.length; i++) {
         const line = lines[i].trim();
         if (line.includes('DataRate') || line.includes('CameraRate') || line.includes('NumFrames') || line.includes('NumMarkers') || line.includes('Units')) {
           const parts = line.split('\t');
           if (parts.length >= 2) {
             header[parts[0]] = parts[1];
           }
         }
         
         // Check for column headers line (contains Frame# and Time)
         if (line.includes('Frame#') && line.includes('Time')) {
           // Skip the coordinate labels line and find the actual data start
           for (let j = i + 1; j < lines.length; j++) {
             const dataLine = lines[j].trim();
             if (/^\d+\s/.test(dataLine)) {  // Line starts with a number
               dataStartIndex = j;
               break;
             }
           }
           break;
         }
       }
       
       // Parse column headers - find the marker names line (should contain Frame# and Time)
       let markerNamesLineIndex = -1;
       for (let i = 0; i < dataStartIndex; i++) {
         if (lines[i].includes('Frame#') && lines[i].includes('Time')) {
           markerNamesLineIndex = i;
           break;
         }
       }
       
       const headerLine = lines[markerNamesLineIndex];
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
           

           
           // Convert from mm to meters (TRC files are typically in mm)
           markerData[markerName].x.push(x / 1000);
           markerData[markerName].y.push(y / 1000);
           markerData[markerName].z.push(z / 1000);
           
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
       
       // Handle case where no animations exist - create a standalone marker visualization
       let animationIndex = this.selectedAnimationForMarkers;
       
       if (this.animations.length === 0 || animationIndex === null) {
         // For standalone marker files, set up the frames for animation control
         this.frames = timeData;
         this.frame = 0;
         this.time = (timeData[0] || 0).toFixed(2);
         
         // Calculate frame rate for marker data
         this.frameRate = this.calculateFrameRate(timeData);
         
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
       if (!this.scene) {
         console.log('Initializing scene for standalone markers...');
         // Wait for DOM to be ready before initializing scene
         this.$nextTick(() => {
         this.initScene();
           // Create marker spheres after scene is initialized
           this.createMarkerSpheres();
           this.handlePostMarkerCreation();
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
       if (!this.scene) {
         console.error('Scene not initialized when creating marker spheres');
         throw new Error('Scene not initialized');
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
         sphere.material.color.setHex(this.markerColor.replace('#', '0x'));
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
      this.loadSampleFiles(sampleSetId);
    },
    
    getSampleIcon(sampleSetId) {
      const iconMap = {
        'STS': 'mdi-chair-rolling',
        'squat': 'mdi-human-handsdown', 
        'walk': 'mdi-walk',
        'rmasb': 'mdi-run-fast'
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
          const shareId = this.generateShareId();
          await this.storeShareData(shareId, shareData);
          this.shareUrl = `${baseUrl}?shareId=${shareId}`;
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
        // Try cloud storage first
        const response = await fetch('https://opencap-share-backend.onrender.com/api/share', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ shareId, data })
        });

        if (response.ok) {
          console.log(`Stored share data in cloud with ID: ${shareId}`);
          return;
        }
        
        // Fallback to localStorage if cloud fails
        console.warn('Cloud storage failed, falling back to localStorage');
        const shareKey = `opencap_share_${shareId}`;
        localStorage.setItem(shareKey, JSON.stringify(data));
        console.log(`Stored share data locally with ID: ${shareId}`);
        
      } catch (error) {
        console.error('Error storing share data:', error);
        // Final fallback to localStorage
        try {
          const shareKey = `opencap_share_${shareId}`;
          localStorage.setItem(shareKey, JSON.stringify(data));
          console.log(`Fallback: Stored share data locally with ID: ${shareId}`);
        } catch (localError) {
          throw new Error('Failed to store share data');
        }
      }
    },

    async loadShareData(shareId) {
      try {
        // Try cloud storage first
        const response = await fetch(`https://opencap-share-backend.onrender.com/api/share/${shareId}`);
        
        if (response.ok) {
          const result = await response.json();
          console.log(`Loaded share data from cloud with ID: ${shareId}`);
          return result.data;
        }
        
        // Fallback to localStorage if cloud fails or data not found
        console.warn('Cloud data not found, trying localStorage');
        const shareKey = `opencap_share_${shareId}`;
        const storedData = localStorage.getItem(shareKey);
        if (!storedData) {
          throw new Error('Share data not found');
        }
        console.log(`Loaded share data from localStorage with ID: ${shareId}`);
        return JSON.parse(storedData);
        
      } catch (error) {
        console.error('Error loading share data:', error);
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
          offset: [anim.offset.x, anim.offset.y, anim.offset.z] // Use array instead of object
        }))
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
            calculatedFps: this.calculateFrameRate(decompressedData.time),
            visible: true, // Default to visible
            playable: true // Default to playable
          });
          
          this.initializeAlphaValue(i);
          // Ensure all color arrays are synchronized when adding new animations
          this.ensureColorArraysSync();
        }
        
        // Set frames from first animation
        if (this.animations.length > 0) {
          this.frames = this.animations[0].data.time;
          this.frameRate = this.animations[0].calculatedFps;
          console.log(`[loadSharedVisualization] Frames setup - Total frames: ${this.frames.length}, Frame rate: ${this.frameRate}, Current frame: ${this.frame}`);
          console.log(`[loadSharedVisualization] First few frames:`, this.frames.slice(0, 5));
          console.log(`[loadSharedVisualization] Last few frames:`, this.frames.slice(-5));
        }
        
        // Apply shared settings
        if (shareData.settings) {
          const settings = shareData.settings;
          this.backgroundColor = settings.backgroundColor || this.backgroundColor;
          this.groundColor = settings.groundColor || this.groundColor;
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
          this.frame = shareData.currentFrame;
          // Update time to match the frame
          if (this.frames && this.frames[this.frame] !== undefined) {
            this.time = parseFloat(this.frames[this.frame]).toFixed(2);
          } else if (this.frameRate) {
            this.time = parseFloat(this.frame / this.frameRate).toFixed(2);
          }
        }
        
        // Initialize the 3D scene
        await this.$nextTick();
        this.initScene();
        
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
              if (this.frames && this.frames[this.frame] !== undefined) {
                this.time = parseFloat(this.frames[this.frame]).toFixed(2);
              } else if (this.frameRate) {
                this.time = parseFloat(this.frame / this.frameRate).toFixed(2);
              }
            }
            
            // All models loaded, now animate to current frame
            setTimeout(() => {
              this.animateOneFrame();
              console.log(`[loadSharedVisualization] Initial frame animation complete. Try using play controls or navigating frames.`);
            }, 100);
          }
        };
        
        // If no models to load, animate immediately
        if (totalModelsToLoad === 0) {
          // Update time to match the current frame 
          if (shareData.currentFrame !== undefined) {
            if (this.frames && this.frames[this.frame] !== undefined) {
              this.time = parseFloat(this.frames[this.frame]).toFixed(2);
            } else if (this.frameRate) {
              this.time = parseFloat(this.frame / this.frameRate).toFixed(2);
            }
          }
          
          setTimeout(() => {
            this.animateOneFrame();
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
        
      } catch (error) {
        console.error('Error loading shared visualization:', error);
        this.$toasted.error('Failed to load shared visualization');
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
        // Always schedule the next frame first
        requestAnimationFrame(this.animate);

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
        const deltaTime = (currentTime - this.lastFrameTime) / 1000; // Convert to seconds

        // Check if we have markers or animations to animate
        // Refined check for clarity: Checks if any animation is playable OR if markers exist
        const hasAnimatedContent = this.animations.some(a => a.playable !== false) || 
                                 (this.markerSpheres.length > 0) ||
                                 (Object.keys(this.markersDatasets).length > 0);
        
        // Note: Debug removed - animation loop should now work for shared visualizations

        // Only advance frames if playing, enough time passed, and content exists
        if (deltaTime >= (1 / this.frameRate) && hasAnimatedContent) {
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
                        // Stop playing state is handled by stopRecording
                        return; // Exit this specific animate cycle
                    }
                } else if (nextFrame >= this.frames.length) {
                    // If not recording OR loopCount is Infinite, check playback looping
                    if (this.isLooping) {
                      // Loop back normally using modulo
                      nextFrame = nextFrame % this.frames.length;
                    
                    // When looping, also reset video to beginning if present
                    if (this.videoFile && this.$refs.videoPreview) {
                      try {
                        console.log('[animate] Looping animation, resetting video to beginning');
                        this.$refs.videoPreview.currentTime = 0;
                        
                        // Ensure video keeps playing if it was previously playing
                        if (this.playing && this.$refs.videoPreview.paused) {
                          const playPromise = this.$refs.videoPreview.play();
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

                // Update lastFrameTime (using current time is simpler and often sufficient)
                this.lastFrameTime = currentTime;

                // Update displayed time
                if (this.frames[this.frame] !== undefined) {
                    this.time = parseFloat(this.frames[this.frame]).toFixed(2);
                } else {
                    // Fallback if frames array doesn't have time for this index (should not happen with proper sync)
                    this.time = parseFloat(this.frame / this.frameRate).toFixed(2);
                }
                
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
            }
        } 
        // Render even if not enough time has passed to advance the frame, but still playing
        // This ensures smoother rendering, especially at high frame rates or low play speeds
        else if (this.playing) { 
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
            for (let body in json.bodies) {
              json.bodies[body].attachedGeometries.forEach((geom) => {
                const meshKey = `anim${animIndex}_${body}${geom}`;
                if (this.meshes[meshKey]) {
                  // Check if translation data exists for this frame
                  if (!json.bodies[body].translation || !json.bodies[body].translation[cframe]) {
                    console.error(`[animateOneFrame] Missing translation data for body ${body} frame ${cframe}`);
                    return; // Skip this geometry
                  }
                  
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
                  
                  // Check if rotation data exists for this frame
                  if (!json.bodies[body].rotation || !json.bodies[body].rotation[cframe]) {
                    console.error(`[animateOneFrame] Missing rotation data for body ${body} frame ${cframe}`);
                    return; // Skip this geometry
                  }
                  
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
  
          // Render the scene (moved before marker update)
          if (this.renderer && this.scene && this.camera) {
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
            this.renderer.render(this.scene, this.camera);
          }
        } else {
            // If frame is out of bounds, still render the scene
            if (this.renderer && this.scene && this.camera) {
              this.renderer.render(this.scene, this.camera);
            }
        }
        
        // Update real-time plot if enabled
        if (this.showPlottingDialog && this.plotUpdatesEnabled) {
          this.updatePlotInRealTime();
        }
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
          // Reset timing references when starting playback
          this.lastFrameTime = performance.now();
          // Make sure first frame gets displayed immediately if starting from pause
          this.animateOneFrame(); 
        } 
        // No specific 'else' action needed here for pause, the animate loop handles it.

        // Video sync logic
        if (this.videoFile && this.$refs.videoPreview) {
          try {
            if (this.playing) {
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
            window.parent.postMessage({ type: 'playbackState', isPlaying: this.playing }, '*');
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
          // Temporarily remove the timeupdate listener to prevent feedback loops
          const videoElement = this.$refs.videoPreview;
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
      } else if (checkMimeType('video/mp4')) {
        mimeType = 'video/mp4';
      } else {
        // Fallback to WebM if MP4 isn't supported
        console.warn('MP4 format not supported by browser, falling back to WebM');
        this.recordingFormat = 'webm';
        mimeType = supportedMimeTypes.find(checkMimeType) || 'video/webm';
      }
        fileExtension = '.mp4';
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
      console.warn(`Failed to create MediaRecorder with ${mimeType}, trying with default settings`, error);
      
      // Last resort - let the browser decide the format
      try {
        this.mediaRecorder = new MediaRecorder(stream);
        console.log('MediaRecorder created with default settings');
      } catch (fallbackError) {
        console.error('Failed to create MediaRecorder', fallbackError);
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
      
    // Start recording with timeslices to ensure data is captured in smaller chunks
    // This helps with memory usage and ensures more consistent recording
    this.mediaRecorder.start(1000); // Capture in 1-second intervals
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
            this.$nextTick(() => {
                this.initScene();
            });
        }

        // Get the current number of animations for offset calculation
        const startIndex = this.animations.length;

        // Create a Promise for each file
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

        // Process all files together
        Promise.allSettled(filePromises).then(results => {
            // Filter successful results
            const successfulResults = results
                .filter(result => result.status === 'fulfilled')
                .map(result => result.value);
            
            // Log any errors
            const errors = results.filter(result => result.status === 'rejected');
            errors.forEach(error => {
                console.error('Error loading file:', error.reason);
                this.$toasted.error(`Error loading file: ${error.reason.file.name}`);
            });
            
            if (successfulResults.length === 0) {
                this.$toasted.error('No valid files could be loaded');
                return;
            }
            // Check if any file is a share file
            const shareFiles = successfulResults.filter(({ data }) => 
                data && data.animations && Array.isArray(data.animations)
            );
            
            if (shareFiles.length > 0) {
                // Load as shared visualization
                const shareData = shareFiles[0].data;
                this.loadSharedVisualization(shareData);
                this.$toasted.success('Share file loaded successfully!');
                return;
            }
            
            successfulResults.forEach(({ data, file }, index) => {
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
                    playable: true, // Add playable property, default to true
                    calculatedFps: fileFps // Store calculated FPS
                });

                if (this.animations.length === 1) {
                    this.frames = data.time;
                    this.trial = { results: [] };
                    // Set the global frameRate based on the first file loaded
                    this.frameRate = fileFps;
                    // Reset frame counter to 0 and set initial time
                    this.frame = 0;
                    this.time = data.time && data.time.length > 0 ? parseFloat(data.time[0]).toFixed(2) : "0.00";
                }

                // Initialize the alpha value for the new animation
                this.initializeAlphaValue(startIndex + index);
                
                // Extract marker data from JSON file for plotting
                this.extractMarkerDataFromJson(data, startIndex + index, file.name);
            });

            // Ensure all color arrays are synchronized after adding new animations
            this.ensureColorArraysSync();

            // Keep track of loaded geometries
            let geometriesLoaded = 0;
            const totalGeometries = successfulResults.reduce((total, { data }) => {
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

                                    // Calculate animation duration for headless operation
                                    if (this.frames && this.frames.length > 0 && this.frameRate > 0) {
                                        this.animationDurationInSeconds = (this.frames.length - 1) / this.frameRate;
                                    }

                                    // Start animation loop and render first frame
                                    this.animate();
                                    this.frame = 0;
                                    this.animateOneFrame();
                                    // Start playing automatically
                                    this.togglePlay(true);
                                    
                                    // Signal that all visuals are loaded for headless operation
                                    window.allVisualsLoaded = true;
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
        console.log('initScene called');
        const container = this.$refs.mocap;
        if (!container) {
          console.error('Container not found in initScene');
          console.log('Available refs:', Object.keys(this.$refs));
          console.log('DOM ready?', document.readyState);
          console.log('Trial:', !!this.trial);
          console.log('Animations:', this.animations.length);
          console.log('MarkerSpheres:', this.markerSpheres.length);
          console.log('TrialLoading:', this.trialLoading);
          console.log('Converting:', this.converting);
          
          // Try again in the next tick if we're in a loading state
          if (this.trialLoading || this.converting || this.animations.length > 0) {
            console.log('Retrying initScene in next tick...');
            this.$nextTick(() => {
              this.initScene();
            });
          }
          return;
        }

        let ratio = container.clientWidth / container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(35, ratio, 0.1, 125);
        this.camera.position.x = 3.33;
        this.camera.position.z = -2.30;
        this.camera.position.y = 3.5;

        this.scene = new THREE.Scene();
        console.log('Scene and camera initialized');

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
        console.log(`[initScene] Setting background color to: ${this.backgroundColor}`);
        this.scene.background = new THREE.Color(this.backgroundColor);
        
        // Configure renderer with current background color and better shadows
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.setClearColor(this.backgroundColor);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        this.onResize();
        container.appendChild(this.renderer.domElement);
        this.controls = new THREE_OC.OrbitControls(this.camera, this.renderer.domElement);

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
        const planeMat = new THREE.MeshPhongMaterial({
            map: this.useGroundTexture ? texture : null,
            side: THREE.DoubleSide,
            color: new THREE.Color(this.groundColor),
            opacity: this.groundOpacity,
            transparent: this.groundOpacity < 1.0
        });
        const groundMesh = new THREE.Mesh(planeGeo, planeMat);
        groundMesh.rotation.x = Math.PI * -.5;
        groundMesh.position.y = 0;
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

        // Main directional light with softer intensity
        const lightIntensity = 0.5;
        const lightColor = 0xFFFFFF;
        const directionalLight = new THREE.DirectionalLight(lightColor, lightIntensity);
        directionalLight.position.set(-10, 10, -10);
        directionalLight.target.position.set(0, 0, 0);
        this.scene.add(directionalLight);
        this.scene.add(directionalLight.target);
        this.lights.directionals = [directionalLight];

        // Add spotlight to create the gradient lighting effect around subjects
        const spotLight = new THREE.SpotLight(0xffffff, 1); // Increased intensity from 1 to 1.2
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

        // Create an ambient light with higher intensity for better marker visibility
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        this.lights.ambient = ambientLight;

        // Initial render
        this.renderer.render(this.scene, this.camera);

        // Apply loaded settings after scene initialization
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
      
      // Separate files by type
      const jsonFiles = files.filter(file => file.name.toLowerCase().endsWith('.json'));
      const trcFiles = files.filter(file => file.name.toLowerCase().endsWith('.trc'));
      const osimFiles = files.filter(file => file.name.toLowerCase().endsWith('.osim'));
      const motFiles = files.filter(file => file.name.toLowerCase().endsWith('.mot'));
      const videoFiles = files.filter(file => file.type === 'video/mp4' || file.type === 'video/webm');
      
      // Categorize .mot files as either motion or force files
      const { motionFiles, forceFiles } = await this.categorizeMotFiles(motFiles);
      
      console.log('Categorized files:', {
        json: jsonFiles.length,
        trc: trcFiles.length,
        osim: osimFiles.length,
        motion: motionFiles.length,
        force: forceFiles.length,
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
      
      // Show completion message
      if (files.length > 0) {
        this.$toasted.success(`Processed ${files.length} files successfully`);
      }
      
      // Initialize scene if needed
      if (!this.scene && (jsonFiles.length > 0 || trcFiles.length > 0 || (osimFiles.length > 0 && motionFiles.length > 0))) {
        this.$nextTick(() => {
        this.initScene();
        });
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

        // Rebuild meshes and text sprites with correct indices
        this.reindexSubjects();

        if (this.animations.length > 0) {
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

        // Save settings after deletion
        this.saveSettings();
    },
    reindexSubjects() {
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
                
                // Find the new index for this mesh
                let newIndex = -1;
                for (let i = 0; i < this.animations.length; i++) {
                    if (i >= oldIndex) {
                        newIndex = i;
                        break;
                    }
                }
                
                if (newIndex !== -1) {
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
                
                // Find the new index for this text sprite
                let newIndex = -1;
                for (let i = 0; i < this.animations.length; i++) {
                    if (i >= oldIndex) {
                        newIndex = i;
                        break;
                    }
                }
                
                if (newIndex !== -1) {
                    const newKey = `text_${newIndex}`;
                    this.textSprites[newKey] = oldTextSprites[key];
                    
                    // Update text sprite content and color
                    this.updateTextSpriteColor(newIndex, this.formatColor(this.colors[newIndex]));
                }
            }
        });
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
                    playable: true, // Add playable property, default to true
                    calculatedFps: fileFps // Store calculated FPS
                });
                
                // Extract marker data from sample JSON file for plotting
                this.extractMarkerDataFromJson(data, this.animations.length - 1, fileName);
                
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
            // If not using texture, just set the color
            if (!this.useGroundTexture) {
                this.groundMesh.material.color = new THREE.Color(color);
                this.groundMesh.material.opacity = this.groundOpacity;
                this.groundMesh.material.transparent = this.groundOpacity < 1.0;
            } else {
                // If using texture, create a new material with both texture and color
                const oldMaterial = this.groundMesh.material;
                const newMaterial = new THREE.MeshPhongMaterial({
                    map: this.groundTexture,
                    side: THREE.DoubleSide,
                    color: new THREE.Color(color),
                    opacity: this.groundOpacity,
                    transparent: this.groundOpacity < 1.0
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
            this.groundMesh.material.opacity = opacity;
            this.groundMesh.material.transparent = opacity < 1.0;
            
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
                    color: new THREE.Color(this.groundColor),
                    opacity: this.groundOpacity,
                    transparent: this.groundOpacity < 1.0
                });
            } else {
                // Use plain colored material
                this.groundMesh.material = new THREE.MeshPhongMaterial({
                    color: new THREE.Color(this.groundColor),
                    side: THREE.DoubleSide,
                    opacity: this.groundOpacity,
                    transparent: this.groundOpacity < 1.0
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
                color: new THREE.Color(this.groundColor),
                opacity: this.groundOpacity,
                transparent: this.groundOpacity < 1.0
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
            
            // Give time for scene initialization before clearing converting flag
            await new Promise(resolve => setTimeout(resolve, 100));
            
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
          this.$refs.videoPreview.currentTime = videoTimePosition;
        }
      }
    },
  
  handleVideoTimeUpdate() {
    // Only sync if playing and not during a scrubbing operation
    if (this.playing && this.$refs.videoPreview && this.frames.length > 0) {
      // Get current video time
      const videoTime = this.$refs.videoPreview.currentTime;
      
      // Calculate what frame we should be on based on video time
      const frameProgress = videoTime / this.videoDuration;
      const totalFrames = this.frames.length - 1;
      const targetFrame = Math.round(frameProgress * totalFrames);
      
      // If we're more than 1 frame off, sync the animation
      if (Math.abs(targetFrame - this.frame) > 1) {
        console.log(`Video sync: Adjusting animation from frame ${this.frame} to ${targetFrame}`);
        // Update frame without calling onNavigate to avoid recursive sync
        this.frame = targetFrame;
        
        // Update displayed time
        if (this.frames[targetFrame] !== undefined) {
          this.time = parseFloat(this.frames[targetFrame]).toFixed(2);
        }
        
        // Render the updated frame
        this.animateOneFrame();
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
          if (settings.groundOpacity !== undefined) this.groundOpacity = settings.groundOpacity;
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
          // Force timelapseMode to false by default
          this.timelapseMode = false;
          if (settings.timelapseInterval) this.timelapseInterval = settings.timelapseInterval;
          if (settings.timelapseOpacity !== undefined) this.timelapseOpacity = settings.timelapseOpacity;
        if (settings.showTimelapseSettings !== undefined) this.showTimelapseSettings = settings.showTimelapseSettings;
          if (settings.recentSubjectColors) this.recentSubjectColors = settings.recentSubjectColors;
          if (settings.showCameraControls !== undefined) this.showCameraControls = settings.showCameraControls;

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
        timelapseMode: this.timelapseMode,
        timelapseInterval: this.timelapseInterval,
        timelapseOpacity: this.timelapseOpacity,
      showTimelapseSettings: this.showTimelapseSettings,
        recentSubjectColors: this.recentSubjectColors, // Save recent colors
        showCameraControls: this.showCameraControls, // Save camera controls visibility
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
                  color: new THREE.Color(this.groundColor),
                  opacity: this.groundOpacity,
                  transparent: this.groundOpacity < 1.0
                            });
                        } else {
              this.groundMesh.material = new THREE.MeshPhongMaterial({
                  color: new THREE.Color(this.groundColor),
                  side: THREE.DoubleSide,
                  opacity: this.groundOpacity,
                  transparent: this.groundOpacity < 1.0
              });
          }
          if (oldMaterial && oldMaterial !== this.groundMesh.material) {
            oldMaterial.dispose();
          }
                    } else {
          console.warn('[applyLoadedSceneSettings] Ground mesh not ready when applying settings.');
          console.warn('[applyLoadedSceneSettings] Ground mesh not ready.');
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
        this.handleFileUpload(fakeEvent);
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
  width: 330px;
  max-height: calc(100vh - 80px); /* Set max height to match height */
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
  height: calc(100vh - 80px); /* Adjust height to leave space at bottom */
  overflow-y: auto;
}

.left.hidden {
  transform: translateX(-110%);
  opacity: 0;
  pointer-events: none;
}

.right {
  right: 10px;
  height: calc(100vh - 80px); /* Match left sidebar height */
  overflow-y: auto;
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

.plotting-header {
  border-top-left-radius: 12px !important;
  border-top-right-radius: 12px !important;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
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

.resize-handle {
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.resize-handle:hover {
  opacity: 1;
}

/* ... rest of existing styles ... */
</style>
  
                