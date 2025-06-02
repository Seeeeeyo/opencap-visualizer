# OpenCap Visualizer CLI

A command-line tool for generating videos from OpenCap biomechanics JSON files. Convert your motion capture data into high-quality MP4 videos without manually opening a browser.

## Features

- **Headless video generation**: Create videos programmatically from JSON files
- **Multiple camera angles**: Supports anatomical views (anterior, posterior, sagittal, etc.)
- **Batch processing**: Process multiple subjects simultaneously
- **Customizable settings**: Control loops, zoom, centering, and camera positioning
- **High-quality output**: Generates MP4 videos ready for sharing or analysis

## Installation

```bash
pip install opencap-visualizer-cli
```

### Prerequisites

The tool requires:
- Python 3.8+
- Playwright browsers (automatically installed)
- FFmpeg (for video conversion)

After installation, run the setup command to install required browsers:
```bash
playwright install chromium
```

## Quick Start

Generate a video from a JSON file:
```bash
opencap-visualizer data.json --output my_animation.mp4
```

Generate with specific camera angle and multiple loops:
```bash
opencap-visualizer data.json --output my_animation.mp4 --camera anterior --loops 3
```

Process multiple subjects:
```bash
opencap-visualizer subject1.json subject2.json subject3.json --output multi_subject.mp4
```

## Usage

```bash
opencap-visualizer [JSON_FILES...] [OPTIONS]
```

### Arguments

- `JSON_FILES`: One or more OpenCap JSON files to visualize

### Options

- `--output, -o`: Output video filename (default: animation.mp4)
- `--camera`: Camera view angle (default: right)
  - Anatomical terms: `anterior`, `posterior`, `sagittal`, `superior`, `inferior`, `frontal`, `coronal`
  - Directional terms: `front`, `back`, `left`, `right`, `top`, `bottom`
- `--loops`: Number of animation loops (default: 2)
- `--zoom`: Camera zoom factor (default: 1.5 for slight zoom out)
- `--no-center`: Disable automatic centering of subjects
- `--width`: Video width in pixels (default: 1920)
- `--height`: Video height in pixels (default: 1080)

### Camera Views

The tool supports various anatomical viewing angles:

- **`anterior` / `front`**: Front-facing view of the subject
- **`posterior` / `back`**: Back view of the subject  
- **`sagittal` / `left` / `right`**: Side profile views
- **`superior` / `top`**: Top-down view
- **`inferior` / `bottom`**: Bottom-up view
- **`frontal` / `coronal`**: Coronal plane views

### Examples

**Basic usage:**
```bash
opencap-visualizer walking_data.json
```

**Custom output with back view:**
```bash
opencap-visualizer squat_data.json --output squat_back_view.mp4 --camera posterior
```

**Multiple subjects with specific settings:**
```bash
opencap-visualizer person1.json person2.json \
  --output comparison.mp4 \
  --camera sagittal \
  --loops 4 \
  --zoom 2.0
```

**High-resolution video:**
```bash
opencap-visualizer data.json \
  --output hd_video.mp4 \
  --width 3840 \
  --height 2160 \
  --camera anterior
```

## JSON File Format

The tool expects OpenCap JSON files with the following structure:

```json
{
  "time": [0.0, 0.033, 0.066, ...],
  "bodies": {
    "pelvis": {
      "translation": [[x1, y1, z1], [x2, y2, z2], ...],
      "rotation": [[rx1, ry1, rz1], [rx2, ry2, rz2], ...],
      "attachedGeometries": [...]
    },
    "femur_r": {
      "translation": [...],
      "rotation": [...],
      "attachedGeometries": [...]
    }
  }
}
```

## Troubleshooting

**Browser installation issues:**
```bash
playwright install chromium --force
```

**FFmpeg not found:**
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/

**Large file processing:**
For large JSON files or long animations, increase timeout:
```bash
# The tool automatically adjusts timeouts based on file size
opencap-visualizer large_file.json --loops 1  # Reduce loops for faster processing
```

## Web Interface

This CLI tool is built on top of the OpenCap Visualizer web application. You can also use the interactive web interface at:
https://opencap-visualizer.onrender.com/

## Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Full documentation available in the repository
- **Community**: Join discussions about OpenCap and biomechanics visualization


## License

Publish pip package
```
rm -rf dist/ build/ *.egg-info/
python setup.py sdist bdist_wheel
twine upload dist/*
```


## License

MIT License - see LICENSE.md for details.

---

**Part of the OpenCap ecosystem** - Tools for democratizing human movement analysis.


