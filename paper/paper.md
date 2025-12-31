---
title: 'OpenCap Visualizer: A Web-Based Platform for Interactive Biomechanics Visualization and Automated Video Creation'
tags:
  - Python
  - JavaScript
  - Vue.js
  - Three.js
  - biomechanics
  - motion capture
  - visualization
  - OpenSim
  - human movement
authors:
  - name: Selim Gilon
    orcid: 0009-0007-9339-5660
    affiliation: 1
  - name: Scott Uhlrich
    orcid: 0000-0002-3113-367X
    affiliation: 1
affiliations:
 - name: University of Utah
   index: 1
date:  28 August 2025
bibliography: paper.bib
---

# Summary

Biomechanics research relies heavily on visualizing 3D movement data to validate models and interpret results. However, as datasets grow and processing pipelines migrate to the cloud, the traditional reliance on manual, desktop-based graphical user interfaces (GUIs) has become a bottleneck for efficiency and reproducibility. Current tools require significant manual "clicking" to load models, load the associated motion, configure scenes, and export media.

OpenCap Visualizer is a web-based platform and Python package designed to resolve these challenges by enabling both interactive 3D visualization and programmatic video generation. The software provides two primary interfaces: a browser-based viewer for real-time, shareable visualization, and a Python API for automated rendering. Built with Vue.js and Three.js, it supports standard biomechanics formats—including OpenSim models (.osim), kinematics (.mot, .json), markers (.trc), and force data (.mot). This architecture allows researchers to process, analyze, and render videos for large datasets programmatically, minimizing the need for human interaction during the visualization pipeline.

The platform is available at https://opencap-visualizer.onrender.com/.

# Statement of need

The volume of biomechanics data is expanding rapidly due to the rise of markerless motion capture and large-scale, multi-subject studies. Concurrently, data processing is shifting from local desktop computers to cloud-based environments (e.g., OpenCap, AddBiomech). While current visualization tools, such as the OpenSim GUI, are powerful, they are primarily designed for interactive, single-trial analysis on a local machine with a display.

This creates three specific challenges for modern biomechanics workflows:

1. **The "Clicking" Bottleneck in Quality Control:** Evaluating new algorithms or performing quality control on large datasets often requires visual inspection of hundreds of trials. Doing this via traditional GUIs requires manually loading models and motion files for every single trial—a process that is prohibitively time-consuming and prone to human error.
2. **Incompatibility with Headless Servers:** Modern processing pipelines often run on headless servers (machines without monitors). Traditional GUI-based visualizers cannot easily run in these environments, making it difficult to automatically generate visual outputs as part of a server-side pipeline.
3. **Reproducibility and Qualitative Comparison:** While quantitative error metrics are standard in publications, qualitative visual comparisons are equally critical for understanding model performance. Generating these comparisons—such as overlaying a predicted motion on top of ground truth data—usually requires manual screen recording. This makes it difficult to reproduce exact camera angles or lighting across different methods, subjects, or time points.

OpenCap Visualizer addresses these needs by providing a scriptable, platform-agnostic solution. It allows researchers to:

- **Automate Quality Control:** Use the Python API to batch-process and render videos for massive datasets without GUI interaction, allowing researchers to quickly scan for artifacts or errors.
- **Enable Server-Side Rendering:** Generate visualizations directly on headless servers, integrating visual feedback into cloud-based processing pipelines.
- **Create Reproducible Figures and Videos:** Programmatically define camera angles, colors, and subject overlays. This ensures that comparisons between algorithms or time points are visually consistent. It also supports the generation of "timelapse" composite images for static paper figures, allowing dynamic motion to be represented clearly in print.
- **Share 3D Data Instantly:** Replace heavy video files with lightweight URLs that allow collaborators to interactively rotate and inspect 3D data in any web browser.



The platform is built on top of the OpenCap software ecosystem [@opencap], providing native support for OpenCap's markerless motion capture data formats while maintaining full compatibility with traditional marker-based systems and OpenSim models (TODO CHECK OTHER MODELS)[@opensim]. This dual compatibility makes it valuable for the broader biomechanics community, bridging the gap between traditional motion capture workflows and emerging markerless technologies using cameras [@opencap] or IMUs [@opensense] [@opensenseRT], and ensuring seamless integration with both OpenCap and OpenSim research pipelines.

# Key Features

There are three ways to interact with this tool. 

## 1. Interactive Web-Based Visualization

The core visualization engine is built on Three.js, providing 3D rendering directly in web browsers. The web interface is accessible at https://opencap-visualizer.onrender.com/ and requires no installation or registration. Key features include:

- **3D rendering** of skeletal models with anatomically accurate geometry
- **Multi-subject comparison** with independent color coding and transparency controls (see Figure \ref{fig:multisubject})
- **Marker visualization** supporting standard motion capture marker sets (.trc file) (see Figure \ref{fig:markersforces})
- **Ground reaction forces visualization** using .mot file (see Figure \ref{fig:markersforces})
- **Video synchronisation** with skeleton to enable simultaneous viewing of original footage and motion data 
- **Timeline controls** with adjustable playback speed and frame-by-frame navigation
- **Recording capabilities** for capturing custom video segments directly from the web interface
- **Image capture** for generating high-resolution screenshots at specific time points
- **Timelapse capture** to capture sequential motion frames, enabling the representation of dynamic movement within a single static figure (see Figure \ref{fig:timelapse}).
- **Color controls** for customizing background, ground plane, skeletal models, and markers.

## 2. Live Streaming of Kinematics

Beyond playing back pre-computed motion files, OpenCap Visualizer supports live streaming of kinematics from external analysis pipelines. A lightweight Python WebSocket server streams OpenSim-based kinematics frame-by-frame to the browser using the same body-wise transform format as offline visualizations. The viewer exposes a "live mode" that:

