---
title: 'OpenCap Visualizer: A Web-Based Platform for Scriptable, Real-Time, and Interactive Visualization of Biomechanics Data'
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
    affiliation: "1, 2"
affiliations:
  - name: Department of Mechanical Engineering, University of Utah, Salt Lake City, UT, USA
    index: 1
  - name: Department of Orthopaedic Surgery, University of Utah, Salt Lake City, UT, USA
    index: 2
date: 30 March 2026
bibliography: paper.bib
---

# Summary

Biomechanics research relies on visualizing 3D movement data to interpret and validate results, but traditional desktop-based graphical user interfaces (GUIs) have become a bottleneck as the scale of biomechanics datasets grows and processing increasingly moves to cloud-based servers. Current GUIs require extensive manual interaction to load models and motions, configure scenes, and export media. To resolve these challenges, we created OpenCap Visualizer, a web-based platform and Python package that enables both interactive 3D visualization, real-time streaming, and programmatic video generation.

The software provides three primary interfaces: a browser-based viewer for shareable visualization, a WebSocket interface for real-time streaming, and a Python API for automated rendering. Built with Vue.js and Three.js, it supports standard biomechanics formats—including OpenSim models (.osim), kinematics (.mot, .json), markers (.trc), and force data (.mot)—allowing researchers to process, analyze, render, and share biomechanics videos with minimal human intervention.


