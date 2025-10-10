"""
collects data from Go and loads it back to python using json!
I'm very proud of this one.
"""


import os
import json
import subprocess

from utils.errors import display_error_help


def call_go_collector(locations):
    """
    Execute Go data collector subprocess

    Args:
        locations (list): List of location dictionaries with 'name', 'lat', 'lon'

    Returns:
        bool: True if Go collector executed successfully, False otherwise

    Example:
        locations = [
            {'name': 'London, UK', 'lat': 51.5074, 'lon': -0.1278},
            {'name': 'Paris, France', 'lat': 48.8566, 'lon': 2.3522}
        ]
        success = call_go_collector(locations)
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
                "lon": float(loc.get("lon", 0))
            }
            go_locations.append(go_location)

        # Write to JSON file
        with open(input_file, 'w') as f:
            json.dump(go_locations, f, indent=2)



    except Exception as e:
        display_error_help('file_write_error', f"Could not write locations: {e}")
        return False

    # Execute Go data collector
    try:


        # Change to Go directory and run
        go_dir = "go-components/data-collector"
        result = subprocess.run(
            ["go", "run", "main.go"],
            cwd=go_dir,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        if result.returncode == 0:
            # Go data collector completed successfully
            return True
        else:
            return False

    except subprocess.TimeoutExpired:
        display_error_help('subprocess_timeout', "Go collector took too long")
        return False
    except FileNotFoundError:
        display_error_help('go_not_found', "Go not installed or not in PATH")
        return False
    except Exception as e:
        display_error_help('subprocess_error', str(e))
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
        display_error_help('file_not_found', f"Go output file not found: {output_file}")
        return None

    # Read and parse the JSON file
    try:
        with open(output_file, 'r') as f:
            weather_data = json.load(f)



        # Convert Go format to Python-friendly format (optional processing)
        processed_data = []
        for item in weather_data:
            current_weather = item.get('current_weather', {})

            processed_item = {
                'location': item.get('location', {}),
                'temperature': current_weather.get('temperature'),
                'pressure': current_weather.get('pressure'),
                'humidity': current_weather.get('humidity'),
                'wind_speed': current_weather.get('wind_speed'),
                'wind_direction': current_weather.get('wind_direction'),
                'cloud_cover': current_weather.get('cloud_cover'),
                'precipitation_mm': current_weather.get('precipitation_mm', 0),
                'precipitation_probability': current_weather.get('precipitation_probability', 0),
                'symbol_code': current_weather.get('symbol_code', 'unknown'),
                'success': item.get('success', False),
                'error': item.get('error', ''),
                'timestamp': current_weather.get('timestamp'),
                'forecast': item.get('forecast', [])  # Include forecast data for future use
            }
            processed_data.append(processed_item)

        return processed_data

    except json.JSONDecodeError as e:
        display_error_help('json_parsing_error', f"Invalid JSON in output file: {e}")
        return None
    except Exception as e:
        display_error_help('file_read_error', f"Could not read output file: {e}")
        return None
