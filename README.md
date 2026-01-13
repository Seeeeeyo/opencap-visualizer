# OpenCap Visualizer

A comprehensive web-based platform for interactive visualization and automated video creation of biomechanics data. Built with Vue.js and Three.js, the visualizer supports multiple data formats including OpenSim models (.osim files), kinematics data (.mot, .json), markers (.trc), and force data (.mot).

## 🌐 Live Demo

**Try it now**: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)

No installation required - works directly in your browser!

## 🚀 Quick Start

### Web Interface
1. Visit [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)
2. Upload your biomechanics data files
3. Explore interactive 3D visualizations
4. Generate videos and screenshots

### Python Package
For programmatic video generation, install the Python package:

```bash
pip install opencap-visualizer
playwright install chromium
```

```python
import opencap_visualizer as ocv

# Generate video from single subject
success = ocv.create_video(
    "subject_data.json", 
    "output_video.mp4",
    camera="anterior",
    loops=2
)

# Compare multiple subjects
success = ocv.create_video(
    ["subject1.json", "subject2.json"],
    "comparison.mp4",
    colors=["red", "blue"],
    camera="sagittal"
)
```

### Command Line Interface

```bash
# Basic video creation
opencap-visualizer input.json output.mp4

# With camera angle and loops
opencap-visualizer input.json output.mp4 --camera anterior --loops 3

# Compare multiple subjects with colors
opencap-visualizer subject1.json subject2.json output.mp4 --colors red blue

# Custom zoom and resolution
opencap-visualizer input.json output.mp4 --zoom 1.5 --width 1920 --height 1080
```

### Available Camera Angles

| Angle | Description |
|-------|-------------|
| `anterior` | Front view |
| `posterior` | Back view |
| `sagittal` | Side view (left) |
| `sagittal_right` | Side view (right) |
| `superior` | Top-down view |
| `isometric` | 3D perspective view |

