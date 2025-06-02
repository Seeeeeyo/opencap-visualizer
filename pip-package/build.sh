#!/bin/bash
# Build script for OpenCap Visualizer CLI package

set -e

echo "🚀 Building OpenCap Visualizer CLI package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip setuptools wheel build

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
pip install --upgrade twine check-manifest
twine check dist/*

echo "✅ Package built successfully!"
echo "📁 Distribution files are in the 'dist/' directory"
echo ""
echo "To upload to PyPI:"
echo "  twine upload dist/*"
echo ""
echo "To test locally:"
echo "  pip install dist/opencap_visualizer_cli-*.whl" 