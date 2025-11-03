"""
collects data from Go and loads it back to python using json!
I'm very proud of this one.
"""

import os
import json
import subprocess
import platform
import shutil

from utils.errors import display_error_help


def call_go_collector(locations):
    """
    Execute Go data collector subprocess
    First tries to run go directly for development, then falls back to compiled binary
    """
    # Create integration directory if it doesn't exist
    integration_dir = "data/integration"
    os.makedirs(integration_dir, exist_ok=True)

    # Write locations to input file for Go to read
    input_file = os.path.join(integration_dir, "input_locations.json")

    try:
        # Convert Python location format to Go format
        go_locations = []
        for loc in locations:
            go_location = {
                "name": loc.get("name", "Unknown"),
                "lat": float(loc.get("lat", 0)),
                "lon": float(loc.get("lon", 0)),
            }
            go_locations.append(go_location)

        # Write to JSON file
        with open(input_file, "w") as f:
            json.dump(go_locations, f, indent=2)

    except Exception as e:
        display_error_help("file_write_error", f"Could not write locations: {e}")
        return False

    # First, try to run Go directly for development (go run)
    try:
        go_dir = "go-components/data-collector"
        # Check if the go directory and main.go exist
        if not os.path.exists(os.path.join(go_dir, "main.go")):
            raise FileNotFoundError("main.go not found in go-components/data-collector")

        # When running go run, we need to run from the go directory
        # But we also need to make sure the input file is accessible
        # Let's create a symbolic link or copy the input file to the expected location
        expected_input_dir = os.path.join(go_dir, "data", "integration")
        os.makedirs(expected_input_dir, exist_ok=True)
        expected_input_file = os.path.join(expected_input_dir, "input_locations.json")

        # Copy the input file to where Go expects it
        shutil.copy2(input_file, expected_input_file)

        # Run from the go directory
        result = subprocess.run(
            ["go", "run", "main.go"],
            cwd=go_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Clean up the copied file
        if os.path.exists(expected_input_file):
            os.remove(expected_input_file)

        if result.returncode == 0:
            return True
        # If go run fails, continue to try compiled binary
    except FileNotFoundError as e:
        # go command not found or main.go not found, continue to try compiled binary
        print(f"FileNotFoundError during go run: {e}")
        pass
    except subprocess.TimeoutExpired:
        display_error_help("subprocess_timeout", "Go collector took too long")
        return False
    except Exception as e:
        # Any other error with go run, continue to try compiled binary
        # But let's log the error for debugging
        print(f"Exception during go run: {e}")
        pass

    # Execute Go data collector using compiled binary
    try:
        # Determine the correct binary name based on the OS
        system = platform.system().lower()
        if system == "windows":
            binary_path = "./data-collector.exe"
        else:
            binary_path = "./data-collector"  # Linux/macOS

        # Use compiled binary directly (check will be part of subprocess call)
        result = subprocess.run(
            [binary_path], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            return True
        else:
            # Try without the leading
            if system == "windows":
                fallback_path = "data-collector.exe"
            else:
                fallback_path = "data-collector"

            result = subprocess.run(
                [fallback_path], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return True
            else:
                return False

    except subprocess.TimeoutExpired:
        display_error_help("subprocess_timeout", "Go collector took too long")
        return False
    except FileNotFoundError:
        display_error_help("go_binary_not_found", "Go binary not found and 'go' command not available")
        return False
    except Exception as e:
        display_error_help("subprocess_error", str(e))
        return False


def load_go_collected_data():
    """
    Read data from Go collector output

    Returns:
        list: List of weather data dictionaries, or None if failed

    Example return format:
        [
            {
                "location": {"name": "London, UK", "lat": 51.5074, "lon": -0.1278},
                "temperature": 15.2,
                "pressure": 1013.25,
                "humidity": 65.0,
                "wind_speed": 4.5,
                "success": true,
                "timestamp": "2025-09-26T15:00:00Z"
            }
        ]
    """

    # Check if output file exists
    output_file = "data/integration/output_weather.json"

    if not os.path.exists(output_file):
        display_error_help("file_not_found", f"Go output file not found: {output_file}")
        return None

    # Read and parse the JSON file
    try:
        with open(output_file, "r") as f:
            weather_data = json.load(f)

        # Convert Go format to Python-friendly format (optional processing)
        processed_data = []
        for item in weather_data:
            current_weather = item.get("current_weather", {})

            processed_item = {
                "location": item.get("location", {}),
                "temperature": current_weather.get("temperature"),
                "pressure": current_weather.get("pressure"),
                "humidity": current_weather.get("humidity"),
                "wind_speed": current_weather.get("wind_speed"),
                "wind_direction": current_weather.get("wind_direction"),
                "cloud_cover": current_weather.get("cloud_cover"),
                "precipitation_mm": current_weather.get("precipitation_mm", 0),
                "precipitation_probability": current_weather.get(
                    "precipitation_probability", 0
                ),
                "symbol_code": current_weather.get("symbol_code", "unknown"),
                "success": item.get("success", False),
                "error": item.get("error", ""),
                "timestamp": current_weather.get("timestamp"),
                "forecast": item.get(
                    "forecast", []
                ),  # Include forecast data for future use
            }
            processed_data.append(processed_item)

        return processed_data

    except json.JSONDecodeError as e:
        display_error_help("json_parsing_error", f"Invalid JSON in output file: {e}")
        return None
    except Exception as e:
        display_error_help("file_read_error", f"Could not read output file: {e}")
        return None
