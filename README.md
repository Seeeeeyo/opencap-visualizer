# OpenCap Visualizer

A comprehensive web-based platform for interactive visualization and automated video creation of biomechanics data. Built with Vue.js and Three.js, the visualizer supports multiple data formats including OpenSim models (.osim files), kinematics data (.mot, .json), markers (.trc), and force data (.mot).

## 🌐 Live Demo

**Try it now**: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)

No installation required - works directly in your browser!

## 🚀 Quick Start

### Web Interface
1. Visit [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)
2. Upload your biomechanics data files
3. Explore interactive 3D visualizations
4. Generate videos and screenshots

### Python Package
For programmatic video generation, install the Python package:

```bash
pip install opencap-visualizer
playwright install chromium
```

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
    "comparison.mp4",
    colors=["red", "blue"],
    camera="sagittal"
)
```

**📦 Package Repository**: [opencap-visualizer-pip](https://github.com/Seeeeeyo/opencap-visualizer-pip)

## 🔧 Key Features

### Interactive Web-Based Visualization
- **Real-time 3D rendering** of skeletal models with anatomically accurate geometry
- **Multi-subject comparison** with independent color coding and transparency controls
- **Marker visualization** supporting standard motion capture marker sets (.trc files)
- **Ground reaction forces visualization** using .mot files
- **Video synchronization** with skeleton for simultaneous viewing
- **Timeline controls** with adjustable playback speed and frame-by-frame navigation
- **Recording capabilities** for capturing custom video segments
- **Image capture** for high-resolution screenshots
- **Timelapse mode** for accelerated visualizations
- **Color controls** for customizing all visual elements

### Python API for Automated Video Creation
- **Command-line interface** for batch processing
- **Python API** for integration into analysis pipelines
- **Multiple camera angles** (anterior, posterior, sagittal, superior, etc.)
- **Customizable output** (resolution, colors, loops, zoom)
- **Headless operation** for server-side processing

## 📁 Supported Data Formats

- **OpenSim models** (.osim) with motion files (.mot)
- **JSON-based motion data** from OpenCap and other sources
- **TRC marker files** for traditional motion capture data
- **GRF files** (.mot) for ground reaction forces

## 🔄 OpenSim Integration

For OpenSim users, we provide a dedicated converter API:

**🔗 OpenSim Converter**: [opensim-to-visualizer-api](https://github.com/Seeeeeyo/opensim-to-visualizer-api)

This service converts OpenSim .osim and .mot files into the JSON format required by the visualizer, enabling seamless integration with existing OpenSim workflows.

## 🏗️ Architecture

### Frontend
- **Vue.js** for reactive user interface components
- **Three.js** for 3D graphics rendering and animation
- **Vuetify** for Material Design components

### Backend Services
- **Node.js sharing backend** for URL-based data sharing
- **Python CLI and API** using Playwright for automated browser control
- **OpenSim file converter backend** for .osim/.mot to JSON conversion

## 🎯 Research Applications

- **Clinical Gait Analysis**: Visualize patient gait patterns and compare pre/post-intervention results
- **Sports Biomechanics**: Analyze athletic movements and compare techniques across athletes
- **Rehabilitation Research**: Track changes in movement patterns over time
- **Educational Applications**: Create interactive demonstrations of human movement principles

## 🛠️ Development

### Prerequisites
- Node.js (v14+)
- Python 3.8+
- npm or yarn

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run serve

# Build for production
npm run build
```

### Python Package Development
```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest
```

## 📚 Documentation

- **Web Interface**: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)
- **Python Package**: [opencap-visualizer-pip](https://github.com/Seeeeeyo/opencap-visualizer-pip)
- **OpenSim Converter**: [opensim-to-visualizer-api](https://github.com/Seeeeeyo/opensim-to-visualizer-api)

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines and feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## 🙏 Acknowledgements

We acknowledge the contributions of the OpenCap development team and the broader biomechanics research community. This work builds upon the foundation of open-source biomechanics tools including OpenSim and the Three.js graphics library.

## 📞 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/utahmobl/opencap-visualizer/issues)
- **Web App**: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/)
- **Documentation**: Check the individual repository READMEs for detailed usage instructions
