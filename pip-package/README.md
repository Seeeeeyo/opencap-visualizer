# OpenCap Visualizer

Generate videos from OpenCap biomechanics data files with both command-line interface and Python API.

This tool uses the deployed [OpenCap Visualizer](https://opencap-visualizer.onrender.com/) to create videos from biomechanics data files (.json, .osim/.mot pairs) using headless browser automation.

## Features

- **Dual Interface**: Both command-line tool and Python API
- **No Local Setup Required**: Uses deployed web application by default
- **Multiple Data Formats**: Supports JSON files and OpenSim .osim/.mot pairs
- **Subject Comparison**: Generate videos with multiple subjects
- **Anatomical Camera Views**: Use biomechanics-friendly camera angles
- **Customizable**: Colors, zoom, centering, loops, and dimensions
- **Automatic 3D Geometry**: Loads realistic human models from cloud storage

## Installation

```bash
pip install opencap-visualizer
```

**Note**: After installation, you'll need to install browser dependencies:
```bash
playwright install chromium
```

## Command Line Usage

### Basic Examples

```bash
# Single subject
opencap-visualizer data.json -o output.mp4

# Multiple subjects comparison
opencap-visualizer subject1.json subject2.json -o comparison.mp4

# With custom settings
opencap-visualizer data.json --camera anterior --colors red --loops 2 -o front_view.mp4

# OpenSim files
opencap-visualizer model.osim motion.mot -o simulation.mp4
```

### Advanced Examples

```bash
# Multiple subjects with different colors
opencap-visualizer s1.json s2.json s3.json --colors red green blue --camera sagittal -o side_comparison.mp4

# High-resolution with custom zoom
opencap-visualizer data.json --width 3840 --height 2160 --zoom 0.8 --camera superior -o 4k_top_view.mp4

# Interactive mode for manual exploration
opencap-visualizer data.json --interactive --camera anterior
```

### Camera Views

#### Anatomical Views (Recommended)
- `anterior` / `frontal` / `coronal` - Front-facing view
- `posterior` - Back view  
- `sagittal` / `lateral` - Side profile view
- `superior` - Top-down view
- `inferior` - Bottom-up view

#### Technical Views
- `top`, `bottom`, `front`, `back`, `left`, `right`
- `isometric`, `default`
- Corner views: `frontTopRight`, `backBottomLeft`, etc.

### Command Line Options

```
positional arguments:
  FILE                  Data files (.json, or .osim/.mot pairs)

optional arguments:
  -o, --output PATH     Output video file (default: animation_video.mp4)
  --camera VIEW         Camera position (default: isometric)
  --colors COLOR...     Subject colors (hex or names: red, blue, #ff0000)
  --loops N             Animation loops to record (default: 1)
  --width PX            Video width (default: 1920)
  --height PX           Video height (default: 1080)
  --zoom FACTOR         Zoom factor (>1.0 = zoom out, default: 1.5)
  --no-center           Disable auto-centering on subjects
  --timeout SEC         Loading timeout in seconds (default: 120)
  --interactive         Open browser for manual exploration
  --vue-app-path PATH   Custom Vue app index.html path
  --dev-server-url URL  Custom Vue development server URL
  -v, --verbose         Enable verbose output
```

## Python API Usage

### Basic Examples

```python
import opencap_visualizer as ocv

# Simple usage
success = ocv.create_video("data.json", "output.mp4")
if success:
    print("Video generated successfully!")

# Multiple subjects with settings
success = ocv.create_video(
    ["subject1.json", "subject2.json"],
    "comparison.mp4", 
    camera="anterior",
    colors=["red", "blue"],
    loops=2,
    verbose=True
)
```

### Class-based Usage

```python
import opencap_visualizer as ocv

# Create visualizer instance
visualizer = ocv.OpenCapVisualizer(verbose=True)

# Generate video synchronously
success = visualizer.generate_video_sync(
    input_files=["subject1.json", "subject2.json"],
    output_path="comparison.mp4",
    camera="sagittal", 
    colors=["#ff0000", "#00ff00"],
    width=1920,
    height=1080,
    zoom=1.2
)

print(f"Success: {success}")
```

### Async Usage

```python
import asyncio
import opencap_visualizer as ocv

async def generate_videos():
    # Using convenience function
    success = await ocv.create_video_async(
        "data.json", 
        "output.mp4",
        camera="anterior",
        colors=["blue"]
    )
    
    # Using class
    visualizer = ocv.OpenCapVisualizer(verbose=True)
    success = await visualizer.generate_video(
        ["s1.json", "s2.json", "s3.json"],
        "triple_comparison.mp4",
        camera="posterior",
        colors=["red", "green", "blue"],
        center_subjects=True,
        zoom=1.5
    )
    
    return success

# Run async function
success = asyncio.run(generate_videos())
```

### API Reference

#### `OpenCapVisualizer` Class

```python
class OpenCapVisualizer:
    def __init__(self, verbose: bool = False)
    
    async def generate_video(
        self,
        input_files: Union[str, List[str]],
        output_path: str = "animation_video.mp4",
        *,
        vue_app_path: Optional[str] = None,
        dev_server_url: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        timeout_seconds: int = 120,
        loops: int = 1,
        camera: Optional[str] = None,
        center_subjects: bool = True,
        zoom: float = 1.5,
        colors: Optional[List[str]] = None,
        interactive: bool = False
    ) -> bool
    
    def generate_video_sync(self, ...) -> bool  # Synchronous wrapper
```

#### Convenience Functions

```python
async def create_video_async(input_files, output_path, **kwargs) -> bool
def create_video(input_files, output_path, **kwargs) -> bool
```

## Data Formats

### JSON Files
The tool accepts biomechanics JSON files with the following structure:
```json
{
  "Data": {
    "ModelScalingVars": "path/to/model.osim",
    "Results": "path/to/motion.mot",
    "FrameTimesOG": [0.0, 0.033, 0.066, ...]
  }
}
```

### OpenSim Files  
Alternatively, provide `.osim` (model) and `.mot` (motion) file pairs:
```bash
opencap-visualizer model.osim motion.mot -o output.mp4
```

## Dependencies

The tool automatically detects the best available option:

1. **Deployed Version** (Recommended): `https://opencap-visualizer.onrender.com/`
   - No local setup required
   - Always up-to-date
   - Requires internet connection

2. **Local Development Server**: `http://localhost:3000`
   - Start with `npm run serve` in the Vue.js project
   - Faster for development/testing

3. **Built Files**: Local `dist/index.html`
   - Build with `npm run build` in the Vue.js project
   - Works offline

## Configuration

### Custom Servers
```bash
# Use local development server
opencap-visualizer data.json --dev-server-url http://localhost:3000

# Use custom built files
opencap-visualizer data.json --vue-app-path /path/to/dist/index.html
```

### Environment Variables
```bash
# Set default development server
export OPENCAP_DEV_SERVER=http://localhost:3000
```

## Troubleshooting

### Browser Installation
If you get browser-related errors:
```bash
playwright install chromium
```

### Connection Issues
- Check internet connection for deployed version
- For local development: `npm run serve` in Vue project
- For built files: `npm run build` in Vue project

### File Format Issues
- Ensure JSON files contain valid biomechanics data structure
- For OpenSim files, provide both `.osim` and `.mot` files
- Check file paths are correct and accessible

### Video Generation Issues
- Increase timeout: `--timeout 300`
- Enable verbose mode: `--verbose` or `verbose=True`
- Try interactive mode: `--interactive`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see the source repository for guidelines.

## Support

For issues and questions:
- GitHub Issues: [https://github.com/utahmobl/opencap-visualizer/issues](https://github.com/utahmobl/opencap-visualizer/issues)
- Web App: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/) 