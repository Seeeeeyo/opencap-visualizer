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
    affiliation: 1,2
affiliations:
  - name: Department of Mechanical Engineering, University of Utah, Salt Lake City, UT, USA
    index: 1
  - name: Department of Orthopaedic Surgery, University of Utah, Salt Lake City, UT, USA
    index: 2
date: 30 March 2026
bibliography: paper.bib
---

# Summary

Biomechanics research relies on visualizing 3D movement data to interpret and validate results, but traditional desktop-based graphical user interfaces (GUIs) have become a bottleneck as the scale of biomechanics datasets grows and processing increasingly moves to cloud-based servers. Current GUIs require extensive manual interaction to load models, motions, configure scenes, and export media. To resolve these challenges, we created OpenCap Visualizer, a web-based platform and Python package that enables both interactive 3D visualization, real-time streaming, and programmatic video generation.

The software provides three primary interfaces: a browser-based viewer for shareable visualization, a WebSocket interface for real-time streaming, and a Python API for automated rendering. Built with Vue.js and Three.js, it supports standard biomechanics formats—including OpenSim models (.osim), kinematics (.mot, .json), markers (.trc), and force data (.mot)—allowing researchers to process, analyze, render, and share biomechanics videos with minimal human intervention.


The platform is available at [https://www.visualizer.opencap.ai](https://www.visualizer.opencap.ai).

# Statement of Need

Biomechanics datasets are growing by orders of magnitude due to recent advances in mobile sensing, including wearables and markerless motion capture  [@Boswell; @AddBiomechanics; @Duane; @opencap; @opencap-monocular], and data processing is increasingly performed on cloud-based servers such as OpenCap [@opencap] or AddBiomechanics [@AddBiomechanics]. Existing visualization tools, such as the OpenSim GUI, are optimized for interactive, single-trial analysis on local machines and do not scale well to automated workflows required for analyzing large datasets. For example, we recently conducted a study using OpenCap with 129 individuals performing 10 activities; manually loading 1,290 trials for quality control in a GUI is infeasible. Similarly, comparing the effects of different algorithms on a motion is common in biomechanics research and currently requires extensive GUI interaction. The biomechanics community lacks a flexible tool for programmatic, real-time, and sharable visualization of movement data.

OpenCap Visualizer addresses these challenges by providing a scriptable, platform-agnostic visualization system that supports both interactive web-based viewing and fully automated, server-side rendering. Through its Python API, researchers can batch-generate reproducible videos and figures with programmatically defined camera settings, overlays, and styling, enabling scalable quality control and consistent qualitative comparison without manual intervention. Interactive browser-based visualization further allows collaborators to inspect 3D data directly via lightweight URLs.

The platform builds on the OpenCap ecosystem [@opencap] and is compatible with OpenSim models and standard biomechanics data formats [@opensim], making it applicable to both traditional marker-based workflows and emerging markerless approaches using cameras [@opencap; @opencap-monocular] or IMUs [@opensense; @opensenseRT].


# Key Features

OpenCap Visualizer supports three complementary modes of interaction: browser-based visualization, live streaming, and automated rendering via Python. It supports common biomechanics data formats, including OpenSim models (.osim), motion and force files (.sto, .mot), marker trajectories (.trc), JSON-based kinematics (e.g., OpenCap), and SMPL motion sequences (.pkl).


## 1. Interactive Web-Based Visualization

OpenCap Visualizer provides installation-free 3D visualization directly in the browser using Three.js. It supports anatomically accurate skeletal rendering, multi-subject overlays, markers (.trc), ground reaction forces (.mot), and synchronized video playback (\autoref{fig:multisubject}). Users can interactively control playback, camera views, colors, and transparency, and export high-resolution images, videos, or timelapse composites for figures and presentations (\autoref{fig:timelapse}).

\autoref{fig:multisubject} illustrates multi-subject comparison, including overlay of OpenCap monocular and marker-based motion capture.

\begin{figure}
\centering
\includegraphics[width=0.9\textwidth]{demo.png}
\caption{Example visualization of the web interface with multiple subjects.}
\label{fig:multisubject}
\end{figure}

\autoref{fig:markersforces} shows a visualization of marker trajectories and ground reaction forces.

\begin{figure}[h!]
\centering
\includegraphics[width=0.9\textwidth]{demo2.png}
\caption{Example visualization of the web interface with markers and forces.}
\label{fig:markersforces}
\end{figure}

\autoref{fig:timelapse} presents the timelapse rendering used to summarize dynamic movement patterns in static figures.

<!-- Selim TODO change figure to white background -->

\begin{figure}[h!]
\centering
\includegraphics[width=\textwidth]{gait.png}
\caption{Example timelapse visualization generated on the visualizer.}
\label{fig:timelapse}
\end{figure}

## 2. Live Streaming of Kinematics

In addition to offline playback, the visualizer supports real-time streaming of OpenSim-based kinematics via a lightweight Python WebSocket server. Incoming frames are incrementally rendered in the browser (\autoref{fig:livestream}). Multiple concurrent streams (e.g., predicted vs. reference motion; \autoref{fig:multisubject}) can be displayed simultaneously. This enables real-time monitoring of inverse kinematics, model validation during data collection, and flexible visualization of results from real-time inverse kinematics pipelines such as OpenSenseRT [@opensenseRT]. Example commands for real-time streaming include:

<!-- Selim TODO add RT commands -->

\autoref{fig:livestream} shows OpenSim kinematics streamed in real-time to the browser via the visualizer's WebSocket interface.

\begin{figure}[h!]
\centering
\includegraphics[width=0.7\textwidth]{livestream.jpg}
\caption{Example visualization of OpenSim kinematics in livestream (real-time)}
\label{fig:livestream}
\end{figure}

Example WebSocket server:

```python
import asyncio
import websockets
from opencap_visualizer import (
    build_live_init_dict,
    send_live_init,
    send_live_frame,
    skeleton_bodies_from_visualizer_json,
)

TEMPLATE = "subject1.json"  # or any visualizer JSON with bodies

async def handler(websocket):
    meta = skeleton_bodies_from_visualizer_json(TEMPLATE)
    init = build_live_init_dict(
        [{"id": "ik", "label": "Test", "bodies": meta, "model": "LaiArnold"}],
        frame_rate=30.0,
        camera="anterior",
    )
    await send_live_init(websocket, init, mesh_load_delay=0.5)

    frame_rate_hz = 30.0
    frame_dt = 1.0 / frame_rate_hz

    # Continuous real-time stream. Finite demo: break after N frames or set streaming = False.
    streaming = True
    t = 0.0
    while streaming:
        # Body pose (example): rotation in rad, translation in model units.
        # Sample rotation: [0.0, 0.0, 0.0]; sample translation: [0.0, 1.0, 0.0]
        rot_x = 0.0
        rot_y = 0.0
        rot_z = 0.0
        trans_x = 0.0
        trans_y = 1.0
        trans_z = 0.0

        bodies = {}
        for body_name in meta:
            bodies[body_name] = {
                "rotation": [rot_x, rot_y, rot_z],
                "translation": [trans_x, trans_y, trans_z],
            }

        await send_live_frame(websocket, {"ik": {"time": t, "bodies": bodies}})
        t += frame_dt
        await asyncio.sleep(frame_dt)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 876):
        await asyncio.Future()

asyncio.run(main())
```

## 3. Python API for Automated Video Creation

The opencap-visualizer Python package ([https://pypi.org/project/opencap-visualizer](https://pypi.org/project/opencap-visualizer)) enables fully programmatic video generation for integration into automated pipelines and headless servers. Users can batch-render videos with configurable camera views, subject overlays, colors, and looping behavior from standard OpenCap and OpenSim inputs, eliminating the need for manual GUI interaction. Example commands for video rendering include:

```python
import opencap_visualizer as ocv

# Single-subject OpenCap data
ocv.create_video("subj.json", "output.mp4", camera="anterior")
# Multi-subject comparison from OpenCap jsons
ocv.create_video(["subj1.json", "subj2.json"], "compare.mp4", colors=["red","blue"])
# Multiple synchronized data modalities
paths = ["model.osim", "motion.mot", "markers.trc", "forces.mot"]
ocv.create_video(paths, "experimental_visualization.mp4")
```


# Implementation

OpenCap Visualizer consists of a web-based frontend and a complementary Python package. The frontend is built with Vue.js and Three.js for interactive 3D visualization, with Vuetify providing UI components. The deployed web application includes cloud-based services for URL-based sharing and server-side conversion of OpenSim models and motion files into a browser-compatible JSON format.

For local and automated workflows, a lightweight Python package enables headless video generation for batch rendering, while a separate local Python script supports real-time kinematics streaming via WebSockets.



# Applications

OpenCap Visualizer supports high-throughput biomechanics workflows where manual, GUI-based visualization is impractical.

- **Algorithm development**: The ability to programmatically create videos with multiple models and data modalities allows researchers to quickly visualize comparisons when developing new algorithms or performing validation studies. This was previously a laborious task requiring extensive GUI interaction.

- **Quality control for large datasets**: A single video can be compiled of every motion trial in a dataset enabling rapid quality control after large data collections. This is an essential step for both lab-based and out-of-lab biomechanics experiments and is cumbersome with manual GUI interaction.

- **Reproducible figures for publications**: Timelapse rendering allows dynamic motion to be represented in static, publication-quality figures, facilitating clear qualitative comparisons in print.

- **Real-time biofeedback**: Real-time streaming enables real-time biofeedback studies using inverse kinematics from pipelines like OpenSenseRT [@opensenseRT].

- **Education and clinical documentation**: Browser-based visualization removes installation barriers, enabling interactive teaching materials and standardized video generation for documenting patient movement and intervention outcomes.



# Usage Summary

The web visualizer is available at [https://www.visualizer.opencap.ai](https://www.visualizer.opencap.ai). The pip package, named *opencap-visualizer*, is available at ([https://pypi.org/project/opencap-visualizer](https://pypi.org/project/opencap-visualizer)). The open-source code and example Python scripts are available at ([https://github.com/utahmobl/opencap-visualizer](https://github.com/utahmobl/opencap-visualizer)).


# References 
