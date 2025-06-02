# Development Guide

This guide explains how to develop, build, and distribute the OpenCap Visualizer CLI package.

## 🛠️ Development Setup

### 1. Clone and Setup
```bash
git clone https://github.com/utahmobl/opencap-visualizer-cli.git
cd opencap-visualizer/pip-package
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Development Dependencies
```bash
pip install -e .[dev]
pip install playwright
playwright install chromium
```

## 🔧 Development Workflow

### Testing Changes Locally
```bash
# Install in development mode
pip install -e .

# Test the CLI
opencap-visualizer --help
opencap-visualizer sample.json --interactive
```

### Code Quality
```bash
# Format code
black opencap_visualizer/

# Lint code
flake8 opencap_visualizer/

# Type checking
mypy opencap_visualizer/
```

## 📦 Building the Package

### Using the Build Script
```bash
chmod +x build.sh
./build.sh
```

### Manual Build
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Install build tools
pip install --upgrade build twine

# Build package
python -m build

# Check package
twine check dist/*
```

## 🚀 Publishing

### Test on PyPI Test
```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ opencap-visualizer-cli
```

### Publish to PyPI
```bash
# Upload to PyPI
twine upload dist/*
```

## 📋 Release Checklist

Before releasing a new version:

- [ ] Update version in `opencap_visualizer/__init__.py`
- [ ] Update `CHANGELOG.md` with new features/fixes
- [ ] Test all functionality locally
- [ ] Run `./build.sh` to build and check package
- [ ] Test install from built wheel: `pip install dist/*.whl`
- [ ] Test upload to TestPyPI
- [ ] Test install from TestPyPI
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Create GitHub release

## 🧪 Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Test with real data files
opencap-visualizer sample.json -o test_output.mp4

# Test interactive mode
opencap-visualizer sample.json --interactive

# Test different formats
opencap-visualizer model.osim motion.mot -o test_opensim.mp4
```

### Manual Testing Checklist

- [ ] Basic video generation works
- [ ] Interactive mode opens browser correctly
- [ ] `--quiet` flag suppresses browser logs
- [ ] Multiple subjects render correctly
- [ ] Camera views work as expected
- [ ] Color customization works
- [ ] OpenSim file conversion works
- [ ] FFmpeg conversion works (if installed)
- [ ] Error handling provides useful messages

## 📁 Package Structure

```
pip-package/
├── opencap_visualizer/          # Main package
│   ├── __init__.py             # Package metadata
│   └── cli.py                  # Main CLI implementation
├── build.sh                    # Build script
├── setup.py                    # Setup configuration
├── pyproject.toml              # Modern Python packaging
├── requirements.txt            # Dependencies
├── MANIFEST.in                 # Include additional files
├── README.md                   # Package documentation
├── LICENSE                     # MIT license
├── CHANGELOG.md                # Version history
└── DEVELOPMENT.md              # This file
```

## 🔄 Version Management

The package uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

Update version in `opencap_visualizer/__init__.py`:
```python
__version__ = "1.1.0"
```

## 🐛 Debugging

### Common Issues

**Package not found after installation:**
```bash
# Ensure you're in the right environment
which python
which opencap-visualizer
```

**Playwright browser issues:**
```bash
# Reinstall browsers
playwright install chromium
```

**Build issues:**
```bash
# Clean everything and rebuild
rm -rf build/ dist/ *.egg-info/
pip install --upgrade build setuptools wheel
python -m build
```

## 📝 Documentation

Update documentation in:
- `README.md` - Main usage documentation
- `CHANGELOG.md` - Version history
- `DEVELOPMENT.md` - Development instructions
- Docstrings in Python code 