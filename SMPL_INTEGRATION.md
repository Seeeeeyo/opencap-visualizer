# SMPL Integration for OpenCap Visualizer

This document describes the SMPL (Skinned Multi-Person Linear Model) integration added to the OpenCap Visualizer.

## Overview

The SMPL integration provides a way to visualize and manipulate human body models using the SMPL framework within the OpenCap Visualizer. This allows users to:

- Load and display SMPL models (male, female, neutral)
- Adjust shape parameters (β) to modify body proportions
- Control pose parameters (θ) to animate the model
- Export/import SMPL parameters
- Integrate with existing OpenCap motion data

## Components

### 1. SMPLViewer Component (`src/components/ui/SMPLViewer.vue`)

A standalone Vue component that provides:
- 3D visualization of SMPL models using Three.js
- Interactive controls for shape and pose parameters
- Model selection (SMPL Male, Female, Neutral, SMPL-H variants)
- Animation controls (static, sequence, loop)
- Export functionality for parameters and meshes

### 2. SMPL Utilities (`src/util/SMPLUtils.js`)

Utility functions for:
- Converting between OpenCap and SMPL data formats
- Parameter validation
- Model loading and manipulation
- File import/export

### 3. Integration with Session.vue

The main Session component has been extended with:
- SMPL viewer toggle button
- SMPL viewer integration in the main interface
- Parameter synchronization with OpenCap data

## Features

### Model Support
- **SMPL Male**: Standard male body model
- **SMPL Female**: Standard female body model  
- **SMPL Neutral**: Gender-neutral body model
- **SMPL-H Male/Female**: Hand-inclusive variants (planned)

### Parameter Controls
- **Shape Parameters (β)**: 10 parameters controlling body proportions
- **Pose Parameters (θ)**: 72 parameters (24 joints × 3 axes) for pose control
- **Gender Selection**: Choose between male, female, neutral models

### Animation Modes
- **Static**: Fixed pose display
- **Sequence**: Play through pose sequence
- **Loop**: Continuous loop animation

### Export Options
- **Parameters**: Export SMPL parameters as JSON
- **Mesh**: Export current model state as OBJ file

## Usage

### Basic Usage
1. Click the "Show SMPL" button in the left sidebar
2. Select a model type (Male, Female, Neutral)
3. Adjust shape parameters using the sliders
4. Modify pose parameters using the joint controls
5. Use animation controls to play sequences

### Advanced Usage
1. Load OpenCap motion data first
2. Enable SMPL viewer
3. Use the sync functionality to convert OpenCap data to SMPL format
4. Export parameters for use in other applications

## File Structure

```
src/
├── components/ui/
│   └── SMPLViewer.vue          # Main SMPL viewer component
├── util/
│   └── SMPLUtils.js            # SMPL utility functions
└── components/pages/
    └── Session.vue             # Updated with SMPL integration

public/
└── models/
    ├── smpl/
    │   ├── male.obj            # SMPL male model
    │   ├── female.obj          # SMPL female model
    │   └── neutral.obj         # SMPL neutral model
    └── smplh/                  # SMPL-H models (planned)
```

## Technical Details

### SMPL Joint Hierarchy
The implementation uses the standard SMPL joint hierarchy with 24 joints:
1. Pelvis
2. Left Hip
3. Right Hip
4. Spine1
5. Left Knee
6. Right Knee
7. Spine2
8. Left Ankle
9. Right Ankle
10. Spine3
11. Left Foot
12. Right Foot
13. Neck
14. Left Collar
15. Right Collar
16. Head
17. Left Shoulder
18. Right Shoulder
19. Left Elbow
20. Right Elbow
21. Left Wrist
22. Right Wrist
23. Left Hand
24. Right Hand

### Parameter Format
- **Shape Parameters (β)**: Array of 10 float values, typically in range [-3, 3]
- **Pose Parameters (θ)**: Array of 72 float values (24 joints × 3 rotation axes), typically in range [-π, π]

### Data Conversion
The system provides conversion utilities between:
- OpenCap motion data format
- SMPL parameter format
- Three.js mesh format

## Future Enhancements

### Planned Features
1. **SMPL-H Support**: Full hand model integration
2. **Texture Support**: Skin texture mapping
3. **Physics Integration**: Realistic physics simulation
4. **Motion Capture Integration**: Direct SMPL fitting from video
5. **Batch Processing**: Process multiple frames simultaneously

### Advanced Features
1. **Differentiable Rendering**: For optimization tasks
2. **Neural Network Integration**: AI-powered parameter estimation
3. **Real-time Streaming**: Live motion capture to SMPL
4. **Multi-person Support**: Multiple SMPL models simultaneously

## Dependencies

- **Three.js**: 3D rendering and visualization
- **Vue.js**: Component framework
- **Vuetify**: UI components
- **SMPL Models**: Placeholder models included (replace with actual SMPL models)

## Installation

The SMPL integration is included in the main OpenCap Visualizer codebase. No additional installation is required beyond the standard dependencies.

## Configuration

### Model Paths
Update the model paths in `SMPLUtils.js` to point to your actual SMPL model files:

```javascript
export const SMPL_MODELS = {
  smpl_male: {
    path: '/path/to/your/smpl/male.obj',
    // ...
  }
}
```

### Parameter Ranges
Adjust parameter ranges in the SMPLViewer component:

```javascript
// Shape parameter range
:min="-3" :max="3" :step="0.1"

// Pose parameter range  
:min="-Math.PI" :max="Math.PI" :step="0.1"
```

## Troubleshooting

### Common Issues
1. **Model not loading**: Check file paths and ensure OBJ files are accessible
2. **Performance issues**: Reduce model complexity or disable shadows
3. **Parameter not updating**: Check console for JavaScript errors

### Debug Mode
Enable debug logging by setting:

```javascript
console.log('SMPL Debug:', parameters);
```

## Contributing

To contribute to the SMPL integration:

1. Follow the existing code style
2. Add appropriate tests for new features
3. Update documentation for any API changes
4. Ensure compatibility with existing OpenCap functionality

## References

- [SMPL Paper](https://files.is.tue.mpg.de/black/papers/SMPL2015.pdf)
- [SMPL-H Paper](https://files.is.tue.mpg.de/black/papers/SMPL+H2019.pdf)
- [Three.js Documentation](https://threejs.org/docs/)
- [Vue.js Documentation](https://vuejs.org/guide/) 