"""
OpenCap Visualizer - Generate videos from biomechanics data files

A tool for creating videos from OpenCap biomechanics data with both 
command-line interface and Python API support.

Basic Usage:
    Command Line:
        $ opencap-visualizer data.json -o output.mp4
        $ opencap-visualizer subject1.json subject2.json --camera anterior --colors red blue
    
    Python API:
        >>> import opencap_visualizer as ocv
        >>> success = ocv.create_video("data.json", "output.mp4")  # Synchronous
        >>> success = await ocv.create_video_async("data.json", "output.mp4")  # Async
        
        >>> visualizer = ocv.OpenCapVisualizer(verbose=True)
        >>> await visualizer.generate_video(
        ...     ["subject1.json", "subject2.json"], 
        ...     "comparison.mp4",
        ...     camera="anterior", 
        ...     colors=["red", "blue"]
        ... )
"""

__version__ = "1.0.0"
__author__ = "Selim Gilon"
__email__ = "selim.gilon@utah.edu"

# Import CLI main function
from .cli import main

# Import Python API
from .api import (
    OpenCapVisualizer,
    create_video,
    create_video_async,
    DEFAULT_OUTPUT_FILENAME,
    DEFAULT_VIEWPORT_SIZE,
    DEFAULT_TIMEOUT
)

__all__ = [
    # CLI
    "main",
    
    # Python API - Main class
    "OpenCapVisualizer",
    
    # Python API - Convenience functions
    "create_video",
    "create_video_async",
    
    # Constants
    "DEFAULT_OUTPUT_FILENAME",
    "DEFAULT_VIEWPORT_SIZE", 
    "DEFAULT_TIMEOUT",
] 