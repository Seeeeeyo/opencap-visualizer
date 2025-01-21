import os
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def automate_recording(json1_path, json2_path, output_video_path, wait_time=5, num_loops=3):
    """
    Automate the process of loading two JSON files and recording the animation.
    
    Args:
        json1_path (str): Path to the first JSON file
        json2_path (str): Path to the second JSON file
        output_video_path (str): Path where the video should be saved
        wait_time (int): Time to wait for animation to load in seconds
        num_loops (int): Number of animation loops to record with different camera angles
    """
    # Load and parse the first JSON file to get animation length
    with open(json1_path, 'r') as f:
        json1_data = json.load(f)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set download directory to current directory
    download_dir = os.path.dirname(os.path.abspath(output_video_path))
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
    })
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Copy JSON files to public directory
        shutil.copy(json1_path, "public/test.json")
        shutil.copy(json2_path, "public/test2.json")
        
        # Navigate to the viewer
        driver.get("http://localhost:8080")
        
        # Wait for the scene to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mocap"))
        )
        
        # Wait for models to load
        time.sleep(wait_time)
        
        # Get the canvas element for mouse interactions
        canvas = driver.find_element(By.CSS_SELECTOR, "#mocap canvas")
        
        # Find and click the record button
        record_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Record')]"))
        )
        record_button.click()
        
        # Calculate single loop duration
        animation_length = len(json1_data["time"]) / 60  # Assuming 60fps
        
        # Define camera positions for different views
        camera_positions = [
            {"rotation": 0, "height": 3},    # Front view
            {"rotation": 90, "height": 3},   # Side view
            {"rotation": 180, "height": 3},  # Back view
            {"rotation": 45, "height": 5},   # High angle diagonal view
        ]
        
        # Record multiple loops with different camera angles
        actions = ActionChains(driver)
        
        for loop in range(num_loops):
            print(f"Recording loop {loop + 1} of {num_loops}...")
            
            # Set camera position for this loop
            pos = camera_positions[loop % len(camera_positions)]
            
            # Rotate camera using mouse drag
            actions.move_to_element(canvas)
            actions.click_and_hold()
            actions.move_by_offset(pos["rotation"], 0)  # Horizontal rotation
            actions.release()
            actions.perform()
            
            # Adjust camera height using keyboard
            current_height = 3  # Default height
            target_height = pos["height"]
            height_diff = target_height - current_height
            
            if height_diff > 0:
                for _ in range(int(height_diff * 2)):  # Multiply by 2 for finer control
                    actions.send_keys(Keys.PAGE_UP).perform()
            else:
                for _ in range(int(-height_diff * 2)):
                    actions.send_keys(Keys.PAGE_DOWN).perform()
            
            # Wait for one complete animation cycle
            time.sleep(animation_length)
        
        # Find and click the stop button
        stop_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Stop Recording')]"))
        )
        stop_button.click()
        
        # Wait for download to complete
        time.sleep(2)
        
        # Move the downloaded file to the desired location
        downloaded_file = os.path.join(download_dir, "animation-recording.webm")
        if os.path.exists(downloaded_file):
            shutil.move(downloaded_file, output_video_path)
            print(f"Video saved to: {output_video_path}")
        else:
            print("Warning: Recording file not found in downloads directory")
        
    finally:
        # Clean up
        driver.quit()
        
        # Remove temporary JSON files
        if os.path.exists("public/test.json"):
            os.remove("public/test.json")
        if os.path.exists("public/test2.json"):
            os.remove("public/test2.json")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automate animation recording')
    parser.add_argument('json1', help='Path to first JSON file')
    parser.add_argument('json2', help='Path to second JSON file')
    parser.add_argument('output', help='Path for output video file')
    parser.add_argument('--wait', type=int, default=5, help='Wait time for loading in seconds')
    parser.add_argument('--loops', type=int, default=3, help='Number of animation loops to record with different camera angles')
    
    args = parser.parse_args()
    
    automate_recording(args.json1, args.json2, args.output, args.wait, args.loops)