- **Subscribes to a local WebSocket endpoint** (e.g., `ws://localhost:8765`) and incrementally updates body transforms as new frames arrive.
- **Downsamples high-frequency data** (e.g., 100 Hz motion capture) to ~30 Hz for smooth browser rendering while preserving the recorded timing.
- **Handles multiple concurrent subjects**, allowing two kinematic streams (e.g., experimental vs. reference) to be visualized in real time with distinct default colors and offsets.
- **Supports normal playback controls** (play/pause, looping) while buffering incoming frames so that users can pause, inspect a pose, and resume from the most recent streamed frame.

This live streaming capability enables workflows such as monitoring ongoing inverse kinematics computations, validating OpenSim models during data collection, or comparing real-time kinematics against an offline reference (e.g OpenSenseRT [@opensenseRT]).

## 3. Python API for Automated Video Creation

This tool can also be accessed through python code. The `opencap-visualizer` (https://pypi.org/project/opencap-visualizer) Python package provides programmatic access to video generation functionality:

The package can be installed via pip:
```
pip install opencap-visualizer
```

The API supports extensive customization options including camera angles, subject colors, transparency levels, and animation loops, enabling integration into automated analysis pipelines.

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
    "output_video.mp4",
    colors=["red", "blue"],
    camera="sagittal"
)


# OpenSim files 
success = ocv.create_video(
    ["model.osim", "motion.mot", "markers.trc", "forces.mot"],
    "output_video.mp4",
)
```

## Format Compatibility

The software supports multiple data formats common in biomechanics research:

- **OpenSim models** (.osim) 
- **OpenSim motion data** (.mot)
- **JSON-based motion data** from OpenCap and other sources
- **TRC marker files** for marker trajectory data
- **GRF files** (.mot) for ground reaction forces 
- **SMPL** motion sequences (.pkl) 


# Implementation

OpenCap Visualizer is implemented as a modern web application with a complementary Python package:

## Frontend Architecture

- **Vue.js** for reactive user interface components
- **Three.js** for 3D graphics rendering and animation
- **Vuetify** for Material Design components

## Backend Services

**Deployed, cloud based:**

- **Node.js sharing backend** for URL-based data sharing
- **Python OpenSim file converter backend** to convert .osim and .mot into .json

**Using the deployed web-app but requiring some code locally:**

- **Python WebSocket streamer** for real-time delivery of kinematics to the browser in live mode, using a simple JSON protocol compatible with the offline visualizer format
- **Python headless video generation** via pip package

# Applications

OpenCap Visualizer is designed to support high-throughput research and modern biomechanics workflows where traditional manual visualization is a bottleneck:

- **Algorithm Development and Quality Control**: The platform is optimized for researchers developing new biomechanics models or motion-capture algorithms, enabling the rapid visual inspection of hundreds of trials. This allows researchers to identify edge-case failures or model artifacts across diverse subjects without manual GUI interaction.

- **Communicating Research via Static Figures**: The timelapse functionality addresses the difficulty of representing motion in print. Researchers can now create publication-quality figures that clearly illustrate movement progression (e.g., a gait cycle or a specific rehabilitation exercise) in an image format suitable for publications.


- **Educational Outreach and Clinical Documentation**: By removing the barrier of software installation, the platform makes complex biomechanics data accessible to students and clinicians. Educators can create interactive demonstrations accessible via any browser, while clinicians can generate standardized videos to document patient progress or intervention outcomes with minimal overhead.


# Figures

Figure \ref{fig:multisubject} shows a multi-subject comparison on the interface, demonstrating the comparison between OpenCap monocular motion capture and traditional marker-based motion capture data in this example.
Figure \ref{fig:markersforces} demonstrates the comprehensive visualization capabilities including traditional motion capture markers and ground reaction forces. 
Figure \ref{fig:timelapse} showcases the timelapse functionality, which enables researchers to create accelerated visualizations of movement patterns using skeleton trajectory traces.

\begin{figure}
\centering
\includegraphics[width=\textwidth]{demo.png}
\caption{Example visualization of the web interface with multiple subjects.}
\label{fig:multisubject}
\end{figure}

\begin{figure}
\centering
\includegraphics[width=\textwidth]{demo2.png}
\caption{Example visualization of the web interface with markers and forces.}
\label{fig:markersforces}
\end{figure}

\begin{figure}
\centering
\includegraphics[width=\textwidth]{sample.png}
\caption{Example timelapse screenshot generated on the visualizer.}
\label{fig:timelapse}
\end{figure}


# Comparison with Related Work

OpenCap Visualizer distinguishes itself from existing biomechanics visualization tools through its unique combination of web-based accessibility and programmatic video generation:

- **OpenSim GUI** [@opensim] provides comprehensive modeling capabilities. However, it is primarily designed as a GUI for manual, trial-by-trial inspection. Visualizing data requires many human computer interactions (loading models, loading motion files, adjusting camera views), which becomes a bottleneck when performing quality control on hundreds of trials. Furthermore, these tools typically lack a native Python API for headless video rendering, making them difficult to integrate into automated cloud pipelines.
- **Visual3D** provides commercial visualization but lacks web-based accessibility and open-source flexibility.
- **MuJoCo** [@mujoco] offers a visualizer but requires coding capabilities.  

OpenCap Visualizer's browser-based approach eliminates installation barriers while its Python API enables seamless integration into research workflows, making it uniquely positioned to serve both interactive exploration and automated analysis needs.

# Acknowledgements

This work builds upon the foundation of open-source biomechanics tools including OpenSim and OpenCap. 

# References 
