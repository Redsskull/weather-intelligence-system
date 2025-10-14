"""
Weather Intelligence System - CS50p Final Project
Main application file for weather data analysis and pattern recognition.

This file must be named 'project.py' per CS50 requirements.
"""

import sys
from datetime import datetime

# Import custom modules
from utils.translations import translate_code
from utils.errors import display_error_help
from utils.geocoding import suggest_similar_cities
from utils.detection import get_user_location, get_manual_city_input
from utils.intelligence_persistence import save_to_timeseries
from utils.analyzer import analyze_patterns
from utils.collection import call_go_collector, load_go_collected_data
from utils.forecast import display_weekly_forecast


def main():
    """
    Main function - orchestrates the weather intelligence system using Go data engine
    This is the entry point of the entire application.
    """
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "uninstall":
            show_uninstall_instructions()
            return
        elif command in ["-h", "--help", "help"]:
            show_help()
            return
        else:
            print(f"Unknown command: {command}")
            show_help()
            return

    print("Weather Intelligence System v1.0")
    print("=" * 40)

    # Get location from user or auto-detect
    location_data = get_location()
    if location_data is None:
        print("❌ Could not determine location, exiting")
        return

    # Extract location information
    location_name = location_data["display_name"]
    latitude = location_data["lat"]
    longitude = location_data["lon"]

    # Show which method was used for transparency
    source = location_data.get("source", "geocoding")
    if source == "ip_detection":
        print(f"📍 Using detected location: {location_name}")
    else:
        print(f"🌍 Using specified location: {location_name}")

    print(f"Fetching weather data for {location_name}...")

    # Fetch and process weather data
    weather_data = fetch_and_process_weather_data(location_name, latitude, longitude)
    if weather_data is None:
        print("❌ Failed to fetch or process weather data")
        return

    # Display current weather information
    display_current_weather(weather_data)

    # Analyze weather patterns and display analysis
    pattern_analysis = analyze_patterns(weather_data)
    display_weather_analysis(pattern_analysis)

    # Display forecast
    print("\n📅 Weekly Forecast:")
    display_weekly_forecast(weather_data)


def get_location():
    """
    Determine location either through auto-detection or user input
    
    Returns:
        dict: Location data with name, latitude, longitude, and source
    """
    # Ask user once for their location preference
    auto_location = get_user_location()

    if auto_location:
        # User chose auto-detection and it worked
        return auto_location
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
            return None

        if len(suggestions) == 1:
            # Only one option, use it
            location_data = suggestions[0]
        else:
            # Multiple options, let user choose
            print(f"\n💡 Found multiple locations for '{user_input}':")
            for i, suggestion in enumerate(suggestions, 1):
                country = suggestion.get("country", "Unknown")
                print(f"  {i}. {suggestion['display_name']} ({country})")

            try:
                choice = input(
                    f"\nSelect 1-{len(suggestions)} (or Enter for #{1}): "
                ).strip()
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

        return location_data


def fetch_and_process_weather_data(location_name, latitude, longitude):
    """
    Fetch weather data from the Go collector and process it
    
    Args:
        location_name (str): Name of the location
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location
    
    Returns:
        dict: Processed weather data or None if failed
    """
    # Use Go data engine to fetch weather data
    locations = [{"name": location_name, "lat": latitude, "lon": longitude}]
    weather_data_list = fetch_weather_data(locations)

    if weather_data_list is None or len(weather_data_list) == 0:
        print("❌ Failed to fetch weather data")
        return None

    # Parse the weather data from Go collector
    current_weather = parse_current_weather(weather_data_list[0])

    if current_weather is None:
        print("❌ Failed to parse weather data")
        return None

    # Save weather data if enabled
    if True:  # Always save historical data
        save_to_timeseries(
            current_weather, location_name, {"lat": latitude, "lon": longitude}
        )

    return weather_data_list[0]


def display_current_weather(current_weather):
    """
    Display current weather information to the user
    
    Args:
        current_weather (dict): Current weather data
    """
    print("\n🌤️  Current Weather:")
    print(f"Temperature: {current_weather.get('temperature', 'N/A')}°C")
    print(f"Pressure: {current_weather.get('pressure', 'N/A')} hPa")
    print(f"Humidity: {current_weather.get('humidity', 'N/A')}%")
    print(f"Wind Speed: {current_weather.get('wind_speed', 'N/A')} m/s")
    print(
        f"Conditions: {translate_code(current_weather.get('symbol_code', 'unknown'), 'weather_symbol')}"
    )
    print(f"Precipitation: {current_weather.get('precipitation_mm', 0)} mm (next hour)")
    print(f"Rain Chance: {current_weather.get('precipitation_probability', 0)}%")


