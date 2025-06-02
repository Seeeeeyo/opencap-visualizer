# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of OpenCap Visualizer CLI
- Generate videos from OpenCap JSON files
- Support for .osim/.mot file pairs (OpenSim format)
- Multiple subject comparison in single video
- Anatomical camera view options (anterior, posterior, sagittal, superior, inferior)
- Custom subject colors (hex codes and color names)
- Interactive browser mode for manual exploration
- Automatic camera centering and zoom controls
- Multiple animation loops support
- Uses deployed OpenCap Visualizer web app by default
- Fallback to local development server and built files
- MP4 and WebM video output formats
- FFmpeg integration for better MP4 compatibility
- Comprehensive command-line interface
- Cross-platform support (Windows, macOS, Linux)

### Features
- **File Format Support**: JSON, .osim/.mot pairs
- **Camera Views**: anatomical and technical perspectives
- **Visual Customization**: colors, zoom, centering, loops
- **Output Options**: MP4/WebM, custom resolution, quality settings
- **Interactive Mode**: browser-based exploration and manual recording
- **Automation**: headless video generation with customizable parameters
- **Reliability**: multiple fallback options for Vue app access

### Technical Details
- Built on Playwright for browser automation
- Integrates with deployed Vue.js visualizer
- Async Python architecture for performance
- Comprehensive error handling and user feedback
- Modular design for easy maintenance and extension 