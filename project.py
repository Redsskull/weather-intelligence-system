"""
Weather Intelligence System - CS50p Final Project
Main application file for weather data analysis and pattern recognition.

This file must be named 'project.py' per CS50 requirements.
"""

import json
import subprocess
import os

# Import custom modules
from utils.translations import translate_code
from utils.errors import display_error_help
from utils.geocoding import suggest_similar_cities
from utils.detection import get_user_location, get_manual_city_input
from utils.intelligence_persistence import save_to_timeseries
from utils.analyzer import analyze_patterns

def main():
    """
    Main function - orchestrates the weather intelligence system using Go data engine
    This is the entry point of the entire application.
    """
    print("Weather Intelligence System v1.0")
    print("=" * 40)

    # Ask user once for their location preference
    auto_location = get_user_location()

    if auto_location:
        # User chose auto-detection and it worked
        location_data = auto_location
        user_input = auto_location['display_name']
    else:
        # User chose manual entry OR auto-detection failed
        location_data = None
        while True:
            user_input = get_manual_city_input()

            if user_input and isinstance(user_input, str):
                # User entered a city name
                break
            else:
                print("❌ Please enter a city name")

        # Geocode the user input
        suggestions = suggest_similar_cities(user_input, limit=5)

        if not suggestions:
            print("❌ Could not find that city, exiting")
            return

        if len(suggestions) == 1:
            # Only one option, use it
            location_data = suggestions[0]
        else:
            # Multiple options, let user choose
            print(f"\n💡 Found multiple locations for '{user_input}':")
            for i, suggestion in enumerate(suggestions, 1):
                country = suggestion.get('country', 'Unknown')
                print(f"  {i}. {suggestion['display_name']} ({country})")

            try:
                choice = input(f"\nSelect 1-{len(suggestions)} (or Enter for #{1}): ").strip()
                if choice and choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(suggestions):
                        location_data = suggestions[choice_idx]
                    else:
                        location_data = suggestions[0]  # Default to first
                else:
                    location_data = suggestions[0]  # Default to first
            except (ValueError, KeyboardInterrupt):
                location_data = suggestions[0]  # Default to first

    # Extract location information
    location_name = location_data['display_name']
    latitude = location_data['lat']
    longitude = location_data['lon']

    # Show which method was used for transparency
    source = location_data.get('source', 'geocoding')
    if source == 'ip_detection':
        print(f"📍 Using detected location: {location_name}")
    else:
        print(f"🌍 Using specified location: {location_name}")

    print(f"Fetching weather data for {location_name}...")

    # Step 1: Use Go data engine to fetch weather data
    locations = [{'name': location_name, 'lat': latitude, 'lon': longitude}]
    weather_data_list = fetch_weather_data(locations)

    if weather_data_list is None or len(weather_data_list) == 0:
        print("❌ Failed to fetch weather data")
        return

    # Step 2: Parse the weather data from Go collector
    current_weather = parse_current_weather(weather_data_list[0])

    if current_weather is None:
        print("❌ Failed to parse weather data")
        return

    # Save weather data if enabled
    if True:  # Always save historical data
        save_to_timeseries(current_weather, location_name, {
            'lat': latitude,
            'lon': longitude
        })

    # Step 3: Display current weather
    print("\n🌤️  Current Weather:")
    print(f"Temperature: {current_weather.get('temperature', 'N/A')}°C")
    print(f"Pressure: {current_weather.get('pressure', 'N/A')} hPa")
    print(f"Humidity: {current_weather.get('humidity', 'N/A')}%")
    print(f"Wind Speed: {current_weather.get('wind_speed', 'N/A')} m/s")
    print(f"Conditions: {translate_code(current_weather.get('symbol_code', 'unknown'), 'weather_symbol')}")
    print(f"Precipitation: {current_weather.get('precipitation_mm', 0)} mm (next hour)")
    print(f"Rain Chance: {current_weather.get('precipitation_probability', 0)}%")

    # Step 4: Analyze patterns (Python's specialty - intelligence layer)
    # Pass the full weather data including forecasts
    pattern_analysis = analyze_patterns(weather_data_list[0])

    print("\n📊 Weather Analysis:")
    print(f"Status: {pattern_analysis.get('status', 'N/A')}")

    patterns_count = pattern_analysis.get('patterns_detected', 0)
    if patterns_count == 0:
        print("🟢 Normal weather conditions")
    else:
        print(f"🟡 {patterns_count} notable condition{'s' if patterns_count > 1 else ''} detected:")

        # Show each condition with nice formatting
        conditions = pattern_analysis.get('conditions_detected', [])
        for condition in conditions:
            readable_condition = translate_code(condition, 'condition')
            print(f"   • {readable_condition}")

    print(f"📈 Trend: {pattern_analysis.get('trend', 'unknown').replace('_', ' ').title()}")

    # Show forecast insights if available, or inform user about stable conditions
    forecast_highlights = pattern_analysis.get('forecast_highlights', [])
    if forecast_highlights:
        print("\n🔮 Forecast Insights:")
        for highlight in forecast_highlights[:5]:  # Show top 5 highlights
            print(f"   • {highlight}")
    elif pattern_analysis.get('forecast_hours', 0) > 0:
        # If we have forecast data but no significant insights, inform user
        print("\nWeather Outlook:")
        print("   • No significant weather changes expected in the near term")
        print("   • Current conditions are expected to continue")


