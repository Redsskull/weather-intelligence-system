"""
Weather Intelligence System - CS50p Final Project
Main application file for weather data analysis and pattern recognition.

This file must be named 'project.py' per CS50 requirements.
"""

def main():
    """
    Main function
    This is the entry point of the entire application.
    """
    print("Weather Intelligence System v1.0")
    print("=" * 40)

    # Example coordinates for London, UK
    latitude = 51.5074
    longitude = -0.1278
    location_name = "London, UK"

    print(f"Fetching weather data for {location_name}...")

    # Step 1: Fetch weather data
    weather_data = fetch_weather_data(latitude, longitude)

    if weather_data is None:
        print("❌ Failed to fetch weather data")
        return

    # Step 2: Parse the current weather
    current_weather = parse_current_weather(weather_data)

    if current_weather is None:
        print("❌ Failed to parse weather data")
        return

    # Step 3: Display current weather
    print("\n🌤️  Current Weather:")
    print(f"Temperature: {current_weather.get('temperature', 'N/A')}°C")
    print(f"Pressure: {current_weather.get('pressure', 'N/A')} hPa")
    print(f"Humidity: {current_weather.get('humidity', 'N/A')}%")
    print(f"Wind Speed: {current_weather.get('wind_speed', 'N/A')} m/s")
    print(f"Conditions: {current_weather.get('conditions', 'N/A')}")

    # Step 4: Analyze patterns (basic for now)
    pattern_analysis = analyze_patterns([current_weather])

    print("\n📊 Pattern Analysis:")
    print(f"Status: {pattern_analysis.get('status', 'N/A')}")


def fetch_weather_data(lat, lon):
    """
    Fetch weather data from met.no API

    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate

    Returns:
        dict: Weather data JSON response or None if failed

    This function handles the HTTP request to the Norwegian
    Meteorological Institute API. It's free and doesn't require an API key!
    """
    # TODO: Implement HTTP request to met.no API
    # For now, return None to indicate not implemented
    print("⚠️  fetch_weather_data() not implemented yet")
    return None


def parse_current_weather(data):
    """
    Parse current weather from API response

    Args:
        data (dict): Raw weather data from API

    Returns:
        dict: Structured weather information or None if failed

   This function extracts the specific data we care about
    from the complex API response structure.
    """
    # TODO: Implement parsing logic
    # For now, return None to indicate not implemented
    print("⚠️  parse_current_weather() not implemented yet")
    return None


def analyze_patterns(data):
    """
    Basic pattern analysis of weather data

    Args:
        data (list): List of weather data points

    Returns:
        dict: Pattern analysis results

    Teaching note: This function will grow to become quite sophisticated,
    but we start simple and build up complexity.
    """
    # TODO: Implement pattern analysis
    # For now, return a basic status
    return {
        "status": "Analysis not implemented yet",
        "patterns_detected": 0,
        "trend": "unknown"
    }


if __name__ == "__main__":
    main()
