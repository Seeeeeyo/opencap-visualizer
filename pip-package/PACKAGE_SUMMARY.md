# OpenCap Visualizer Package Summary

## Version 1.1.0 - Major Update: Python API + Naming Consistency

### 🚨 Package Renamed
- **Old**: `opencap-visualizer-cli` 
- **New**: `opencap-visualizer`
- **Commands remain the same**: `opencap-visualizer` and `opencap-viz`

### ✨ New Python API

#### Class-based Usage
```python
import opencap_visualizer as ocv

visualizer = ocv.OpenCapVisualizer(verbose=True)
success = visualizer.generate_video_sync(
    ["subject1.json", "subject2.json"],
    "comparison.mp4",
    camera="anterior",
    colors=["red", "blue"]
)
```

#### Convenience Functions
```python
import opencap_visualizer as ocv

# Synchronous
success = ocv.create_video("data.json", "output.mp4")

# Asynchronous  
success = await ocv.create_video_async("data.json", "output.mp4")
```

### 📦 Package Structure
```
opencap_visualizer/
├── __init__.py          # Main API exports
├── api.py               # Python API classes/functions
├── cli.py               # Command-line interface
└── example_usage.py     # Usage examples
```

### 🔄 Migration Guide

#### For CLI Users
- **No changes required** - commands work exactly the same
- Package installation: `pip install opencap-visualizer` (was `opencap-visualizer-cli`)

#### For Python Users
- **New capability** - can now call directly from Python
- Import: `import opencap_visualizer as ocv`

### 📋 Features Summary

#### Command Line Interface
- Generate videos from biomechanics data files (.json, .osim/.mot)
- Multiple subjects comparison
- Anatomical camera views (anterior, posterior, sagittal, etc.)
- Custom colors, zoom, centering, loops
- Interactive browser mode
- Automatic fallback: deployed app → local dev → built files

#### Python API
- **OpenCapVisualizer class**: Object-oriented interface
- **Convenience functions**: Direct function calls
- **Async/sync support**: Choose based on your needs  
- **Type hints**: Full typing support
- **Comprehensive docs**: Docstrings and examples

### 🛠️ Technical Details

#### Dependencies
- `playwright>=1.40.0` - Browser automation
- `aiohttp>=3.8.0` - HTTP client for server detection
- `pathlib2>=2.3.0` - Path handling (Python <3.4)

#### Supported Platforms
- Windows, macOS, Linux
- Python 3.7+

#### Video Generation
- Uses deployed OpenCap Visualizer web app
- Headless browser automation with Playwright
- WebM recording with optional FFmpeg conversion to MP4
- Configurable resolution, frame rate, timeout

### 📖 Documentation

#### Updated Files
- `README.md` - Complete rewrite with CLI + Python API examples
- `CHANGELOG.md` - Detailed version history
- `example_usage.py` - Comprehensive Python API examples
- `setup.py` - Updated package metadata and description

#### Examples Provided
1. **Basic Usage**: Simple video generation
2. **Multiple Subjects**: Comparison videos with custom settings
3. **Class-based**: Object-oriented approach
4. **Async Usage**: Non-blocking video generation
5. **OpenSim Files**: Model + motion file pairs
6. **Batch Processing**: Multiple datasets automation

### 🎯 Use Cases

#### Research & Clinical
```python
# Generate standardized videos for publications
for trial in walking_trials:
    ocv.create_video(
        trial["data_file"], 
        f"publication_videos/{trial['subject']}_walking.mp4",
        camera="sagittal", 
        colors=["blue"],
        loops=2
    )
```

#### Automation & Integration
```python
# Integrate into larger analysis pipelines
async def analyze_subject(subject_id):
    # ... run biomechanics analysis ...
    
    # Generate visualization video
    video_success = await ocv.create_video_async(
        f"{subject_id}_results.json",
        f"reports/{subject_id}_animation.mp4", 
        camera="anterior"
    )
    
    return analysis_results, video_success
```

#### Interactive Development
```bash
# Quick CLI testing during development
opencap-visualizer test_data.json --interactive --camera anterior --verbose
```

### 🚀 Installation & Setup

```bash
# Install package
pip install opencap-visualizer

# Install browser dependencies
playwright install chromium

# Test CLI
opencap-visualizer --help

# Test Python API
python -c "import opencap_visualizer as ocv; print('✅ Ready to go!')"
```

### 🔍 Quality Assurance

#### Tested Components
- ✅ Package imports correctly
- ✅ CLI interface works as before  
- ✅ Python API classes instantiate
- ✅ Function signatures are correct
- ✅ Type hints are comprehensive
- ✅ Documentation is complete

#### Backward Compatibility
- ✅ All CLI commands work identically
- ✅ All CLI options preserved
- ✅ Same video output quality
- ✅ Same fallback logic (deployed → local → built)

### 📊 Impact

#### For Current CLI Users
- **Zero breaking changes** to existing workflows
- **Enhanced**: Better package name consistency  
- **Bonus**: Can now integrate into Python scripts

#### For New Python Users
- **Native Python integration** without subprocess calls
- **Type safety** with comprehensive hints
- **Async support** for high-performance applications  
- **Clean API** following Python best practices

### 🎉 Summary

This update transforms `opencap-visualizer` from a CLI-only tool into a **dual-purpose package** that maintains full backward compatibility while adding powerful Python API capabilities. The naming is now consistent (`opencap-visualizer` package → `opencap-visualizer` command), and users can choose between command-line usage and programmatic integration based on their needs. 