The platform is available at [https://www.visualizer.opencap.ai](https://www.visualizer.opencap.ai).

# Statement of Need

Biomechanics datasets are growing by orders of magnitude due to recent advances in mobile sensing, including wearables and markerless motion capture [@Boswell; @AddBiomechanics; @Duane; @opencap; @opencap-monocular], and data processing is increasingly performed on cloud-based servers such as OpenCap [@opencap] and AddBiomechanics [@AddBiomechanics]. Existing visualization workflows do not scale to these settings: we recently conducted a study using OpenCap with 129 individuals performing 10 activities, and manually loading 1,290 trials for quality control in a desktop GUI is infeasible. Comparing the effects of different algorithms on a single motion is a similarly common biomechanics task that currently requires extensive manual interaction. The community therefore lacks a flexible tool for programmatic, real-time, and shareable visualization of movement data, and this gap is felt most acutely by researchers running cloud-based pipelines, large field studies, and real-time experiments.

OpenCap Visualizer addresses this gap with a Python API for batch-generating reproducible videos and figures, a browser-based viewer for collaborators to inspect 3D data via lightweight URLs, and a WebSocket interface for real-time streaming. The platform builds on the OpenCap ecosystem [@opencap] and is compatible with OpenSim models and standard biomechanics data formats [@opensim], making it applicable to both traditional marker-based workflows and emerging markerless approaches using cameras [@opencap; @opencap-monocular] or IMUs [@opensense; @opensenseRT].


# State of the Field

The OpenSim GUI [@opensim] is a widely used visualization tool in musculoskeletal biomechanics and is optimized for interactive, single-trial analysis on local machines through a desktop Java application; it does not expose a scripting interface for video generation and does not scale to the automated workflows required for cloud-processed datasets. Mokka and the underlying Biomechanical ToolKit (BTK) [@btk] target C3D-based motion capture data and similarly rely on desktop interaction. Physics-oriented packages such as MuJoCo [@mujoco] include integrated viewers but are designed around simulation rather than analysis of measured human movement. Web-based viewers bundled with cloud platforms such as AddBiomechanics [@AddBiomechanics] are tightly coupled to a single processing backend and dataset format, restricting their use as general-purpose visualization layers.

We chose to build a new format-agnostic tool rather than extend the OpenSim GUI because cloud-based processing pipelines require server-side, headless rendering that is impractical inside a desktop Java application; browser-based 3D rendering enables zero-install collaboration via shareable URLs; and unifying live streaming, batch video, and interactive viewing under a single data model substantially reduces the friction of moving between visualization modes during research.


# Key Features

OpenCap Visualizer supports three complementary modes of interaction: browser-based visualization, live streaming, and automated rendering via Python. It supports common biomechanics data formats, including OpenSim models (.osim), motion and force files (.sto, .mot), marker trajectories (.trc), JSON-based kinematics (e.g., OpenCap), and SMPL motion sequences (.pkl) [@opensim;@opencap;@smpl].


## 1. Interactive Web-Based Visualization

OpenCap Visualizer provides installation-free 3D visualization directly in the browser using Three.js. It supports anatomically accurate skeletal rendering, multi-subject overlays, markers (.trc), ground reaction forces (.mot), and synchronized video playback. Users can interactively control playback, camera views, colors, and transparency, and export high-resolution images, videos, or timelapse composites for figures and presentations. \autoref{fig:multisubject} illustrates multi-subject comparison, including overlay of OpenCap Monocular [@opencap-monocular] and marker-based motion capture. \autoref{fig:markersforces} shows synchronized motion, marker, and ground reaction force data. \autoref{fig:timelapse} presents the timelapse rendering used to summarize dynamic movement patterns in static figures.

\begin{figure}
\centering
\includegraphics[width=0.9\textwidth]{demo.png}
\caption{Example visualization of the web interface with multiple subjects.}
\label{fig:multisubject}
\end{figure}



\begin{figure}[h!]
\centering
\includegraphics[width=0.9\textwidth]{demo2.png}
\caption{Example visualization of the web interface with markers and forces.}
\label{fig:markersforces}
\end{figure}



\begin{figure}[h!]
\centering
\includegraphics[width=\textwidth]{gait.png}
\caption{Example timelapse visualization generated on the visualizer.}
\label{fig:timelapse}
\end{figure}

## 2. Live Streaming of Kinematics

In addition to offline playback, the visualizer supports real-time streaming of OpenSim-based kinematics via a lightweight Python WebSocket server. Stream setup and frame helpers (e.g., `build_live_init_dict`, `send_live_init`, `send_live_frame`) are included in the opencap-visualizer pip package ([PyPI](https://pypi.org/project/opencap-visualizer)). Incoming frames are incrementally rendered in the browser (\autoref{fig:livestream}). Multiple concurrent streams (e.g., predicted vs. reference motion; \autoref{fig:multisubject}) can be displayed simultaneously. This enables real-time monitoring of inverse kinematics, model validation during data collection, and flexible visualization of results from real-time inverse kinematics pipelines such as OpenSenseRT [@opensenseRT]. Example usage from the package includes:

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

    # Continuous real-time stream. 
    # Finite demo: break after N frames or set streaming = False.
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

\begin{figure}[h!]
\centering
\includegraphics[width=0.7\textwidth]{livestream.jpg}
\caption{Example visualization of OpenSim kinematics in livestream (real-time).}
\label{fig:livestream}
\end{figure}

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


# Software Design

OpenCap Visualizer is structured as a thin web frontend, a stateless cloud service, and a Python client package, with all three layers sharing a single intermediate JSON representation of bodies, motions, markers, and forces. Centering the architecture on this representation rather than a particular file format was a deliberate trade-off: it adds an explicit conversion step on the server, but decouples the rendering pipeline from OpenSim's C++ runtime and lets the same browser viewer drive interactive playback, headless video export through a Puppeteer-controlled Chromium instance, and live streaming. This shared data model is what makes both batch generation on cloud servers and real-time streaming from local inverse kinematics pipelines fit into a single codebase.

We chose Vue.js and Three.js over a more specialized rendering toolkit to keep the dependency surface compatible with shared hosting, embeddable iframes, and mobile browsers, broadening accessibility for collaborators who do not run dedicated biomechanics software. The Python package wraps a headless browser to reproduce the exact frontend renderer, ensuring that automatically generated videos are visually identical to interactive playback—an important property for paper figures and reproducibility, but difficult to achieve when the offline renderer is a separate program. The live-streaming server is intentionally minimal: it forwards body transforms over WebSockets without owning model state, so users can plug in any inverse kinematics backend (e.g., OpenSenseRT [@opensenseRT]) without modifying the visualizer.

The frontend is built with Vue.js and Three.js, with Vuetify providing UI components. The deployed web application includes cloud-based services for URL-based sharing and server-side conversion of OpenSim models and motion files into the browser-compatible JSON representation. For local and automated workflows, the lightweight Python package enables headless video generation, while a companion Python module supports real-time kinematics streaming via WebSockets.



# Applications

OpenCap Visualizer supports high-throughput biomechanics workflows where manual, GUI-based visualization is impractical.

- **Algorithm development**: The ability to programmatically create videos with multiple models and data modalities allows researchers to quickly visualize comparisons when developing new algorithms or performing validation studies. This was previously a laborious task requiring extensive GUI interaction.

- **Quality control for large datasets**: A single video can be compiled of every motion trial in a dataset enabling rapid quality control after large data collections. This is an essential step for both lab-based and out-of-lab biomechanics experiments and was cumbersome with prior GUI-based workflows.

- **Reproducible figures for publications**: Timelapse rendering allows dynamic motion to be represented in static, publication-quality figures, facilitating clear qualitative comparisons in print.

- **Real-time biofeedback**: Real-time streaming enables real-time biofeedback studies using inverse kinematics from pipelines like OpenSenseRT [@opensenseRT].

- **Education and clinical documentation**: Browser-based visualization removes installation barriers, enabling interactive teaching materials and standardized video generation for documenting patient movement and intervention outcomes.


# Research Impact

OpenCap Visualizer is integrated into the OpenCap [@opencap] processing pipeline and serves as the default visualization tool for OpenCap Monocular [@opencap-monocular]. The Python package is published on PyPI ([https://pypi.org/project/opencap-visualizer](https://pypi.org/project/opencap-visualizer)) and has been used by our group to run a parameter optimization across several hundred trials to visualize the resulting motions from OpenCap Monocular, with both the qualitative figures and the supplementary motion videos in [@opencap-monocular] generated directly with the tool. The browser viewer has further supported peer collaboration on OpenCap projects through shareable URLs. The codebase is released open-source under the Apache License 2.0 on GitHub with public issue tracking, automated PyPI releases, and worked examples in the repository. Near-term uptake is anticipated by groups working with markerless motion capture, real-time biofeedback, and large-scale field studies, where the absence of a scriptable, browser-based visualizer has been a recurring bottleneck.


# AI Usage Disclosure

Generative AI assistants (GitHub Copilot and Anthropic Claude) were used during software development to draft boilerplate code, write documentation, and propose refactorings, and during paper writing to polish prose and tighten phrasing. All AI-generated code was reviewed, tested, and edited by the authors before being merged.


# Usage Summary

The web visualizer is available at [https://www.visualizer.opencap.ai](https://www.visualizer.opencap.ai). The Python package, *opencap-visualizer*, can be installed via pip at [https://pypi.org/project/opencap-visualizer](https://pypi.org/project/opencap-visualizer). The open-source code and example Python scripts are available at [https://github.com/utahmobl/opencap-visualizer](https://github.com/utahmobl/opencap-visualizer).


# References 
