#!/bin/bash
# Test installation script for OpenCap Visualizer CLI package

set -e

echo "🧪 Testing OpenCap Visualizer CLI package installation..."

# Create a temporary virtual environment
echo "📦 Creating test environment..."
python -m venv test_env
source test_env/bin/activate

# Install from the built wheel
echo "⬇️ Installing package from wheel..."
pip install dist/opencap_visualizer_cli-*.whl

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Test the CLI commands
echo "🔧 Testing CLI commands..."
echo "Testing help command:"
opencap-visualizer --help

echo "Testing short command:"
opencap-viz --help

echo "✅ Package installation test completed successfully!"
echo ""
echo "To test with real data:"
echo "  opencap-visualizer your_data.json -o test_video.mp4"
echo ""
echo "To test interactive mode:"
echo "  opencap-visualizer your_data.json --interactive"

# Clean up
deactivate
rm -rf test_env

echo "🧹 Test environment cleaned up." 