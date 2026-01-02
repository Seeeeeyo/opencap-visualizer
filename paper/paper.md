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
  - name: Department of Mechanical Engineering, University of Utah, Salt Lake City, UT, USA
    index: 1
date: 2 January 2026
bibliography: paper.bib
---

# Summary

Biomechanics research relies on visualizing 3D movement data to interpret and validate results, but traditional desktop-based graphical user interfaces (GUIs) have become a bottleneck for efficiency and reproducibility, requiring extensive manual interaction to load models, motions, configure scenes, and export media. To resolve these challenges, OpenCap Visualizer is a web-based platform and Python package that enables both interactive 3D visualization and fully programmatic video generation.

The software provides two primary interfaces: a browser-based viewer for real-time, shareable visualization, and a Python API for automated rendering. Built with Vue.js and Three.js, it supports standard biomechanics formats—including OpenSim models (.osim), kinematics (.mot, .json), markers (.trc), and force data (.mot)—allowing researchers to process, analyze, render, and share biomechanics videos with minimal human intervention.

The platform is available at TODO. 

# Statement of need

Biomechanics datasets are rapidly growing due to markerless motion capture and large-scale studies, while data processing is increasingly performed on cloud-based servers such as OpenCap [@opencap] or AddBiomechanics [@AddBiomechanics]. Existing visualization tools, such as the OpenSim GUI, are optimized for interactive, single-trial analysis on local machines and do not scale well to modern, automated workflows.

As a result, quality control and qualitative comparison across large datasets are time-consuming, error-prone, and difficult to reproduce, as generating consistent visual outputs (e.g., predicted–reference motion overlays) requires extensive manual GUI interaction.

OpenCap Visualizer addresses these challenges by providing a scriptable, platform-agnostic visualization system that supports both interactive web-based viewing and fully automated, server-side rendering. Through its Python API, researchers can batch-generate reproducible videos and figures with programmatically defined camera settings, overlays, and styling, enabling scalable quality control and consistent qualitative comparison without manual intervention. Interactive browser-based visualization further allows collaborators to inspect 3D data directly via lightweight URLs.

The platform builds on the OpenCap ecosystem [@opencap] while remaining compatible with OpenSim models and standard biomechanics data formats [@opensim], making it applicable to both traditional marker-based workflows and emerging markerless approaches using cameras [@opencap] or IMUs [@opensense; @opensenseRT].

# Key Features

OpenCap Visualizer supports three complementary modes of interaction: browser-based visualization, live streaming, and automated rendering via Python. It supports common biomechanics data formats, including OpenSim models (.osim), motion and force files (.mot), marker trajectories (.trc), JSON-based kinematics (e.g., OpenCap), and SMPL motion sequences (.pkl).

## 1. Interactive Web-Based Visualization

OpenCap Visualizer provides installation-free 3D visualization directly in the browser using Three.js (TODO). It supports anatomically accurate skeletal rendering, multi-subject overlays, markers (.trc), ground reaction forces (.mot), and synchronized video playback. Users can interactively control playback, camera views, colors, and transparency, and export high-resolution images, videos, or timelapse composites for figures and presentations.

## 2. Live Streaming of Kinematics

In addition to offline playback, the visualizer supports real-time streaming of OpenSim-based kinematics via a lightweight Python WebSocket server. Incoming frames are incrementally rendered in the browser, with automatic downsampling for smooth visualization. Multiple concurrent streams (e.g., predicted vs. reference motion) can be displayed simultaneously with standard playback controls. This enables real-time monitoring of inverse kinematics, model validation during data collection, and comparison against live reference pipelines such as OpenSenseRT [@opensenseRT].

## 3. Python API for Automated Video Creation

The opencap-visualizer Python package (https://pypi.org/project/opencap-visualizer) enables fully programmatic video generation for integration into automated pipelines and headless servers. Users can batch-render videos with configurable camera views, subject overlays, colors, and looping behavior from standard OpenCap and OpenSim inputs, eliminating the need for manual GUI interaction.

Example usage:
```python
import opencap_visualizer as ocv

ocv.create_video("subject.json", "output.mp4", camera="anterior")
ocv.create_video(["subj1.json", "subj2.json"], "compare.mp4", colors=["red","blue"])
ocv.create_video(["model.osim","motion.mot","markers.trc","forces.mot"], "opensim.mp4")
```

# Implementation

OpenCap Visualizer consists of a web-based frontend and a complementary Python package. The frontend is built with Vue.js and Three.js for interactive 3D visualization, with Vuetify providing UI components. The deployed web application includes cloud-based services for URL-based sharing and server-side conversion of OpenSim models and motion files into a browser-compatible JSON format.

For local and automated workflows, a lightweight Python package enables headless video generation for batch rendering, while a separate local Python script supports real-time kinematics streaming via WebSockets.


# Applications

OpenCap Visualizer supports high-throughput biomechanics workflows where manual, GUI-based visualization limits scalability and reproducibility.

- **Algorithm development and quality control**: Enables rapid visual inspection of large datasets, allowing researchers to identify model failures or artifacts across many trials without manual GUI interaction.

- **Reproducible figures for publications**: Timelapse rendering allows dynamic motion to be represented in static, publication-quality figures, facilitating clear qualitative comparisons in print.


- **Education and clinical documentation**: Browser-based visualization removes installation barriers, enabling interactive teaching materials and standardized video generation for documenting patient movement and intervention outcomes.


# Figures

Figure \ref{fig:multisubject} illustrates multi-subject comparison, including overlay of OpenCap monocular and marker-based motion capture. Figure \ref{fig:markersforces} shows visualization of marker trajectories and ground reaction forces. Figure \ref{fig:timelapse} presents the timelapse rendering used to summarize dynamic movement patterns in static figures.

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


# References 
