# Force Loading Implementation for OpenCap Visualizer

## Overview

This implementation adds comprehensive support for loading and visualizing ground reaction forces from `.mot` files in the OpenCap Visualizer. The system automatically detects force files, maps different column naming conventions, and visualizes forces as arrows positioned at the subject's feet.

## Features

### 1. Automatic Force File Detection
- Detects `.mot` files containing force data based on:
  - Filename containing "force"
  - Column headers containing force-related keywords
- Supports multiple naming conventions for force columns

### 2. Column Mapping System
The system automatically maps different column naming conventions to a standard format:

**Supported Formats:**
- Standard OpenSim: `R_ground_force_vx`, `L_ground_force_vx`
- Alternative: `ground_force_right_vx`, `ground_force_left_vx`
- Extended: `right_ground_force_vx`, `left_ground_force_vx`

**Mapped Columns:**
- Force vectors: `vx`, `vy`, `vz` (force magnitude and direction)
- Center of pressure: `px`, `py`, `pz` (force application point)

### 3. Multiple Loading Methods
- **Drag & Drop**: Drop `.mot` force files directly into the viewer
- **Import Button**: Use the Import dialog and select "Forces"
- **Sample Data**: Click "Load Sample Forces" button for testing
- **File Input**: Use the forces file input in the forces dialog

### 4. Automatic Association
- Forces are automatically associated with animations
- If no animations exist, creates a standalone force visualization
- Replaces existing forces if all animations already have force data

### 5. Visual Representation
- Forces displayed as 3D arrows at the feet
- Arrow direction shows force direction
- Arrow length represents force magnitude (scaled for visibility)
- Arrows positioned at center of pressure (COP) or foot position
- Color-coded per animation with customizable colors

## Implementation Details

### Key Methods Added/Modified

1. **`mapForceColumns(forceData, columnHeaders)`**
   - Maps different column naming conventions to standard format
   - Supports multiple naming patterns for compatibility

2. **`parseForcesData(content)`**
   - Enhanced to use column mapping
   - Stores both original and mapped data

3. **`loadSampleForceFile()`**
   - Loads the sample force file for testing
   - Fetches from `/sample_grf_resultant.mot`

4. **`processForceFile(forceFile)`**
   - Handles force file processing and association
   - Supports both standalone and animation-associated forces

5. **`isForceMotFile(file)`**
   - Enhanced detection with expanded keywords
   - Supports more force-related column patterns

### File Structure

```
opencap-visualizer/
├── public/
│   └── sample_grf_resultant.mot    # Sample force file for testing
├── src/components/pages/
│   └── Session.vue                 # Main implementation
├── test_force_loading.html         # Test page for verification
└── FORCE_LOADING_IMPLEMENTATION.md # This documentation
```

## Usage Instructions

### For Users

1. **Load Sample Forces:**
   - Click "Load Sample Forces" button in the getting started section
   - This loads the provided sample force file for testing

2. **Load Custom Force Files:**
   - Drag & drop `.mot` force files into the viewer
   - Or use Import button → Forces → Select file
   - Or use the forces dialog in the right panel

3. **Visualize Forces:**
   - Forces appear as colored arrows at the feet
   - Use the force controls to adjust visibility, color, and scale
   - Forces animate with the motion data

### For Developers

1. **Adding New Column Formats:**
   - Extend the `columnMappings` object in `mapForceColumns()`
   - Add new patterns to the `forceKeywords` array in `isForceMotFile()`

2. **Customizing Force Visualization:**
   - Modify `createForceArrows()` for different visual styles
   - Adjust `updateForceArrows()` for different positioning logic

3. **Testing:**
   - Use `test_force_loading.html` to verify functionality
   - Check browser console for detailed logging

## Sample Force File Format

The sample file `sample_grf_resultant.mot` contains:

```
version=1
nRows=23
nColumns=19
inDegrees=yes
endheader
time	ground_force_right_vx	ground_force_right_vy	ground_force_right_vz	ground_force_right_px	ground_force_right_py	ground_force_right_pz	ground_torque_right_x	ground_torque_right_y	ground_torque_right_z	ground_force_left_vx	ground_force_left_vy	ground_force_left_vz	ground_force_left_px	ground_force_left_py	ground_force_left_pz	ground_torque_left_x	ground_torque_left_y	ground_torque_left_z
```

## Technical Notes

### Column Mapping Logic
The system maps columns using a priority-based approach:
1. Check for standard OpenSim format first
2. Fall back to alternative naming conventions
3. Log mapping results for debugging

### Force Visualization
- Forces are rendered as 3D arrows using Three.js
- Arrow head and shaft are separate geometries for better control
- Forces are scaled for visibility (configurable via `forceScale`)
- Arrows are positioned at the center of pressure or foot position

### Performance Considerations
- Force data is loaded once and cached
- Arrow updates are optimized for real-time playback
- Memory is properly managed with disposal of geometries and materials

## Troubleshooting

### Common Issues

1. **Forces not appearing:**
   - Check if force file has correct column names
   - Verify animation has foot segments (`calcn_r`, `calcn_l`)
   - Check browser console for error messages

2. **Wrong force positioning:**
   - Verify COP data exists in force file
   - Check animation offset settings
   - Ensure coordinate systems match

3. **Column mapping issues:**
   - Check console logs for mapping results
   - Verify column names in force file
   - Add new patterns to mapping if needed

### Debug Information
The implementation includes extensive console logging:
- Column mapping results
- Force detection decisions
- Arrow creation and updates
- Error messages and warnings

## Future Enhancements

Potential improvements for future versions:
1. Support for more force file formats (C3D, etc.)
2. Advanced force visualization options
3. Force analysis tools and plots
4. Export force data functionality
5. Support for multiple force platforms
6. Real-time force data streaming