def display_weather_analysis(pattern_analysis):
    """
    Display weather pattern analysis to the user
    
    Args:
        pattern_analysis (dict): Pattern analysis results
    """
    print("\n📊 Weather Analysis:")
    print(f"Status: {pattern_analysis.get('status', 'N/A')}")

    patterns_count = pattern_analysis.get("patterns_detected", 0)
    if patterns_count == 0:
        print("🟢 Normal weather conditions")
    else:
        print(
            f"🟡 {patterns_count} notable condition{'s' if patterns_count > 1 else ''} detected:"
        )

        # Show each condition with nice formatting
        conditions = pattern_analysis.get("conditions_detected", [])
        for condition in conditions:
            readable_condition = translate_code(condition, "condition")
            print(f"   • {readable_condition}")

    print(
        f"📈 Trend: {pattern_analysis.get('trend', 'unknown').replace('_', ' ').title()}"
    )

    # Show forecast insights if available, or inform user about stable conditions
    forecast_highlights = pattern_analysis.get("forecast_highlights", [])
    if forecast_highlights:
        print("\n🔮 Forecast Insights:")
        for highlight in forecast_highlights[:5]:  # Show top 5 highlights
            print(f"   • {highlight}")
    elif pattern_analysis.get("forecast_hours", 0) > 0:
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
        display_error_help("go_collector_failed", "Go data collector failed to execute")
        return None

    # Load the results from Go collector
    weather_data = load_go_collected_data()

    if weather_data is None:
        display_error_help("go_data_load_failed", "Failed to load Go collector results")
        return None

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
        if not go_weather_result.get("success", False):
            error_msg = go_weather_result.get("error", "Unknown error")
            display_error_help(
                "go_collection_error", f"Go collector error: {error_msg}"
            )
            return None

        # Extract weather data from the processed structure (values already extracted to root level by load_go_collected_data)
        weather = {
            "temperature": go_weather_result.get("temperature"),
            "pressure": go_weather_result.get("pressure"),
            "humidity": go_weather_result.get("humidity"),
            "wind_speed": go_weather_result.get("wind_speed"),
            "wind_direction": go_weather_result.get("wind_direction"),
            "cloud_cover": go_weather_result.get("cloud_cover"),
            "precipitation_mm": go_weather_result.get("precipitation_mm", 0),
            "precipitation_probability": go_weather_result.get(
                "precipitation_probability", 0
            ),
            "symbol_code": go_weather_result.get("symbol_code", "unknown"),
            "timestamp": go_weather_result.get("timestamp"),
        }

        return weather

    except Exception as e:
        display_error_help("data_parsing_error", str(e))
        return None


def get_forecast_for_time(forecast_data, target_time):
    """
    Helper function to get forecast closest to a specific time

    Args:
        forecast_data (list): List of forecast data points
        target_time (datetime): Target time to find forecast for

    Returns:
        dict: Forecast data point closest to the target time, or None
    """
    if not forecast_data:
        return None

    # Find forecast closest to target_time
    closest_forecast = forecast_data[0]
    closest_diff = abs(
        (
            datetime.fromisoformat(closest_forecast["timestamp"].replace("Z", "+00:00"))
            - target_time
        ).total_seconds()
    )

    for forecast in forecast_data:
        try:
            forecast_time = datetime.fromisoformat(
                forecast["timestamp"].replace("Z", "+00:00")
            )
            diff = abs((forecast_time - target_time).total_seconds())
            if diff < closest_diff:
                closest_diff = diff
                closest_forecast = forecast
        except ValueError:
            continue

    return closest_forecast


def show_uninstall_instructions():
    """Show instructions for uninstalling the Weather Intelligence System"""
    print("To uninstall the Weather Intelligence System, run:")
    print("  weather-uninstall")
    print("")
    print("This will remove all installed components including:")
    print("  - The main application files")
    print("  - Binary executables")
    print("  - Configuration changes to your shell")
    print("")
    print(
        "Note: You can also find the 'weather-uninstall' script in your PATH directory."
    )


def show_help():
    """Show help information for the weather command"""
    print("Weather Intelligence System v1.0")
    print("=" * 40)
    print("Usage: weather [command]")
    print("")
    print("Commands:")
    print("  (no command)    - Run the main weather intelligence system")
    print("  uninstall       - Show instructions for uninstalling the system")
    print("  -h, --help      - Show this help message")
    print("")
    print("Example:")
    print("  weather          - Get current weather and analysis")
    print("  weather uninstall - Show uninstall instructions")


if __name__ == "__main__":
    main()
