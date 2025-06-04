#!/usr/bin/env python3
"""
Example usage of OpenCap Visualizer Python API

This script demonstrates various ways to use the opencap_visualizer package
from Python code, showing both synchronous and asynchronous usage patterns.
"""

import asyncio
import opencap_visualizer as ocv

def example_basic_usage():
    """Example 1: Basic synchronous usage"""
    print("=== Example 1: Basic Usage ===")
    
    # Simple video generation
    success = ocv.create_video(
        "example_data.json", 
        "basic_output.mp4",
        verbose=True
    )
    
    if success:
        print("✅ Video generated successfully!")
    else:
        print("❌ Video generation failed")
    
    return success

def example_multiple_subjects():
    """Example 2: Multiple subjects with custom settings"""
    print("\n=== Example 2: Multiple Subjects ===")
    
    # Multiple subjects with custom colors and camera
    success = ocv.create_video(
        ["subject1.json", "subject2.json", "subject3.json"],
        "comparison.mp4",
        camera="anterior",  # Front-facing view
        colors=["red", "green", "blue"],  # Custom colors
        loops=2,  # Two animation loops
        zoom=1.2,  # Slightly zoomed out
        verbose=True
    )
    
    if success:
        print("✅ Multi-subject comparison video created!")
    else:
        print("❌ Multi-subject video generation failed")
    
    return success

def example_class_based():
    """Example 3: Using the OpenCapVisualizer class"""
    print("\n=== Example 3: Class-based Usage ===")
    
    # Create visualizer instance with verbose logging
    visualizer = ocv.OpenCapVisualizer(verbose=True)
    
    # Generate high-resolution video
    success = visualizer.generate_video_sync(
        input_files="biomechanics_data.json",
        output_path="high_res_output.mp4",
        width=3840,   # 4K width
        height=2160,  # 4K height
        camera="sagittal",  # Side profile view
        colors=["#ff6b35"],  # Custom orange color
        center_subjects=True,  # Auto-center camera
        zoom=1.5  # Zoomed out view
    )
    
    if success:
        print("✅ High-resolution video created!")
    else:
        print("❌ High-resolution video generation failed")
    
    return success

async def example_async_usage():
    """Example 4: Asynchronous usage"""
    print("\n=== Example 4: Async Usage ===")
    
    # Using the async convenience function
    success1 = await ocv.create_video_async(
        "data1.json",
        "async_output1.mp4",
        camera="posterior",  # Back view
        colors=["blue"],
        verbose=True
    )
    
    # Using the class with async method
    visualizer = ocv.OpenCapVisualizer(verbose=True)
    success2 = await visualizer.generate_video(
        ["data2.json", "data3.json"],
        "async_comparison.mp4",
        camera="superior",  # Top-down view
        colors=["purple", "cyan"],
        loops=3
    )
    
    if success1 and success2:
        print("✅ Both async videos generated successfully!")
    else:
        print("❌ One or more async video generations failed")
    
    return success1 and success2

def example_opensim_files():
    """Example 5: Working with OpenSim files"""
    print("\n=== Example 5: OpenSim Files ===")
    
    # Generate video from OpenSim model and motion files
    success = ocv.create_video(
        ["model.osim", "motion.mot"],
        "opensim_simulation.mp4",
        camera="isometric",  # 3D perspective view
        colors=["green"],
        loops=1,
        verbose=True
    )
    
    if success:
        print("✅ OpenSim simulation video created!")
    else:
        print("❌ OpenSim video generation failed")
    
    return success

async def example_batch_processing():
    """Example 6: Batch processing multiple datasets"""
    print("\n=== Example 6: Batch Processing ===")
    
    datasets = [
        ("walking_trial1.json", "walking_1.mp4"),
        ("walking_trial2.json", "walking_2.mp4"),
        ("running_trial1.json", "running_1.mp4"),
    ]
    
    visualizer = ocv.OpenCapVisualizer(verbose=True)
    results = []
    
    for input_file, output_file in datasets:
        print(f"Processing {input_file}...")
        success = await visualizer.generate_video(
            input_file,
            output_file,
            camera="sagittal",  # Side view for gait analysis
            colors=["red"],
            zoom=1.3
        )
        results.append(success)
        
        if success:
            print(f"✅ {output_file} created successfully")
        else:
            print(f"❌ Failed to create {output_file}")
    
    successful_count = sum(results)
    print(f"\n📊 Batch processing complete: {successful_count}/{len(datasets)} videos created")
    
    return results

def main():
    """Run all examples"""
    print("OpenCap Visualizer Python API Examples")
    print("=" * 40)
    
    # Run synchronous examples
    example_basic_usage()
    example_multiple_subjects() 
    example_class_based()
    example_opensim_files()
    
    # Run asynchronous examples
    print("\n🔄 Running async examples...")
    asyncio.run(example_async_usage())
    asyncio.run(example_batch_processing())
    
    print("\n🎉 All examples completed!")
    print("\nNOTE: These examples assume you have valid data files.")
    print("Replace the file paths with your actual biomechanics data files.")

if __name__ == "__main__":
    main() 