**📦 Package Repository**: [opencap-visualizer-pip](https://github.com/Seeeeeyo/opencap-visualizer-pip)

## 🔧 Key Features

### Interactive Web-Based Visualization
- **Real-time 3D rendering** of skeletal models with anatomically accurate geometry
- **Multi-subject comparison** with independent color coding and transparency controls
- **Marker visualization** supporting standard motion capture marker sets (.trc files)
- **Ground reaction forces visualization** using .mot files
- **Video synchronization** with skeleton for simultaneous viewing
- **Timeline controls** with adjustable playback speed and frame-by-frame navigation
- **Recording capabilities** for capturing custom video segments
- **Image capture** for high-resolution screenshots
- **Timelapse mode** for accelerated visualizations
- **Color controls** for customizing all visual elements

### Python API for Automated Video Creation
- **Command-line interface** for batch processing
- **Python API** for integration into analysis pipelines
- **Multiple camera angles** (anterior, posterior, sagittal, superior, etc.)
- **Customizable output** (resolution, colors, loops, zoom)
- **Headless operation** for server-side processing

## 🎮 User Interface Guide

### Loading Data
There are multiple ways to load your biomechanics data:

1. **Drag & Drop**: Simply drag files directly into the viewer window
2. **Import Button**: Click the Import button for specific file types
3. **Sample Data**: Click "Try with Sample Files" to explore with pre-loaded examples
4. **URL Sharing**: Open a shared visualization link

Supported file combinations:
- `.json` - Motion data (OpenCap format)
- `.trc` - Motion capture markers (can be loaded independently)
- `.osim` + `.mot` - OpenSim model with kinematics
- `.mot` - Ground reaction force data (auto-positioned at feet)

### Camera Controls

The 3D cube gizmo at the bottom of the viewer provides intuitive camera control:

| View | Description |
|------|-------------|
| **Front (Z)** | View from the front of the subject |
| **Back (-Z)** | View from behind the subject |
| **Right (X)** | View from the right side |
| **Left (-X)** | View from the left side |
| **Top (Y)** | Bird's eye view from above |
| **Bottom (-Y)** | View from below |
| **Corner Views** | Click cube corners for isometric perspectives |
| **Arrow Buttons** | Rotate smoothly between adjacent views |
| **Reset Button** | Return to default perspective |

You can also click and drag anywhere in the 3D view to orbit, scroll to zoom, and right-click drag to pan.

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause animation |
| `←` Arrow | Previous frame (stops playback) |
| `→` Arrow | Next frame (stops playback) |
| `↑` Arrow | Increase playback speed (+0.25x) |
| `↓` Arrow | Decrease playback speed (-0.25x) |
| `Shift` + Arrow Keys | Nudge selected subject position |

### Playback Controls

- **Play/Pause**: Toggle animation playback
- **Loop**: Enable/disable continuous looping
- **Speed**: Adjust from 0.25x to 4x playback speed
- **Timeline Slider**: Scrub through the animation
- **Time Input**: Jump to a specific time in seconds
- **Frame Navigation**: Step through frame by frame

### Scene Customization

#### Ground Settings
- **Visibility**: Show/hide the ground plane
- **Color**: Customize ground color
- **Opacity**: Adjust transparency (0-100%)
- **Texture**: Toggle checkerboard or grid patterns
- **Position**: Adjust vertical position (Y offset)

#### Background & Lighting
- **Background Color**: Set scene background
- **Lighting**: Toggle realistic lighting with shadows
- **Shadow Quality**: Adjust shadow resolution

#### Subject Controls
- **Color**: Assign unique colors to each subject
- **Transparency**: Adjust individual subject opacity
- **Offset**: Position subjects with X/Y/Z offsets
- **Visibility**: Show/hide individual subjects

### Recording & Export

#### Video Recording
1. Configure recording settings (loops, capture mode)
2. Click **Record** to start
3. Playback will automatically begin
4. Click **Stop** when done
5. Video downloads as `.webm` file

#### Screenshot Capture
- Capture high-resolution images of the current view
- Options for transparent background export
- Perfect for publications and presentations

#### Timelapse Mode
- Create motion trails showing movement over time
- Adjustable interval and opacity settings
- Great for visualizing movement patterns

### Sharing Visualizations

1. Load your data into the visualizer
2. Click the **Share** button in the sidebar
3. Choose sharing method:
   - **URL Sharing**: Generate a shareable link (data embedded in URL)
   - **Backend Storage**: For larger files, data is stored server-side
4. Copy the generated URL to share with others

#### Embedding
Add `?embed=true` to any visualization URL to hide the UI controls for clean embedding in websites or presentations.

## 📁 Supported Data Formats

### File Types

| Format | Description | Usage |
|--------|-------------|-------|
| `.json` | OpenCap motion data | Primary format with skeleton + kinematics |
| `.osim` | OpenSim model | Skeletal model definition |
| `.mot` | Motion/Forces | Kinematics (with .osim) or GRF data |
| `.trc` | Marker data | Motion capture markers |

### JSON Motion Data Format

The visualizer uses a JSON format that includes skeleton definition and joint positions:

```json
{
  "joints": [0.0, 0.9, 0.0, ...],  // Flattened joint positions [x,y,z, x,y,z, ...]
  "joint_names": ["Pelvis", "L_Hip", "R_Hip", ...],
  "joint_count": 24,
  "fps": 30,
  "frames": 150
}
```

### OpenSim Workflow

For OpenSim users:
1. Use the [OpenSim Converter API](https://github.com/Seeeeeyo/opensim-to-visualizer-api) to convert `.osim` + `.mot` files
2. Or drag & drop both files directly into the visualizer (automatic conversion)

### Marker Data (.trc)

Standard TRC format from motion capture systems:
- Markers are displayed as colored spheres
- Can be loaded independently or alongside skeleton data
- Marker size and color are customizable

### Ground Reaction Forces (.mot)

Force files are automatically detected and visualized:
- Force vectors rendered at the feet
- Magnitude indicated by vector length
- Customizable colors and scaling

## 🔄 OpenSim Integration

For OpenSim users, we provide a dedicated converter API:

**🔗 OpenSim Converter**: [opensim-to-visualizer-api](https://github.com/Seeeeeyo/opensim-to-visualizer-api)

This service converts OpenSim .osim and .mot files into the JSON format required by the visualizer, enabling seamless integration with existing OpenSim workflows.

## 💡 Tips & Best Practices

### Multi-Subject Comparison
- Load multiple JSON files to compare subjects side-by-side
- Use distinct colors for each subject for clarity
- Adjust transparency to see overlapping movements
- Use X/Y/Z offsets to position subjects apart

### Creating Publication-Quality Videos
1. Set up your desired camera angle
2. Customize colors and background
3. Hide unnecessary elements (ground, markers if not needed)
4. Use high bitrate in recording settings
5. Record multiple loops for smoother transitions

### Performance Tips
- For large files, consider reducing playback speed initially
- Close unnecessary browser tabs to free up GPU resources
- Use Chrome or Edge for best WebGL performance

### Video Overlay
- Load a reference video alongside your motion data
- Adjust opacity to blend video with 3D skeleton
- Use chroma key to remove green screen backgrounds
- Sync video playback with motion data timeline

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Blank screen** | Ensure WebGL is enabled in your browser |
| **Slow performance** | Close other tabs, use a dedicated GPU |
| **File won't load** | Check file format matches expected structure |
| **Markers not visible** | Increase marker size in display settings |
| **Ground flickering** | Adjust ground position to avoid z-fighting |
| **Video not syncing** | Verify video frame rate matches motion data FPS |

## 🏗️ Architecture

### Frontend
- **Vue.js** for reactive user interface components
- **Three.js** for 3D graphics rendering and animation
- **Vuetify** for Material Design components

### Backend Services
- **Node.js sharing backend** for URL-based data sharing
- **Python CLI and API** using Playwright for automated browser control
- **OpenSim file converter backend** for .osim/.mot to JSON conversion

## 🎯 Research Applications

- **Algorithm development and quality control**: Enables rapid visual inspection of large datasets, allowing researchers to identify model failures or artifacts across many trials without manual GUI interaction.
- **Reproducible figures for publications**: Timelapse rendering allows dynamic motion to be represented in static, publication-quality figures, facilitating clear qualitative comparisons in print.
- **Education and clinical documentation**: Browser-based visualization removes installation barriers, enabling interactive teaching materials and standardized video generation for documenting patient movement and intervention outcomes.


## 🛠️ Development

### Prerequisites
- Node.js (v14+)
- Python 3.8+
- npm or yarn

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run serve

# Build for production
npm run build
```

### Python Package Development
```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest
```

## 📚 Documentation

- **Web Interface**: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)
- **Python Package**: [opencap-visualizer-pip](https://github.com/Seeeeeyo/opencap-visualizer-pip)
- **OpenSim Converter**: [opensim-to-visualizer-api](https://github.com/Seeeeeyo/opensim-to-visualizer-api)

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines and feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## 🙏 Acknowledgements

We acknowledge the contributions of the OpenCap development team and the broader biomechanics research community. This work builds upon the foundation of open-source biomechanics tools including OpenSim and the Three.js graphics library.

## 📞 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/Seeeeeyo/opencap-visualizer/issues)
- **Web App**: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)
- **Documentation**: Check the individual repository READMEs for detailed usage instructions
