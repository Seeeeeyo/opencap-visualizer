# OpenCap Visualizer CLI

A command-line tool for generating videos from biomechanics data files using the [OpenCap Visualizer](https://opencap-visualizer.onrender.com/) web application.

## 🚀 Features

- **Generate videos** from OpenCap JSON files, .osim/.mot pairs, and more
- **Multiple file support** - Compare subjects side-by-side
- **Anatomical camera views** - anterior, posterior, sagittal, superior, etc.
- **Custom colors** - Set subject colors with hex codes or names
- **Interactive mode** - Open browser for manual exploration
- **No local setup** - Uses deployed web app by default
- **Flexible output** - MP4 and WebM video formats

## 📦 Installation

```bash
pip install opencap-visualizer-cli
```

### Prerequisites

The tool requires a browser for rendering. Install Playwright browsers:

```bash
playwright install chromium
```

### Optional: FFmpeg for MP4 conversion

For best MP4 compatibility, install FFmpeg:

```bash
# macOS (via Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

## 🎯 Quick Start

### Basic Usage

```bash
# Generate video from single subject (quiet by default)
opencap-visualizer data.json -o animation.mp4
# Output: /path/to/your/workspace/animation.mp4

# Enable verbose logging
opencap-visualizer data.json -o animation.mp4 --verbose

# Compare multiple subjects
opencap-visualizer subject1.json subject2.json -o comparison.mp4

# Use .osim/.mot files
opencap-visualizer model.osim motion.mot -o simulation.mp4
```

### Interactive Mode

```bash
# Open browser for manual exploration (quiet by default)
opencap-visualizer data.json --interactive --camera anterior --colors red

# Interactive mode with verbose logging
opencap-visualizer data.json --interactive --camera anterior --colors red --verbose
```

## 📖 Usage Examples

### Camera Views
```bash
# Anatomical views
opencap-visualizer data.json --camera anterior -o front_view.mp4    # Front-facing
opencap-visualizer data.json --camera posterior -o back_view.mp4    # Back view  
opencap-visualizer data.json --camera sagittal -o side_view.mp4     # Side profile
opencap-visualizer data.json --camera superior -o top_view.mp4      # Top-down

# Technical views
opencap-visualizer data.json --camera isometric -o iso_view.mp4     # 3D perspective
```

### Subject Colors
```bash
# Color names
opencap-visualizer s1.json s2.json --colors red blue -o colored.mp4

# Hex colors
opencap-visualizer s1.json s2.json --colors "#ff0000" "#0000ff" -o custom.mp4

# Mixed colors (will cycle if fewer colors than subjects)
opencap-visualizer s1.json s2.json s3.json --colors red green -o mixed.mp4
```

### Animation Control
```bash
# Multiple loops
opencap-visualizer data.json --loops 3 -o triple_loop.mp4

# Custom zoom (1.0 = default, >1.0 = zoom out, <1.0 = zoom in)
opencap-visualizer data.json --zoom 2.0 -o zoomed_out.mp4

# Disable auto-centering
opencap-visualizer data.json --no-center -o no_center.mp4
```

### Advanced Examples
```bash
# Complete customization
opencap-visualizer subject1.json subject2.json \
  --camera anterior \
  --colors red blue \
  --loops 2 \
  --zoom 1.5 \
  --width 1920 \
  --height 1080 \
  -o custom_comparison.mp4

# OpenSim workflow
opencap-visualizer model.osim motion.mot \
  --camera sagittal \
  --colors green \
  --loops 1 \
  -o opensim_analysis.mp4
```

## 🛠️ Command-Line Options

### Input Files
- **JSON files**: OpenCap format data
- **.osim/.mot pairs**: OpenSim model and motion files
- **Mixed inputs**: Combine JSON and .osim/.mot in same command

### Camera Options
| Option | Description |
|--------|-------------|
| `--camera anterior` | Front-facing view (person facing camera) |
| `--camera posterior` | Back view (person's back to camera) |
| `--camera sagittal/lateral` | Side profile view |
| `--camera superior` | Top-down view |
| `--camera inferior` | Bottom-up view |
| `--camera isometric` | 3D perspective view |

### Visual Options
| Option | Description |
|--------|-------------|
| `--colors red blue` | Set subject colors |
| `--zoom 1.5` | Camera zoom factor |
| `--no-center` | Disable auto-centering |
| `--loops 3` | Number of animation loops |

### Output Options
| Option | Description |
|--------|-------------|
| `-o filename.mp4` | Output video file |
| `--width 1920` | Video width in pixels |
| `--height 1080` | Video height in pixels |

### Advanced Options
| Option | Description |
|--------|-------------|
| `--interactive` | Open browser for manual exploration |
| `-v`, `--verbose` | Enable verbose output, including script progress and browser console logs. |
| `--timeout 120` | Timeout in seconds |
| `--dev-server-url URL` | Use custom visualizer URL |

## 🎨 Available Colors

### Color Names
- **Basic**: red, green, blue, yellow, cyan, magenta, orange, purple, white, gray
- **Light variants**: lightred, lightgreen, lightblue, lightpink, lightcyan, lightorange

### Hex Colors
Use standard hex format: `#ff0000`, `#00ff00`, `#0000ff`, etc.

## 🌐 How It Works

1. **Connects** to deployed OpenCap Visualizer at https://opencap-visualizer.onrender.com/
2. **Uploads** your data files to the web app
3. **Configures** camera, colors, and animation settings
4. **Records** the 3D visualization as video
5. **Downloads** the final video file

## 🔧 Troubleshooting

### Common Issues

**Too much log output:**
By default, the CLI is quiet. If you are seeing too much, ensure you haven't added the `--verbose` flag.

```bash
# Verbose mode:
opencap-visualizer data.json -o video.mp4 --verbose
```

**Browser installation:**
```bash
# If Playwright browsers aren't installed
playwright install chromium
```

**Network issues:**
```bash
# Use local development server
opencap-visualizer data.json --dev-server-url http://localhost:3000
```

**Video format issues:**
```bash
# Install FFmpeg for better MP4 support
brew install ffmpeg  # macOS
```

### Error Messages

- **"Could not find Vue app"**: Check internet connection or install FFmpeg
- **"No valid input files"**: Ensure JSON files are valid or .osim/.mot files are paired
- **"Timeout waiting"**: Increase timeout with `--timeout 300`

## 📄 File Format Support

### JSON Files
Standard OpenCap format with:
- `time` array
- `bodies` object with geometry data
- Motion data for each frame

### OpenSim Files
- **Model files**: `.osim` format
- **Motion files**: `.mot` format
- Must be provided as pairs (one .osim + one .mot)

## 🤝 Contributing

Issues and pull requests welcome! Visit the [GitHub repository](https://github.com/utahmobl/opencap-visualizer-cli) for more information.

## 📜 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [OpenCap Project](https://www.opencap.ai/)
- Built on [Three.js](https://threejs.org/) and [Vue.js](https://vuejs.org/) 