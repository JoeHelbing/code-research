#!/usr/bin/env python3
"""
Script to capture screenshots of all FastHTML styling experiments.
This script starts each experiment server, captures a screenshot, and then stops the server.
"""

import subprocess
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Set HOME to /root to fix Firefox permission issues
os.environ['HOME'] = '/root'

# List of all experiments
EXPERIMENTS = [
    ("01_inline_styles.py", "01_inline_styles.png"),
    ("02_global_styles.py", "02_global_styles.png"),
    ("03_dynamic_styles.py", "03_dynamic_styles.png"),
    ("04_style_dictionaries.py", "04_style_dictionaries.png"),
    ("05_component_styling.py", "05_component_styling.png"),
    ("06_css_class_generator.py", "06_css_class_generator.png"),
]

# Directory to store screenshots
SCREENSHOTS_DIR = Path("screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

def capture_screenshot(script_name: str, output_name: str, port: int = 5001):
    """
    Start a FastHTML server, capture a screenshot, and stop the server.

    Args:
        script_name: Name of the Python script to run
        output_name: Name of the output screenshot file
        port: Port number for the server (default: 5001)
    """
    print(f"\n{'='*60}")
    print(f"Processing: {script_name}")
    print(f"{'='*60}")

    # Start the FastHTML server
    print(f"Starting server for {script_name}...")
    process = subprocess.Popen(
        ["python", script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)

    try:
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"ERROR: Server failed to start!")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

        # Capture screenshot with Playwright
        print(f"Capturing screenshot...")
        with sync_playwright() as p:
            # Launch Chromium with extensive flags for container compatibility
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--single-process',
                    '--no-zygote',
                    '--disable-software-rasterizer',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            try:
                page.goto(f"http://localhost:{port}", timeout=10000)
                # Wait for page to fully load
                page.wait_for_load_state("networkidle", timeout=10000)

                # Take screenshot
                screenshot_path = SCREENSHOTS_DIR / output_name
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"Screenshot saved: {screenshot_path}")

            except Exception as e:
                print(f"ERROR: Failed to capture screenshot: {e}")
                return False
            finally:
                browser.close()

        print(f"✓ Successfully captured {output_name}")
        return True

    finally:
        # Stop the server
        print("Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        print("Server stopped.")

def main():
    """Main function to capture all screenshots."""
    print("\n" + "="*60)
    print("FastHTML Styling Experiments - Screenshot Capture")
    print("="*60)

    success_count = 0
    failed_experiments = []

    for script_name, output_name in EXPERIMENTS:
        if capture_screenshot(script_name, output_name):
            success_count += 1
        else:
            failed_experiments.append(script_name)

        # Wait a bit between experiments
        time.sleep(1)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total experiments: {len(EXPERIMENTS)}")
    print(f"Successful captures: {success_count}")
    print(f"Failed captures: {len(failed_experiments)}")

    if failed_experiments:
        print("\nFailed experiments:")
        for exp in failed_experiments:
            print(f"  - {exp}")

    print("\nScreenshots saved in:", SCREENSHOTS_DIR.absolute())
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
