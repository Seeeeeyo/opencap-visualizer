# Forces Visualization Test - UPDATED

## Testing the Enhanced Forces Visualization Feature

### Files Needed
1. `testData/mocap/LaiArnoldModified2017_poly_withArms_weldHand_scaled.osim` - OpenSim model
2. `testData/mocap/STS1.mot` - Motion data
3. `testData/mocap/STS1.trc` - Marker data
4. `testData/mocap/STS1_forces.mot` - Forces data

### How to Test

1. **Load the Animation Data First:**
   - Click "Import" button in the left sidebar
   - Select "OpenSim" option 
   - Upload both the .osim and .mot files from testData/mocap/
   - Wait for the model to load and animation to start playing

2. **Load the Forces Data:**
   - Click "Import Forces" button (green button with vector icon)
   - The dialog will show "Import Ground Reaction Forces"
   - Select which animation to associate forces with (if multiple loaded)
   - Select the `STS1_forces.mot` file
   - Adjust force scale (recommended: 0.005-0.01)
   - Choose arrow color (default green)
   - Click "Load Forces"

3. **Expected Results:**
   - ✅ Green arrows now appear AT THE SUBJECT'S FEET (not at fixed platforms)
   - ✅ Arrows move dynamically with the calcaneus (heel) bones during animation
   - ✅ **NEW: Traditional pointed arrow heads instead of cone shapes**
   - ✅ **NEW: Cylindrical shafts for better 3D appearance**
   - ✅ Arrow length represents ground reaction force magnitude
   - ✅ Arrow direction represents actual force direction in 3D space
   - ✅ Forces are only visible when force magnitude > 1N (during ground contact)
   - ✅ Sidebar shows "Associated with Animation X" information

### Arrow Style Improvements
The arrows now feature:
- **Pointed Arrow Heads**: Traditional tapered arrow tips that point to sharp tips
- **Cylindrical Shafts**: 3D cylindrical shafts instead of flat lines
- **Better Proportions**: Improved size ratio between head and shaft
- **Enhanced Lighting**: Arrow heads and shafts respond to scene lighting
- **Consistent Colors**: Both head and shaft use the same material color

### Force-to-Model Mapping
The system now correctly maps:
- **R platform** → `calcn_r` (right calcaneus/heel bone)
- **L platform** → `calcn_l` (left calcaneus/heel bone)
- **Force vectors** positioned at exact foot locations per frame

### Enhanced Features
- **Animation Association**: Forces are tied to specific animations
- **Real-time Positioning**: Arrows follow foot segments during movement
- **Intelligent Scaling**: Forces scale with magnitude but maintain direction
- **Automatic Foot Detection**: System finds foot segments in loaded models
- **Better UI**: Shows which animation forces are associated with

### Force Data Structure
The STS1_forces.mot file contains:
- `time` - time stamps matching animation
- `R_ground_force_vx/vy/vz` - Right foot force components
- `L_ground_force_vx/vy/vz` - Left foot force components
- System combines these into resultant force vectors

### Troubleshooting
- If dialog says "load animation first": Import .osim/.mot files before forces
- If no arrows appear: Check that foot segments (calcn_r, calcn_l) exist in model
- If arrows are static: Verify forces are associated with the correct animation
- If arrows are too small/large: Adjust force scale in sidebar controls
- If arrows look wrong: Check that both arrow head and shaft are visible and properly colored

### Technical Implementation
- Forces positioned using real foot segment translation data
- Arrow direction calculated from X/Y/Z force components  
- Magnitude threshold prevents tiny forces from cluttering display
- Animation offset properly applied to force positioning
- Real-time updates synchronized with animation frame rate
- **NEW: Custom arrow head geometry using CylinderGeometry with tapered design**
- **NEW: 3D cylindrical shafts with proper scaling and rotation** 