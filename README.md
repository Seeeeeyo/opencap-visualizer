# OpenCap Viewer

A web-based 3D viewer for OpenCap motion capture data with advanced visualization and recording capabilities.

## Demo

[Live website](https://opencap-viewer.onrender.com)

This demo shows:
- Side-by-side comparison of multiple animations
- Customizable scene appearance
- 3D model visualization with labels
- Smooth playback and transitions

## Features

- Load and visualize OpenCap JSON files in 3D
- Compare multiple animations simultaneously
- Adjustable offsets in X, Y, and Z directions
- Color-coded models with customizable colors
- Video recording with configurable quality
- High-resolution image capture
- Customizable scene appearance:
  - Background color selection
  - Ground color and texture options
  - Option to hide ground plane
- Playback speed control
- Interactive timeline
- Drag and drop file loading
- Sample files for quick testing

## Prerequisites

- Node.js (v14 or higher)
- Python 3.7+ (for automation scripts)
- Modern web browser (Chrome recommended)
- npm or yarn

## Installation

1. Install Node.js dependencies:
```bash
npm install
```

2. Create and activate a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Viewer

1. Start the development server:
```bash
npm run serve
```

2. The viewer will be available at `http://localhost:3000`

### Manual Usage

1. Open the viewer in your browser
2. Load your JSON files by:
   - Using the "Load JSON Files" button
   - Dragging and dropping files onto the viewer
   - Using the "Try with Sample Files" button
3. Use the controls to:
   - Adjust model positions using offset controls
   - Control playback using the timeline
   - Customize subject colors
   - Modify scene appearance (background and ground)
   - Capture high-resolution screenshots
   - Record videos

### Scene Customization

The viewer offers several options to customize the scene:

- **Background Color**: Choose from various colors to change the scene background
- **Ground Options**:
  - Toggle ground visibility
  - Switch between textured and solid color ground
  - Choose between checkerboard and grid patterns
  - Select from various ground colors

### Recording and Capturing

- **Video Recording**: Click the "Record" button to start recording the scene. Click "Stop Recording" to save the video.
- **Image Capture**: Click the "Capture Image" button to save a high-resolution screenshot of the current scene.

### Automated Recording

Use the Python script to automate the recording process:

```bash
python automation.py path/to/first.json path/to/second.json output_video.webm
```

Optional arguments:
- `--wait`: Adjust loading wait time (default: 5 seconds)
- `--loops`: Number of camera angle changes (default: 3)

Example:
```bash
python automation.py test1.json test2.json comparison.webm --wait 10 --loops 4
```

## File Format

The viewer expects OpenCap JSON files with the following structure:
```json
{
  "time": [...],
  "bodies": {
    "body_name": {
      "translation": [...],
      "rotation": [...],
      "attachedGeometries": [...]
    }
  }
}
```

## Troubleshooting

1. If videos or images don't download:
   - Check browser download permissions
   - Ensure the output directory is writable

2. If models don't appear:
   - Verify JSON file format
   - Check browser console for errors
   - Increase the wait time if using automation

3. If camera controls don't work:
   - Ensure the browser window is focused
   - Try refreshing the page

4. If colors or textures don't update:
   - Try toggling the option off and on again
   - Check browser console for errors

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
