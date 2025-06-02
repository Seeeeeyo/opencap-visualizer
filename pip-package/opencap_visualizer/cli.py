#!/usr/bin/env python3
"""
OpenCap Visualizer CLI - Generate videos from biomechanics JSON files
"""

import argparse
import asyncio
import os
import sys
import tempfile
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
DEFAULT_OUTPUT_FILENAME = "animation_video.mp4"
DEFAULT_VIEWPORT_SIZE = {"width": 1920, "height": 1080}
DEFAULT_FRAME_RATE = 30
DEFAULT_TIMEOUT = 120000  # 2 minutes in milliseconds

class VisualizerCLI:
    def __init__(self):
        self.browser = None
        self.page = None
        self.verbose = False # Will be set based on quiet_mode
    
    def _log(self, message):
        """Helper to log messages only if not in quiet mode (i.e., verbose is True)."""
        if self.verbose:
            print(message)
    
    def _process_subject_colors(self, color_input: list, num_subjects: int) -> list:
        """Process and validate subject colors, returning hex color strings."""
        
        # Color name to hex mapping (matching Session.vue's availableColors)
        color_names = {
            'red': '#ff0000',
            'green': '#00ff00', 
            'blue': '#0000ff',
            'yellow': '#ffff00',
            'magenta': '#ff00ff',
            'cyan': '#00ffff',
            'orange': '#ff8000',
            'purple': '#8000ff',
            'white': '#ffffff',
            'gray': '#808080',
            'grey': '#808080',
            'lightred': '#ff8080',
            'lightgreen': '#80ff80',
            'lightblue': '#8080ff',
            'lightpink': '#ff80ff',
            'lightcyan': '#80ffff',
            'lightorange': '#ffa040'
        }
        
        processed_colors = []
        
        for color in color_input:
            # Convert to lowercase for name matching
            color_lower = color.lower()
            
            # Check if it's a predefined color name
            if color_lower in color_names:
                processed_colors.append(color_names[color_lower])
            # Check if it's a valid hex color
            elif self._is_valid_hex_color(color):
                # Ensure it starts with #
                hex_color = color if color.startswith('#') else f'#{color}'
                processed_colors.append(hex_color.upper())
            else:
                print(f"Warning: Invalid color '{color}', skipping")
                continue
        
        if not processed_colors:
            return None
        
        # If we have fewer colors than subjects, cycle through them
        if len(processed_colors) < num_subjects:
            # Extend the list by cycling through existing colors
            original_colors = processed_colors.copy()
            while len(processed_colors) < num_subjects:
                processed_colors.extend(original_colors)
            # Trim to exact number needed
            processed_colors = processed_colors[:num_subjects]
        
        return processed_colors
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if a string is a valid hex color."""
        # Remove # if present
        hex_part = color[1:] if color.startswith('#') else color
        
        # Check if it's 3 or 6 characters and all hex digits
        if len(hex_part) == 3:
            return all(c in '0123456789ABCDEFabcdef' for c in hex_part)
        elif len(hex_part) == 6:
            return all(c in '0123456789ABCDEFabcdef' for c in hex_part)
        else:
            return False
        
    async def create_video_from_json(self, json_file_paths: list, output_video_path: str, vue_app_path: str = None, viewport_size: dict = None, timeout_ms: int = None, dev_server_url: str = None, loop_count: int = 1, camera_view: str = None, center_subjects: bool = True, zoom_factor: float = 1.0, subject_colors: list = None, interactive_mode: bool = False, quiet_mode: bool = True):
        """
        Main function to launch browser, load data files, and record video or open interactively.
        """
        self.verbose = not quiet_mode # Set verbose state for the logger

        # Use provided values or defaults
        if viewport_size is None:
            viewport_size = DEFAULT_VIEWPORT_SIZE
        if timeout_ms is None:
            timeout_ms = DEFAULT_TIMEOUT
            
        try:
            # Determine how to access the Vue app
            app_url = None
            
            if dev_server_url:
                # Use provided development server URL
                url_param = "" if interactive_mode else "?headless=true"
                app_url = f"{dev_server_url}{url_param}"
                self._log(f"Using development server at: {app_url}")
            elif vue_app_path:
                # Use provided static file path
                if not os.path.exists(vue_app_path):
                    self._log(f"Error: Vue app index.html not found at {vue_app_path}")
                    return False
                url_param = "" if interactive_mode else "?headless=true"
                app_url = f"file://{vue_app_path}{url_param}"
                self._log(f"Using Vue app file at: {vue_app_path}")
            else:
                # Try deployed version first, then local development server, then built files
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    try:
                        # First try the deployed version
                        async with session.get("https://opencap-visualizer.onrender.com/", timeout=10) as response:
                            if response.status == 200:
                                url_param = "" if interactive_mode else "?headless=true"
                                app_url = f"https://opencap-visualizer.onrender.com/{url_param}"
                                self._log("Using deployed OpenCap Visualizer at: https://opencap-visualizer.onrender.com/")
                            else:
                                raise aiohttp.ClientError("Deployed server not responding correctly")
                    except (aiohttp.ClientError, asyncio.TimeoutError):
                        self._log("Deployed version not available, trying local development server...")
                        
                        try:
                            # Fall back to local development server
                            async with session.get("http://localhost:3000", timeout=5) as response:
                                if response.status == 200:
                                    url_param = "" if interactive_mode else "?headless=true"
                                    app_url = f"http://localhost:3000{url_param}"
                                    self._log("Found local Vue development server at: http://localhost:3000")
                                else:
                                    raise aiohttp.ClientError("Local server not responding correctly")
                        except (aiohttp.ClientError, asyncio.TimeoutError):
                            self._log("Local development server not found, trying built files...")
                            
                            # Final fallback to built files
                            script_dir = Path(__file__).parent.absolute()
                            possible_paths = [
                                script_dir / "dist" / "index.html",
                                script_dir / "public" / "index.html",
                                script_dir / ".." / "dist" / "index.html",
                            ]
                            
                            app_index_path = None
                            for path in possible_paths:
                                if path.exists():
                                    app_index_path = str(path.absolute())
                                    break
                            
                            if not app_index_path:
                                self._log("Error: Could not find Vue app")
                                self._log("Please either:")
                                self._log("  1. Check your internet connection for the deployed version")
                                self._log("  2. Start the Vue dev server with 'npm run serve'")
                                self._log("  3. Build the Vue app with 'npm run build'")
                                self._log("  4. Specify --vue-app-path or --dev-server-url")
                                self._log(f"Searched for built files in: {[str(p) for p in possible_paths]}")
                                return False
                            
                            url_param = "" if interactive_mode else "?headless=true"
                            app_url = f"file://{app_index_path}{url_param}"
                            self._log(f"Using built Vue app at: {app_index_path}")
            
            if not app_url:
                self._log("Error: Could not determine Vue app URL")
                return False

            # Launch browser
            async with async_playwright() as p:
                if interactive_mode:
                    self._log("Launching interactive browser...")
                    self.browser = await p.chromium.launch(
                        headless=False,
                        args=[
                            '--disable-web-security',
                            '--disable-features=VizDisplayCompositor',
                            '--allow-file-access-from-files',
                            '--disable-dev-shm-usage',
                            '--no-sandbox'
                        ]
                    )
                else:
                    self._log("Launching headless browser...")
                    self.browser = await p.chromium.launch(
                        headless=True,
                        args=[
                            '--disable-web-security',
                            '--disable-features=VizDisplayCompositor',
                            '--allow-file-access-from-files',
                            '--disable-dev-shm-usage',
                            '--no-sandbox'
                        ]
                    )
                
                # Create page (with or without video recording)
                if interactive_mode:
                    context = await self.browser.new_context(viewport=viewport_size)
                else:
                    context = await self.browser.new_context(
                        viewport=viewport_size,
                        record_video_dir=str(Path(output_video_path).parent),
                        record_video_size=viewport_size
                    )
                self.page = await context.new_page()
                
                # Enable console logging for debugging, only if in verbose mode
                if self.verbose:
                    self.page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))

                # Navigate to Vue app
                self._log(f"Navigating to {app_url}...")
                
                try:
                    await self.page.goto(app_url, wait_until="networkidle", timeout=30000)
                    self._log("Page loaded successfully.")
                except Exception as e:
                    self._log(f"Error loading page: {e}")
                    return False

                # Wait for Vue app to be ready
                self._log("Waiting for Vue app to initialize...")
                try:
                    await self.page.wait_for_selector('#app', timeout=10000)
                    await self.page.wait_for_function(
                        "typeof window.sessionComponent !== 'undefined'", 
                        timeout=timeout_ms
                    )
                    self._log("Vue app initialized successfully.")
                except Exception as e:
                    self._log(f"Error waiting for Vue app: {e}")
                    self._log("Make sure the Session.vue component has 'window.sessionComponent = this;' in mounted()")
                    return False

                # Validate and categorize input files
                valid_files = []
                osim_mot_pairs = []
                
                # Separate different file types
                json_files = [f for f in json_file_paths if f.lower().endswith('.json')]
                osim_files = [f for f in json_file_paths if f.lower().endswith('.osim')]
                mot_files = [f for f in json_file_paths if f.lower().endswith('.mot')]
                
                # Validate JSON files
                for json_file_path in json_files:
                    if not os.path.exists(json_file_path):
                        self._log(f"Warning: JSON file not found: {json_file_path}. Skipping.")
                        continue
                    
                    try:
                        with open(json_file_path, 'r') as f:
                            json.load(f)  # Validate JSON format
                        valid_files.append(json_file_path)
                        self._log(f"Validated JSON file: {json_file_path}")
                    except json.JSONDecodeError as e:
                        self._log(f"Warning: Invalid JSON file {json_file_path}: {e}. Skipping.")
                        continue
                
                # Validate .osim/.mot file pairs
                if osim_files or mot_files:
                    if len(osim_files) != len(mot_files):
                        self._log(f"Error: Found {len(osim_files)} .osim files and {len(mot_files)} .mot files.")
                        self._log("Each .osim file must be paired with exactly one .mot file.")
                        return False
                    
                    # Check that all files exist
                    for osim_file in osim_files:
                        if not os.path.exists(osim_file):
                            self._log(f"Error: .osim file not found: {osim_file}")
                            return False
                    
                    for mot_file in mot_files:
                        if not os.path.exists(mot_file):
                            self._log(f"Error: .mot file not found: {mot_file}")
                            return False
                    
                    # Create pairs (assume they're in the same order as provided)
                    for i in range(len(osim_files)):
                        pair = {'osim': osim_files[i], 'mot': mot_files[i]}
                        osim_mot_pairs.append(pair)
                        self._log(f"Validated .osim/.mot pair: {os.path.basename(osim_files[i])} + {os.path.basename(mot_files[i])}")

                if not valid_files and not osim_mot_pairs:
                    self._log("Error: No valid input files found.")
                    return False
                
                total_subjects = len(valid_files) + len(osim_mot_pairs)
                self._log(f"Total subjects to visualize: {total_subjects} ({len(valid_files)} JSON, {len(osim_mot_pairs)} .osim/.mot pairs)")
                
                # Process and validate subject colors
                processed_colors = None
                if subject_colors:
                    processed_colors = self._process_subject_colors(subject_colors, total_subjects)
                    if processed_colors:
                        self._log(f"Subject colors: {processed_colors}")
                    else:
                        self._log("Warning: Invalid colors provided, using default colors")

                # Process all input files
                self._log(f"Processing {total_subjects} subjects...")
                
                # First, process JSON files
                if valid_files:
                    self._log(f"Loading {len(valid_files)} JSON files...")
                    file_data = []
                    for json_file_path in valid_files:
                        with open(json_file_path, 'r') as f:
                            content = f.read()
                        
                        file_data.append({
                            'name': os.path.basename(json_file_path),
                            'content': content,
                            'type': 'application/json'
                        })

                    # Inject JSON files
                    try:
                        await self.page.evaluate("""
                            async (fileDataArray) => {
                                // Reset any previous state
                                if (window.allVisualsLoaded) {
                                    delete window.allVisualsLoaded;
                                }
                                
                                // Create File objects
                                const files = fileDataArray.map(fileData => {
                                    const blob = new Blob([fileData.content], { type: fileData.type });
                                    return new File([blob], fileData.name, { type: fileData.type });
                                });
                                
                                // Call handleFileUpload on the Session component
                                const sessionComponent = window.sessionComponent;
                                if (!sessionComponent) {
                                    throw new Error('Session component not found');
                                }
                                
                                sessionComponent.handleFileUpload({ 
                                    target: { 
                                        files: files,
                                        value: '' // Reset input value
                                    } 
                                });
                                
                                return files.length;
                            }
                        """, file_data)
                        
                        self._log(f"Successfully loaded {len(file_data)} JSON files.")
                        
                    except Exception as e:
                        self._log(f"Error loading JSON files: {e}")
                        return False
                
                # Then, process .osim/.mot pairs
                if osim_mot_pairs:
                    self._log(f"Converting and loading {len(osim_mot_pairs)} .osim/.mot pairs...")
                    
                    for i, pair in enumerate(osim_mot_pairs):
                        try:
                            self._log(f"Converting pair {i+1}/{len(osim_mot_pairs)}: {os.path.basename(pair['osim'])} + {os.path.basename(pair['mot'])}")
                            self._log("This may take up to 60 seconds depending on file size...")
                            
                            # Read file contents
                            with open(pair['osim'], 'r') as f:
                                osim_content = f.read()
                            with open(pair['mot'], 'r') as f:
                                mot_content = f.read()
                            
                            # Inject .osim/.mot pair and trigger conversion (with timeout)
                            await asyncio.wait_for(self.page.evaluate("""
                                async (fileData) => {
                                    const sessionComponent = window.sessionComponent;
                                    if (!sessionComponent) {
                                        throw new Error('Session component not found');
                                    }
                                    
                                    // Create File objects for .osim and .mot
                                    const osimBlob = new Blob([fileData.osim.content], { type: 'text/plain' });
                                    const motBlob = new Blob([fileData.mot.content], { type: 'text/plain' });
                                    
                                    const osimFile = new File([osimBlob], fileData.osim.name, { type: 'text/plain' });
                                    const motFile = new File([motBlob], fileData.mot.name, { type: 'text/plain' });
                                    
                                    // Set the files on the session component
                                    sessionComponent.osimFile = osimFile;
                                    sessionComponent.motFile = motFile;
                                    
                                    console.log('[Headless] Starting .osim/.mot conversion for:', fileData.osim.name, '+', fileData.mot.name);
                                    
                                    // Set up a promise to track conversion completion
                                    return new Promise((resolve, reject) => {
                                        // Set up conversion tracking
                                        const originalConvertingValue = sessionComponent.converting;
                                        
                                        // Override the conversion completion handler
                                        const originalHandleFileUpload = sessionComponent.handleFileUpload;
                                        sessionComponent.handleFileUpload = function(event) {
                                            console.log('[Headless] Conversion completed, loading JSON...');
                                            const result = originalHandleFileUpload.call(this, event);
                                            // Restore original handler
                                            sessionComponent.handleFileUpload = originalHandleFileUpload;
                                            resolve(true);
                                            return result;
                                        };
                                        
                                        // Handle conversion errors
                                        const checkForError = () => {
                                            if (sessionComponent.conversionError) {
                                                sessionComponent.handleFileUpload = originalHandleFileUpload;
                                                reject(new Error(sessionComponent.conversionError));
                                                return;
                                            }
                                            if (sessionComponent.converting) {
                                                setTimeout(checkForError, 500);
                                            }
                                        };
                                        
                                        // Start the conversion
                                        sessionComponent.convertAndLoadOpenSimFiles().catch(error => {
                                            sessionComponent.handleFileUpload = originalHandleFileUpload;
                                            reject(error);
                                        });
                                        
                                        // Start error checking
                                        setTimeout(checkForError, 500);
                                    });
                                }
                            """, {
                                'osim': {
                                    'name': os.path.basename(pair['osim']),
                                    'content': osim_content
                                },
                                'mot': {
                                    'name': os.path.basename(pair['mot']),
                                    'content': mot_content
                                }
                            }), timeout=120.0)  # 2 minute timeout for conversion
                            
                            self._log(f"Successfully converted and loaded pair {i+1}")
                            
                            # Wait a moment between conversions to let the system settle
                            await asyncio.sleep(2.0)
                            
                        except Exception as e:
                            self._log(f"Error processing .osim/.mot pair {i+1}: {e}")
                            return False

                # Wait for all visuals to load
                self._log("Waiting for all geometries to load...")
                try:
                    await self.page.wait_for_function(
                        "window.allVisualsLoaded === true", 
                        timeout=timeout_ms
                    )
                    self._log("All visuals loaded successfully.")
                except Exception as e:
                    self._log(f"Timeout waiting for visuals to load: {e}")
                    self._log("Make sure 'window.allVisualsLoaded = true;' is set in Session.vue when ready.")
                    return False
                
                # Apply custom subject colors if provided
                if processed_colors:
                    self._log(f"Applying custom colors to {len(processed_colors)} subjects...")
                    try:
                        for i, color in enumerate(processed_colors):
                            await self.page.evaluate(f"""
                                if (window.sessionComponent.updateSubjectColor) {{
                                    console.log('[Headless] Setting subject {i} color to {color}');
                                    window.sessionComponent.updateSubjectColor({i}, '{color}');
                                }} else {{
                                    console.error('[Headless] updateSubjectColor function not found');
                                }}
                            """)
                        
                        await asyncio.sleep(0.5)  # Wait for color updates to apply
                        self._log("Custom colors applied successfully.")
                    except Exception as e:
                        self._log(f"Warning: Failed to apply custom colors: {e}")

                if interactive_mode:
                    self._log("🎉 Interactive mode: Browser opened with subjects loaded!")
                    
                    # Give a moment for all Vue reactivity to settle
                    await asyncio.sleep(1.0)
                    
                    # Check and ensure UI controls are visible in interactive mode
                    try:
                        current_state = await self.page.evaluate("""
                            ({
                                hasTrial: !!window.sessionComponent.trial,
                                hasFrames: window.sessionComponent.frames ? window.sessionComponent.frames.length : 0,
                                animationsCount: window.sessionComponent.animations ? window.sessionComponent.animations.length : 0
                            })
                        """)
                        self._log(f"Current state: trial={current_state['hasTrial']}, frames={current_state['hasFrames']}, animations={current_state['animationsCount']}")
                        
                        await self.page.evaluate("""
                            // Ensure trial is set so controls are visible
                            if (!window.sessionComponent.trial) {
                                console.log('[Interactive] Setting trial for UI controls');
                                window.sessionComponent.trial = { results: [] };
                            }
                            
                            // Also ensure frames are set if we have animations but no frames
                            if (window.sessionComponent.animations.length > 0 && 
                                (!window.sessionComponent.frames || window.sessionComponent.frames.length === 0)) {
                                console.log('[Interactive] Setting frames from first animation');
                                if (window.sessionComponent.animations[0].data && window.sessionComponent.animations[0].data.time) {
                                    window.sessionComponent.frames = window.sessionComponent.animations[0].data.time;
                                }
                            }
                            
                            // Force Vue reactivity update
                            if (window.sessionComponent.$forceUpdate) {
                                window.sessionComponent.$forceUpdate();
                            }
                        """)
                        self._log("Ensured UI controls are visible for interactive mode")
                    except Exception as e:
                        self._log(f"Warning: Could not ensure UI visibility: {e}")
                    
                    self._log("You can now:")
                    self._log("  - Explore the visualization manually")
                    self._log("  - Adjust camera angles, colors, and settings")
                    self._log("  - Use the recording controls in the web interface")
                    self._log("  - Press Ctrl+C to close when done")
                    
                    # Keep the browser open until interrupted
                    try:
                        self._log("Keeping browser open... Press Ctrl+C to exit.")
                        while True:
                            await asyncio.sleep(1.0)
                    except KeyboardInterrupt:
                        self._log("\nClosing browser...")
                        await context.close()
                        await self.browser.close()
                        return True
                
                # Give a moment for all Vue reactivity to settle before recording
                await asyncio.sleep(1.0)
                
                # Set up headless recording using Session.vue's built-in recording functionality
                self._log("Setting up headless recording...")
                
                # Set up recording completion callback with more debugging
                await self.page.evaluate("""
                    window.recordingCompleted = false;
                    window.recordingBlob = null;
                    
                    // Override the finishedRecording function to capture the blob
                    window.finishedRecording = (blobUrl) => {
                        console.log('[Headless] Recording finished callback triggered with URL:', blobUrl);
                        window.recordingCompleted = true;
                        window.recordingBlobUrl = blobUrl;
                    };
                    
                    // Add debug logging to session component
                    const originalStopRecording = window.sessionComponent.stopRecording;
                    window.sessionComponent.stopRecording = function() {
                        console.log('[Headless] stopRecording called, isRecording:', this.isRecording);
                        return originalStopRecording.call(this);
                    };
                """)
                
                # Ensure animation is ready and at frame 0
                await self.page.evaluate("""
                    console.log('[Headless] Resetting animation to frame 0');
                    window.sessionComponent.frame = 0;
                    window.sessionComponent.playing = false;
                    window.sessionComponent.animateOneFrame();
                """)
                
                # Wait a moment for the reset to take effect
                await asyncio.sleep(0.5)
                
                # Configure recording settings
                await self.page.evaluate(f"""
                    // Set recording for specified number of loops
                    window.sessionComponent.loopCount = {loop_count};
                    window.sessionComponent.currentLoop = 0;
                    
                    // Always use WebM for recording (for better browser compatibility)
                    // We'll convert to MP4 with proper H.264 codec using ffmpeg if needed
                    window.sessionComponent.recordingFormat = 'webm';
                    
                    console.log('[Headless] Configured recording: {loop_count} loop(s), webm format');
                    console.log('[Headless] Current frame:', window.sessionComponent.frame);
                    console.log('[Headless] Total frames:', window.sessionComponent.frames.length);
                    console.log('[Headless] Frame rate:', window.sessionComponent.frameRate);
                """)
                
                # Check if we have valid frame data
                frame_info = await self.page.evaluate("""
                    ({
                        currentFrame: window.sessionComponent.frame,
                        totalFrames: window.sessionComponent.frames.length,
                        frameRate: window.sessionComponent.frameRate,
                        isPlaying: window.sessionComponent.playing,
                        isRecording: window.sessionComponent.isRecording
                    })
                """)
                
                self._log(f"Animation state: frame {frame_info['currentFrame']}/{frame_info['totalFrames']}, "
                      f"fps: {frame_info['frameRate']}, playing: {frame_info['isPlaying']}, "
                      f"recording: {frame_info['isRecording']}")
                
                if frame_info['totalFrames'] == 0:
                    self._log("Error: No animation frames loaded")
                    return False
                
                expected_duration = (frame_info['totalFrames'] / frame_info['frameRate']) * loop_count
                self._log(f"Expected recording duration: {expected_duration:.2f} seconds for {loop_count} loop(s)")
                
                # Center camera on subjects first (if requested)
                if center_subjects:
                    self._log("Centering camera on subjects...")
                    try:
                        if total_subjects > 1:
                            # For multiple subjects, center on all animations
                            await self.page.evaluate("""
                                // Center on all animations by calculating combined bounding box
                                if (window.sessionComponent.animations.length > 0) {
                                    const boundingBox = new THREE.Box3();
                                    
                                    window.sessionComponent.animations.forEach((animation, index) => {
                                        const meshKeys = Object.keys(window.sessionComponent.meshes)
                                            .filter(key => key.startsWith(`anim${index}_`));
                                        
                                        meshKeys.forEach(key => {
                                            const mesh = window.sessionComponent.meshes[key];
                                            if (mesh && mesh.visible) {
                                                boundingBox.expandByObject(mesh);
                                            }
                                        });
                                    });
                                    
                                    if (!boundingBox.isEmpty()) {
                                        const center = new THREE.Vector3();
                                        boundingBox.getCenter(center);
                                        
                                        const size = new THREE.Vector3();
                                        boundingBox.getSize(size);
                                        const maxDim = Math.max(size.x, size.y, size.z);
                                        const fov = window.sessionComponent.camera.fov * (Math.PI / 180);
                                        const distance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;
                                        
                                        const direction = new THREE.Vector3(1, 1, 1).normalize();
                                        const position = center.clone().add(direction.multiplyScalar(distance));
                                        
                                        window.sessionComponent.controls.target.copy(center);
                                        window.sessionComponent.camera.position.copy(position);
                                        window.sessionComponent.controls.update();
                                        window.sessionComponent.renderer.render(window.sessionComponent.scene, window.sessionComponent.camera);
                                        
                                        console.log('[Headless] Centered camera on all subjects');
                                    }
                                }
                            """)
                        else:
                            # For single subject, use the built-in function
                            await self.page.evaluate("window.sessionComponent.centerCameraOnAnimation(0)")
                        
                        await asyncio.sleep(0.3)  # Wait for camera adjustment
                    except Exception as e:
                        self._log(f"Warning: Failed to center camera: {e}")
                
                # Set camera view if specified (this will override centering but that's expected)
                if camera_view:
                    # Map anatomical terms to Session.vue camera views
                    camera_mapping = {
                        'anterior': 'right',       # Front-facing (person facing camera)
                        'posterior': 'left',       # Back view (person's back to camera)
                        'sagittal': 'front',       # Side profile view
                        'lateral': 'front',        # Side profile view (synonym)
                        'superior': 'top',         # Top-down view
                        'inferior': 'bottom',      # Bottom-up view
                        'frontal': 'right',        # Frontal plane view (same as anterior)
                        'coronal': 'right',        # Coronal plane view (same as anterior)
                    }
                    
                    # Use mapping if available, otherwise use the provided view directly
                    actual_view = camera_mapping.get(camera_view.lower(), camera_view)
                    view_description = f"{camera_view} (mapped to {actual_view})" if camera_view.lower() in camera_mapping else camera_view
                    
                    self._log(f"Setting camera view to: {view_description}")
                    try:
                        await self.page.evaluate(f"window.sessionComponent.setCameraView('{actual_view}')")
                        # Wait a moment for camera to adjust
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self._log(f"Warning: Failed to set camera view '{actual_view}': {e}")
                
                # Apply zoom factor AFTER camera view is set (so it doesn't get overridden)
                if zoom_factor != 1.0:
                    self._log(f"Applying zoom factor: {zoom_factor}")
                    try:
                        # First, let's check current camera state
                        before_state = await self.page.evaluate("""
                            ({
                                position: {
                                    x: window.sessionComponent.camera.position.x,
                                    y: window.sessionComponent.camera.position.y,
                                    z: window.sessionComponent.camera.position.z
                                },
                                target: {
                                    x: window.sessionComponent.controls.target.x,
                                    y: window.sessionComponent.controls.target.y,
                                    z: window.sessionComponent.controls.target.z
                                },
                                distance: window.sessionComponent.camera.position.distanceTo(window.sessionComponent.controls.target)
                            })
                        """)
                        self._log(f"Before zoom - Distance: {before_state['distance']:.2f}, Position: {before_state['position']}")
                        
                        await self.page.evaluate(f"""
                            const currentDistance = window.sessionComponent.camera.position.distanceTo(window.sessionComponent.controls.target);
                            const newDistance = currentDistance * {zoom_factor};
                            
                            console.log('[Headless] Zoom adjustment - Current distance:', currentDistance, 'New distance:', newDistance, 'Zoom factor:', {zoom_factor});
                            
                            // Access THREE through the camera object since THREE is not global
                            // Create a direction vector by copying camera position and subtracting target
                            const direction = window.sessionComponent.camera.position.clone()
                                .sub(window.sessionComponent.controls.target)
                                .normalize();
                            
                            console.log('[Headless] Direction vector:', direction);
                            
                            // Set new camera position
                            const newPosition = window.sessionComponent.controls.target.clone()
                                .add(direction.multiplyScalar(newDistance));
                            
                            console.log('[Headless] Old position:', window.sessionComponent.camera.position);
                            console.log('[Headless] New position:', newPosition);
                            
                            window.sessionComponent.camera.position.copy(newPosition);
                            window.sessionComponent.controls.update();
                            window.sessionComponent.renderer.render(window.sessionComponent.scene, window.sessionComponent.camera);
                            
                            const finalDistance = window.sessionComponent.camera.position.distanceTo(window.sessionComponent.controls.target);
                            console.log('[Headless] Final distance after zoom:', finalDistance);
                        """)
                        
                        await asyncio.sleep(0.5)  # Wait for camera adjustment
                        
                        # Check final camera state
                        after_state = await self.page.evaluate("""
                            ({
                                position: {
                                    x: window.sessionComponent.camera.position.x,
                                    y: window.sessionComponent.camera.position.y,
                                    z: window.sessionComponent.camera.position.z
                                },
                                target: {
                                    x: window.sessionComponent.controls.target.x,
                                    y: window.sessionComponent.controls.target.y,
                                    z: window.sessionComponent.controls.target.z
                                },
                                distance: window.sessionComponent.camera.position.distanceTo(window.sessionComponent.controls.target)
                            })
                        """)
                        self._log(f"After zoom - Distance: {after_state['distance']:.2f}, Position: {after_state['position']}")
                        
                        expected_distance = before_state['distance'] * zoom_factor
                        actual_distance = after_state['distance'] 
                        self._log(f"Expected distance: {expected_distance:.2f}, Actual distance: {actual_distance:.2f}")
                        
                        if abs(expected_distance - actual_distance) > 0.1:
                            self._log("⚠️  Warning: Zoom may not have been applied correctly!")
                            
                    except Exception as e:
                        self._log(f"Warning: Failed to apply zoom factor: {e}")
                
                # Final camera state check before recording
                final_camera_state = await self.page.evaluate("""
                    ({
                        distance: window.sessionComponent.camera.position.distanceTo(window.sessionComponent.controls.target),
                        position: {
                            x: window.sessionComponent.camera.position.x,
                            y: window.sessionComponent.camera.position.y,
                            z: window.sessionComponent.camera.position.z
                        }
                    })
                """)
                self._log(f"Final camera state before recording - Distance: {final_camera_state['distance']:.2f}")
                
                # Start recording using Session.vue's built-in method
                await self.page.evaluate("window.sessionComponent.startRecording()")
                self._log("Started recording using Session.vue's built-in recording system...")
                
                # Monitor recording progress
                start_time = asyncio.get_event_loop().time()
                
                # Wait for recording to complete (with timeout)
                try:
                    await self.page.wait_for_function(
                        "window.recordingCompleted === true", 
                        timeout=max(timeout_ms, int(expected_duration * 1000) + 30000)  # At least expected duration + 30s buffer
                    )
                    
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    self._log(f"Recording completed successfully in {elapsed_time:.2f} seconds!")
                    
                except Exception as e:
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    self._log(f"Timeout waiting for recording to complete after {elapsed_time:.2f} seconds: {e}")
                    
                    # Check current state for debugging
                    current_state = await self.page.evaluate("""
                        ({
                            isRecording: window.sessionComponent.isRecording,
                            isPlaying: window.sessionComponent.playing,
                            currentFrame: window.sessionComponent.frame,
                            currentLoop: window.sessionComponent.currentLoop,
                            loopCount: window.sessionComponent.loopCount,
                            recordingCompleted: window.recordingCompleted
                        })
                    """)
                    self._log(f"Current state: {current_state}")
                    
                    # Try to stop recording gracefully
                    await self.page.evaluate("window.sessionComponent.stopRecording()")
                    return False
                
                # Download the recorded video blob
                try:
                    blob_url = await self.page.evaluate("window.recordingBlobUrl")
                    if not blob_url:
                        self._log("Error: No recording blob URL found")
                        return False
                    
                    self._log("Downloading recorded video...")
                    
                    # Download the blob as a file
                    async with self.page.expect_download() as download_info:
                        await self.page.evaluate(f"""
                            // Create a temporary download link
                            const a = document.createElement('a');
                            a.href = '{blob_url}';
                            a.download = 'recorded_video.webm';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        """)
                    
                    download = await download_info.value
                    
                    # Save the file with proper format handling
                    if output_video_path.endswith('.mp4'):
                        # Save as webm first, then convert to proper MP4 with H.264
                        temp_webm_path = output_video_path.replace('.mp4', '_temp.webm')
                        await download.save_as(temp_webm_path)
                        
                        # Convert to proper MP4 with H.264 codec using ffmpeg
                        try:
                            import subprocess
                            result = subprocess.run([
                                'ffmpeg', '-i', temp_webm_path, 
                                '-c:v', 'libx264', '-crf', '23', 
                                '-preset', 'medium', '-pix_fmt', 'yuv420p',
                                '-y', output_video_path
                            ], check=True, capture_output=True)
                            
                            # Clean up temp file after successful conversion
                            Path(temp_webm_path).unlink()
                            self._log(f"Video saved as: {output_video_path} (converted to H.264 MP4)")
                            
                        except FileNotFoundError:
                            # ffmpeg not installed - save as webm instead
                            Path(temp_webm_path).unlink()
                            webm_path = output_video_path.replace('.mp4', '.webm')
                            await download.save_as(webm_path)
                            self._log(f"Video saved as: {webm_path} (WebM format - install ffmpeg for MP4)")
                            
                        except subprocess.CalledProcessError as e:
                            # ffmpeg failed - save as webm instead
                            Path(temp_webm_path).unlink()
                            webm_path = output_video_path.replace('.mp4', '.webm')
                            await download.save_as(webm_path)
                            self._log(f"Video saved as: {webm_path} (WebM format - ffmpeg conversion failed)")
                            stderr_output = e.stderr.decode() if e.stderr else 'Unknown error'
                            self._log(f"ffmpeg error: {stderr_output}")
                            
                    else:
                        # Save directly as webm
                        await download.save_as(output_video_path)
                        self._log(f"Video saved as: {output_video_path}")
                
                except Exception as e:
                    self._log(f"Error downloading video: {e}")
                    return False
                finally:
                    # Clean up blob URL
                    await self.page.evaluate("URL.revokeObjectURL(window.recordingBlobUrl)")
                
                # Close browser
                await context.close()
                await self.browser.close()

                # Special handling for quiet mode: print only the absolute output path on success
                if quiet_mode:
                    print(Path(output_video_path).resolve())
                else:
                    # The success message will be handled by main() for non-quiet mode
                    pass 

                return True

        except Exception as e:
            self._log(f"Unexpected error: {e}")
            return False
        finally:
            if self.browser:
                await self.browser.close()

def main():
    parser = argparse.ArgumentParser(
        description="Generate a video from OpenCap Visualizer using JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.json -o animation.mp4
  %(prog)s subject1.json subject2.json -o comparison.mp4
  %(prog)s model.osim motion.mot -o simulation.mp4
  %(prog)s subject1.json subject2.json --colors red blue -o colored_comparison.mp4
  %(prog)s data.json --loops 3 --camera anterior --colors #ff0000 -o red_frontal_view.mp4
  %(prog)s model.osim motion.mot --camera sagittal --zoom 1.5 --colors green -o green_profile.mp4
  %(prog)s s1.json s2.json s3.json --colors red green blue --camera anterior -o rgb_comparison.mp4
  %(prog)s data.json --camera superior --colors yellow -o yellow_top_down.mp4
  %(prog)s data.json --interactive --camera anterior --colors red  # Interactive mode
  %(prog)s subject1.json subject2.json --interactive  # Multiple subjects, manual exploration

Note: Uses deployed OpenCap Visualizer at https://opencap-visualizer.onrender.com/ by default.
No local setup required!
        """
    )
    
    parser.add_argument(
        "input_files",
        metavar="FILE",
        type=str,
        nargs="+",
        help="Path to data files to visualize. Supports: JSON files, or pairs of .osim and .mot files."
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=DEFAULT_OUTPUT_FILENAME,
        help=f"Output video file path (default: {DEFAULT_OUTPUT_FILENAME})"
    )
    
    parser.add_argument(
        "--vue-app-path",
        type=str,
        help="Absolute path to the built Vue app's index.html file"
    )
    
    parser.add_argument(
        "--dev-server-url",
        type=str,
        help="URL of a custom Vue server (default uses deployed version at https://opencap-visualizer.onrender.com/)"
    )
    
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_VIEWPORT_SIZE["width"],
        help=f"Video width in pixels (default: {DEFAULT_VIEWPORT_SIZE['width']})"
    )
    
    parser.add_argument(
        "--height", 
        type=int,
        default=DEFAULT_VIEWPORT_SIZE["height"],
        help=f"Video height in pixels (default: {DEFAULT_VIEWPORT_SIZE['height']})"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT // 1000,
        help=f"Timeout in seconds for loading (default: {DEFAULT_TIMEOUT // 1000})"
    )
    
    parser.add_argument(
        "--loops",
        type=int,
        default=1,
        help="Number of animation loops to record (default: 1)"
    )
    
    parser.add_argument(
        "--camera",
        type=str,
        choices=[
            # Original Session.vue views
            'top', 'bottom', 'front', 'back', 'left', 'right',
            'frontTopRight', 'frontTopLeft', 'frontBottomRight', 'frontBottomLeft',
            'backTopRight', 'backTopLeft', 'backBottomRight', 'backBottomLeft',
            'isometric', 'default',
            # Anatomical aliases for biomechanics users
            'anterior', 'posterior', 'sagittal', 'lateral', 'superior', 'inferior',
            'frontal', 'coronal'
        ],
        help="Camera view position. Anatomical views: anterior/frontal/coronal (front-facing), "
             "posterior (back), sagittal/lateral (side), superior (top), inferior (bottom)"
    )
    
    parser.add_argument(
        "--no-center",
        action="store_true",
        help="Disable automatic centering of the camera on subjects (centering is enabled by default)"
    )
    
    parser.add_argument(
        "--zoom",
        type=float,
        default=1.5,
        help="Zoom factor for the camera. Values > 1.0 zoom out (further), < 1.0 zoom in (closer). Default: 1.5 (zoomed out)"
    )
    
    parser.add_argument(
        "--colors",
        type=str,
        nargs="+",
        help="Colors for subjects in hex format (e.g., #ff0000 #00ff00) or predefined names (red, green, blue, yellow, etc.). "
             "Number of colors should match number of subjects. If fewer colors than subjects, colors will cycle."
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Open browser in interactive mode (non-headless) for manual exploration. No video recording will occur."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output, including script progress and browser console logs."
    )

    args = parser.parse_args()

    # Validate Vue app path if provided
    if args.vue_app_path:
        if not os.path.isabs(args.vue_app_path):
            print("Error: --vue-app-path must be an absolute path.")
            sys.exit(1)
        if not os.path.exists(args.vue_app_path):
            print(f"Error: Vue app file not found: {args.vue_app_path}")
            sys.exit(1)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare configuration
    viewport_size = {"width": args.width, "height": args.height}
    timeout_ms = args.timeout * 1000

    # Create CLI instance and run
    cli = VisualizerCLI()
    
    try:
        success = asyncio.run(cli.create_video_from_json(
            json_file_paths=args.input_files, 
            output_video_path=str(output_path), 
            vue_app_path=args.vue_app_path,
            viewport_size=viewport_size,
            timeout_ms=timeout_ms,
            dev_server_url=args.dev_server_url,
            loop_count=args.loops,
            camera_view=args.camera,
            center_subjects=not args.no_center,
            zoom_factor=args.zoom,
            subject_colors=args.colors,
            interactive_mode=args.interactive,
            quiet_mode=(not args.verbose)
        ))
        
        if success:
            if args.verbose: # Only print success message in verbose mode
                print("✅ Video generation completed successfully!")
            # In quiet mode, the path is already printed by create_video_from_json
            sys.exit(0)
        else:
            if args.verbose: # Print detailed failure in verbose mode
                print("❌ Video generation failed.")
            else: # Print simple failure message in quiet mode to stderr
                print("Video generation failed.", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 