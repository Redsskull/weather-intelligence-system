"""
Weather Intelligence System - CS50p Final Project
Main application file for weather data analysis and pattern recognition.

This file must be named 'project.py' per CS50 requirements.
"""

import requests
import json
import time


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
    print(f"Conditions: {translate_code(current_weather.get('symbol_code', 'unknown'), 'weather_symbol')}")

    print(f"Precipitation: {current_weather.get('precipitation_mm', 0)} mm (next hour)")
    print(f"Rain Chance: {current_weather.get('precipitation_probability', 0)}%")


    # Step 4: Analyze patterns
    pattern_analysis = analyze_patterns([current_weather])

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




def fetch_weather_data(lat, lon):
    """
    Fetch weather data from met.no API

    Args:
        lat (float): Latitude coordinate (-90 to 90)
        lon (float): Longitude coordinate (-180 to 180)

    Returns:
        dict: Weather data JSON response or None if failed
    """

    # Step 1: Build the API URL
    # met.no compact version
    base_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    params = {
        "lat": lat,  # Latitude (North/South position)
        "lon": lon,  # Longitude (East/West position)
    }

    # Step 2: Set up headers (REQUIRED by met.no Terms of Service)
    # User-Agent identifies the application to the API server
    headers = {"User-Agent": "WeatherIntelligenceSystem/1.0 (CS50 Educational Project)"}

    # Step 3: Make the HTTP request with error handling
    try:
        print(f"🌍 Requesting weather data for coordinates ({lat}, {lon})...")

        # HTTP GET request
        response = requests.get(base_url, params=params, headers=headers, timeout=10)

        # Step 4: Check if the request was successful
        # HTTP status codes: 200 = OK, 4xx = client error, 5xx = server error
        if response.status_code == 200:
            print("✅ Successfully received weather data")

            # Convert the JSON response to a Python dictionary
            weather_data = response.json()
            return weather_data

        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"   Error message: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Request timed out - API server took too long to respond")
        return None

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check your internet connection")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Unexpected error making API request: {e}")
        return None

    except json.JSONDecodeError:
        print("❌ Invalid JSON response from API")
        return None


def parse_current_weather(data):
    """
    Parse current weather from API response

    Args:
        data (dict): Raw weather data from API

    Returns:
        dict: Structured weather information or None if failed
    """
    try:
        # Navigate to the current weather data
        timeseries = data['properties']['timeseries']
        current_data = timeseries[0]['data']['instant']['details']

        # Extract current measurements
        weather = {
            'temperature': current_data.get('air_temperature'),
            'pressure': current_data.get('air_pressure_at_sea_level'),
            'humidity': current_data.get('relative_humidity'),
            'wind_speed': current_data.get('wind_speed'),
            'wind_direction': current_data.get('wind_from_direction'),
            'cloud_cover': current_data.get('cloud_area_fraction')
        }

        # Extract forecast data (precipitation and conditions)
        forecast_data = timeseries[0]['data']

        # Get weather symbol and translate it
        symbol_code = 'unknown'
        if 'next_1_hours' in forecast_data and 'summary' in forecast_data['next_1_hours']:
            symbol_code = forecast_data['next_1_hours']['summary'].get('symbol_code', 'unknown')

        weather['symbol_code'] = symbol_code


        # Get precipitation data
        if 'next_1_hours' in forecast_data and 'details' in forecast_data['next_1_hours']:
            precip_details = forecast_data['next_1_hours']['details']
            weather['precipitation_mm'] = precip_details.get('precipitation_amount', 0)
            weather['precipitation_probability'] = precip_details.get('probability_of_precipitation', 0)
        else:
            weather['precipitation_mm'] = 0
            weather['precipitation_probability'] = 0

        # Get timestamp
        weather['timestamp'] = timeseries[0]['time']

        print("✅ Successfully parsed weather data")
        return weather

    except KeyError as e:
        print(f"❌ Missing expected key in weather data: {e}")
        return None

    except IndexError as e:
        print(f"❌ Weather data structure error: {e}")
        return None

    except Exception as e:
        print(f"❌ Unexpected error parsing weather data: {e}")
        return None


