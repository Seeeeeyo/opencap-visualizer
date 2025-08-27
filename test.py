import opencap_visualizer as ocv

# Basic usage with JSON files (fully supported)
success = ocv.create_video("data.json", "output.mp4")

# OpenSim files (fully supported)
# success = ocv.create_video(
#     ["model.osim", "motion.mot"],
#     "opensim_video.mp4", 
#     camera="anterior"
# )

# Multiple file types (framework ready)
success = ocv.create_video(
    ["motion.json", "markers.trc", "forces.mot"],
    "combined.mp4",
    show_markers=True,
    show_forces=True
)