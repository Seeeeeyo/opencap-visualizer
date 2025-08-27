#!/usr/bin/env python3
"""
Test script to verify SMPLX models can be loaded from the specified path
"""

import numpy as np
from pathlib import Path
import json

def test_smplx_model_loading():
    """
    Test loading SMPLX models from the specified path
    """
    print("Testing SMPLX Model Loading")
    print("=" * 40)
    
    # SMPLX model path
    MODEL_BASE_PATH = "/Users/selimgilon/Downloads/smplx"
    model_path = Path(MODEL_BASE_PATH)
    
    if not model_path.exists():
        print(f"❌ SMPLX model path not found: {model_path}")
        return False
    
    print(f"✅ SMPLX model path found: {model_path}")
    
    # Check for available models
    models_found = {}
    for gender in ['MALE', 'FEMALE', 'NEUTRAL']:
        npz_path = model_path / f"SMPLX_{gender}.npz"
        pkl_path = model_path / f"SMPLX_{gender}.pkl"
        
        if npz_path.exists():
            models_found[gender.lower()] = str(npz_path)
            print(f"✅ Found SMPLX {gender} model: {npz_path}")
        elif pkl_path.exists():
            models_found[gender.lower()] = str(pkl_path)
            print(f"✅ Found SMPLX {gender} model: {pkl_path}")
        else:
            print(f"❌ No SMPLX {gender} model found")
    
    # Test SMPLX import and model loading
    try:
        from smplx import SMPLX
        print("✅ SMPLX package imported successfully")
        
        # Test loading one model
        if 'male' in models_found:
            print(f"Testing SMPLX model loading: {models_found['male']}")
            smpl = SMPLX(models_found['male'], gender='male')
            print("✅ SMPLX model loaded successfully")
            
            # Test forward pass
            import torch
            shape_params = torch.zeros(1, 10, dtype=torch.float32)
            global_orient = torch.zeros(1, 3, dtype=torch.float32)
            body_pose = torch.zeros(1, 21, 3, dtype=torch.float32)  # 21 joints × 3 axes (SMPLX has 21 body joints)
            
            body = smpl.forward(betas=shape_params, body_pose=body_pose, global_orient=global_orient)
            print(f"✅ Forward pass successful - Vertices shape: {body.v_shaped.shape}")
            print(f"✅ Faces shape: {smpl.faces.shape}")
            
        else:
            print("❌ No male model found to test")
            
    except ImportError as e:
        print(f"❌ SMPLX package not available: {e}")
        print("Install with: pip install smplx")
        return False
    except Exception as e:
        print(f"❌ Error loading SMPLX model: {e}")
        return False
    
    return len(models_found) > 0

def create_test_animation():
    """
    Create a simple test animation for OpenCap integration
    """
    print("\nCreating Test Animation")
    print("=" * 30)
    
    # Create a simple pose sequence
    frames = 30
    pose_sequence = []
    
    for frame in range(frames):
        time = frame / frames * 2 * np.pi
        
        # Simple pose parameters
        pose_params = np.zeros(72)
        
        # Add some movement
        pose_params[0:3] = [0, np.sin(time) * 0.1, 0]  # Pelvis rotation
        pose_params[3:6] = [np.sin(time) * 0.2, 0, 0]  # Left hip
        pose_params[6:9] = [-np.sin(time) * 0.2, 0, 0]  # Right hip
        
        pose_sequence.append(pose_params.tolist())
    
    # Create test data
    test_data = {
        "model": "smpl_male",
        "gender": "male",
        "shape": [0.0] * 10,
        "pose_sequence": pose_sequence,
        "frame_rate": 30,
        "metadata": {
            "description": "Test animation for OpenCap integration",
            "created_with": "SMPLX Test Script",
            "joint_count": 24,
            "shape_params": 10,
            "pose_params_per_frame": 72,
            "total_frames": len(pose_sequence)
        }
    }
    
    # Save test file
    with open('test_smpl_animation.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print("✅ Test animation created: test_smpl_animation.json")
    return test_data

def main():
    """
    Main test function
    """
    print("SMPLX Model Test Script")
    print("=" * 50)
    
    # Test model loading
    success = test_smplx_model_loading()
    
    if success:
        # Create test animation
        create_test_animation()
        
        print("\n🎉 All tests passed!")
        print("\nNext steps:")
        print("1. Run the advanced integration example:")
        print("   python examples/smpl_gloss_integration_advanced.py")
        print("2. Test the OpenCap integration:")
        print("   - Load test_smpl_animation.json in the browser console")
        print("   - Use the SMPL viewer in OpenCap Visualizer")
    else:
        print("\n❌ Tests failed. Please check the SMPLX installation and model paths.")
        print("\nTroubleshooting:")
        print("1. Install SMPLX: pip install smplx")
        print("2. Verify model paths exist")
        print("3. Check file permissions")

if __name__ == "__main__":
    main() 