def fetch_weather_data(locations):
    """
    Fetch weather data using Go data collector (high-performance engine)

    Args:
        locations (list): List of location dictionaries with 'name', 'lat', 'lon'

    Returns:
        list: List of weather data dictionaries or None if failed
    """
    # Delegate to Go data collector for fast, concurrent data collection
    success = call_go_collector(locations)

    if not success:
        display_error_help('go_collector_failed', 'Go data collector failed to execute')
        return None

    # Load the results from Go collector
    weather_data = load_go_collected_data()

    if weather_data is None:
        display_error_help('go_data_load_failed', 'Failed to load Go collector results')
        return None

    print(f"✅ Successfully collected weather data for {len(weather_data)} locations via Go engine")
    return weather_data


def parse_current_weather(go_weather_result):
    """
    Parse current weather from Go collector result

    Args:
        go_weather_result (dict): Weather data from Go collector

    Returns:
        dict: Structured weather information or None if failed
    """
    try:
        # Check if Go collection was successful
        if not go_weather_result.get('success', False):
            error_msg = go_weather_result.get('error', 'Unknown error')
            display_error_help('go_collection_error', f"Go collector error: {error_msg}")
            return None

        # Extract weather data from the processed structure (values already extracted to root level by load_go_collected_data)
        weather = {
            'temperature': go_weather_result.get('temperature'),
            'pressure': go_weather_result.get('pressure'),
            'humidity': go_weather_result.get('humidity'),
            'wind_speed': go_weather_result.get('wind_speed'),
            'wind_direction': go_weather_result.get('wind_direction'),
            'cloud_cover': go_weather_result.get('cloud_cover'),
            'precipitation_mm': go_weather_result.get('precipitation_mm', 0),
            'precipitation_probability': go_weather_result.get('precipitation_probability', 0),
            'symbol_code': go_weather_result.get('symbol_code', 'unknown'),
            'timestamp': go_weather_result.get('timestamp')
        }

        print("✅ Successfully parsed Go collector weather data")
        return weather

    except Exception as e:
        display_error_help('data_parsing_error', str(e))
        return None


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
    # Step 1: Create integration directory if it doesn't exist
    integration_dir = "data/integration"
    os.makedirs(integration_dir, exist_ok=True)

    # Step 2: Write locations to input file for Go to read
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

        print(f"📝 Wrote {len(go_locations)} locations to {input_file}")

    except Exception as e:
        display_error_help('file_write_error', f"Could not write locations: {e}")
        return False

    # Step 3: Execute Go data collector
    try:
        print("🚀 Launching Go data collector...")

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
            print("✅ Go data collector completed successfully")
            print("📊 Go collector output:")
            # Print the Go program's output (it has nice logging)
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            return True
        else:
            print("❌ Go data collector failed")
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
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

    # Step 1: Check if output file exists
    output_file = "data/integration/output_weather.json"

    if not os.path.exists(output_file):
        display_error_help('file_not_found', f"Go output file not found: {output_file}")
        return None

    # Step 2: Read and parse the JSON file
    try:
        with open(output_file, 'r') as f:
            weather_data = json.load(f)

        print(f"📊 Loaded weather data for {len(weather_data)} locations from Go collector")

        # Step 3: Convert Go format to Python-friendly format (optional processing)
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


if __name__ == "__main__":
    main()