def analyze_patterns(data):
    """
    Basic pattern analysis of weather data

    Args:
        data (list): List of weather data points

    Returns:
        dict: Pattern analysis results
    """
    if not data or len(data) == 0:
        return {
            "status": "No data to analyze",
            "patterns_detected": 0,
            "trend": "unknown",
            "data_points": 0
        }

    # For now, I only have one data point (current weather)
    current_weather = data[0]
    data_points = len(data)

    # Basic data quality analysis
    analysis = {
        "status": "Analysis complete",
        "data_points": data_points,
        "timestamp": current_weather.get('timestamp', 'unknown'),
        "patterns_detected": 0,
        "trend": "insufficient_data" if data_points < 2 else "unknown"
    }

    # Analyze current conditions
    temp = current_weather.get('temperature')
    humidity = current_weather.get('humidity')
    pressure = current_weather.get('pressure')
    precipitation = current_weather.get('precipitation_mm', 0)

    # Basic condition analysis
    conditions = []

    if temp is not None:
        if temp < 0:
            conditions.append("freezing_temperature")
        elif temp > 30:
            conditions.append("hot_temperature")
        elif 20 <= temp <= 25:
            conditions.append("comfortable_temperature")

    if humidity is not None:
        if humidity > 80:
            conditions.append("high_humidity")
        elif humidity < 30:
            conditions.append("low_humidity")

    if pressure is not None:
        if pressure < 1000:
            conditions.append("low_pressure")
        elif pressure > 1030:
            conditions.append("high_pressure")

    if precipitation > 0:
        if precipitation < 0.5:
            conditions.append("light_precipitation")
        elif precipitation > 5:
            conditions.append("heavy_precipitation")
        else:
            conditions.append("moderate_precipitation")

    analysis["conditions_detected"] = conditions
    analysis["patterns_detected"] = len(conditions)

    # Generate human-readable summary
    if len(conditions) == 0:
        analysis["summary"] = "Normal weather conditions"
    else:
        analysis["summary"] = f"Detected {len(conditions)} notable conditions: {', '.join(conditions)}"

    return analysis



def translate_code(code, code_type):
    """
    Universal translator for weather codes and conditions

    Args:
        code (str): The code to translate
        code_type (str): Type of code ('weather_symbol' or 'condition')

    Returns:
        str: Human-readable translation
    """

    # All translation maps in one place
    translation_maps = {
        'weather_symbol': {
            'clearsky_day': '☀️ Clear sky',
            'clearsky_night': '🌙 Clear night',
            'fair_day': '🌤️ Fair weather',
            'fair_night': '🌙 Fair night',
            'partlycloudy_day': '⛅ Partly cloudy',
            'partlycloudy_night': '☁️ Partly cloudy night',
            'cloudy': '☁️ Cloudy',
            'rainshowers_day': '🌦️ Rain showers',
            'rainshowers_night': '🌧️ Night showers',
            'rain': '🌧️ Rain',
            'snow': '❄️ Snow',
            'snowshowers_day': '🌨️ Snow showers',
            'thunderstorm': '⛈️ Thunderstorm',
            'fog': '🌫️ Fog'
        },

        'condition': {
            'freezing_temperature': '🧊 Freezing conditions',
            'hot_temperature': '🔥 Hot weather',
            'comfortable_temperature': '😌 Comfortable temperature',
            'high_humidity': '💧 Very humid',
            'low_humidity': '🏜️ Very dry',
            'low_pressure': '📉 Low pressure (storm possible)',
            'high_pressure': '📈 High pressure (stable weather)',
            'light_precipitation': '🌦️ Light rain/snow',
            'moderate_precipitation': '🌧️ Moderate rain/snow',
            'heavy_precipitation': '⛈️ Heavy rain/snow'
        }
    }

    # Get the right translation map
    translation_map = translation_maps.get(code_type, {})

    # Return the translation or fallback
    return translation_map.get(code, f"❓ {code}")



if __name__ == "__main__":
    main()
