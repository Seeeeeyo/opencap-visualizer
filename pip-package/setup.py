#!/usr/bin/env python3

from setuptools import setup, find_packages
import pathlib

# Read the contents of README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Get version from package
def get_version():
    """Get version from __init__.py"""
    version_file = here / "opencap_visualizer" / "__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"

setup(
    name="opencap-visualizer",
    version=get_version(),
    author="Selim Gilon",
    author_email="selim.gilon@utah.edu",
    description="Tool for creating videos from OpenCap biomechanics data with both CLI and Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/utahmobl/opencap-visualizer",
    project_urls={
        "Bug Reports": "https://github.com/utahmobl/opencap-visualizer/issues",
        "Source": "https://github.com/utahmobl/opencap-visualizer",
        "Web App": "https://opencap-visualizer.onrender.com/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords="biomechanics, motion-capture, visualization, video, opencap, opensim",
    python_requires=">=3.7",
    install_requires=[
        "playwright>=1.40.0",
        "aiohttp>=3.8.0",
        "pathlib2>=2.3.0; python_version<'3.4'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "ffmpeg": [
            "ffmpeg-python>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "opencap-visualizer=opencap_visualizer.cli:main",
            "opencap-viz=opencap_visualizer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "opencap_visualizer": ["*.md", "*.txt"],
    },
    zip_safe=False,
    platforms=["any"],
) 