# OpenCap Viewer

A web-based 3D viewer for OpenCap motion capture data with automated video recording capabilities.

## Demo

[Watch Demo Video](./demo/subj2.webm)

This demo shows:
- Side-by-side comparison of two animations
- Automatic camera angle changes
- 3D model visualization with labels
- Smooth playback and transitions

## Features

- Load and visualize OpenCap JSON files in 3D
- Compare two animations side by side
- Adjustable offsets in X, Y, and Z directions
- Color-coded models with labels
- Video recording with multiple camera angles
- Playback speed control
- Interactive timeline

## Prerequisites

- Node.js (v14 or higher)
- Python 3.7+
- Google Chrome browser
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

2. The viewer will be available at `http://localhost:8080`

### Manual Usage

1. Open the viewer in your browser
2. Load your JSON files
3. Use the controls to:
   - Adjust model positions using offset controls
   - Control playback using the timeline
   - Adjust playback speed
   - Record videos using the record button

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

### Camera Angles

The automated recording cycles through these views:
1. Front view (0°)
2. Side view (90°)
3. Back view (180°)
4. High angle diagonal view (45°)

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

1. If the video doesn't download:
   - Check Chrome's download permissions
   - Ensure the output directory is writable

2. If models don't appear:
   - Verify JSON file format
   - Check browser console for errors
   - Increase the wait time using `--wait`

3. If camera controls don't work:
   - Ensure the browser window is focused
   - Try refreshing the page

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
