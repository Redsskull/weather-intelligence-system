"""
Translation utilities for weather codes and conditions

This module contains all translation dictionaries and functions
for converting weather codes into human-readable text.
"""

# Weather symbol translations
WEATHER_SYMBOL_MAP = {
    "clearsky_day": "☀️ Clear sky",
    "clearsky_night": "🌙 Clear night",
    "fair_day": "🌤️ Fair weather",
    "fair_night": "🌙 Fair night",
    "partlycloudy_day": "⛅ Partly cloudy",
    "partlycloudy_night": "☁️ Partly cloudy night",
    "cloudy": "☁️ Cloudy",
    "rainshowers_day": "🌦️ Rain showers",
    "rainshowers_night": "🌧️ Night showers",
    "rain": "🌧️ Rain",
    "lightrain": "🌦️ Light rain",
    "heavyrain": "⛈️ Heavy rain",
    "drizzle": "🌦️ Drizzle",
    "snow": "❄️ Snow",
    "lightsnow": "🌨️ Light snow",
    "heavysnow": "❄️ Heavy snow",
    "sleet": "🌨️ Sleet",
    "snowshowers_day": "🌨️ Snow showers",
    "thunderstorm": "⛈️ Thunderstorm",
    "fog": "🌫️ Fog",
    "mist": "🌫️ Mist",
}

# Weather condition translations
CONDITION_MAP = {
    "freezing_temperature": "🧊 Freezing conditions",
    "hot_temperature": "🔥 Hot weather",
    "comfortable_temperature": "😌 Comfortable temperature",
    "very_cold_temperature": "🧊 Very cold conditions",
    "warm_temperature": "🌡️ Warm conditions",
    "high_humidity": "💧 Very humid",
    "moderate_humidity": "💧 Moderately humid",
    "low_humidity": "🏜️ Very dry",
    "low_pressure": "📉 Low pressure (storm possible)",
    "high_pressure": "📈 High pressure (stable weather)",
    "below_average_pressure": "📉 Below average pressure",
    "above_average_pressure": "📈 Above average pressure",
    "light_precipitation": "🌦️ Light rain/snow",
    "moderate_precipitation": "🌧️ Moderate rain/snow",
    "heavy_precipitation": "⛈️ Heavy rain/snow",
    "potential_precipitation": "🌦️ Potential precipitation",
    "high_wind_warning": "💨 High wind warning",
    "moderate_wind_warning": "💨 Moderate wind warning",
    "light_wind_condition": "🍃 Light wind condition",
    "freezing_precipitation_warning": "🧊 Freezing precipitation (ice) warning",
    "snow_rain_mix_warning": "🌨️ Snow/rain mix (sleet) warning",
    "very_high_precipitation_probability": "⛈️ Very high chance of precipitation",
    "high_precipitation_probability": "🌧️ High chance of precipitation",
    "moderate_precipitation_probability": "🌦️ Moderate chance of precipitation",
    "overcast_conditions": "☁️ Overcast conditions",
    "mostly_cloudy": "⛅ Mostly cloudy",
    "partly_cloudy": "⛅ Partly cloudy",
    "clear_sky_conditions": "☀️ Clear sky conditions",
    "humid_and_warm_condition": "🌡️ Humid and warm conditions",
    "snow_precipitation_expected": "❄️ Snow expected",
    "mix_precipitation_expected": "🌨️ Mixed rain/snow expected",
    "high_wind_warning_forecast": "💨 High wind warning forecast",
    "increasing_wind_forecast": "💨 Increasing wind forecast",
    "storm_warning": "⛈️ Storm warning",
    "storm_prediction": "⚠️ Storm prediction",
    "clearing_trend": "🌤️ Clearing trend",
    # Forecast trend conditions
    "warming_trend": "🌡️ Temperature rising",
    "cooling_trend": "❄️ Temperature dropping",
    "pressure_rising": "🌪️ Pressure increasing",
    "pressure_dropping": "⚠️ Pressure dropping",
    "precipitation_expected": "🌧️ Rain/snow expected",
    "precipitation_soon": "☔ Precipitation coming soon",
    "light_precipitation_trend": "🌦️ Light precipitation expected",
}

# All translation maps in one place
TRANSLATION_MAPS = {"weather_symbol": WEATHER_SYMBOL_MAP, "condition": CONDITION_MAP}


def translate_code(code, code_type):
    """
    Universal translator for weather codes and conditions

    Args:
        code (str): The code to translate
        code_type (str): Type of code ('weather_symbol' or 'condition')

    Returns:
        str: Human-readable translation
    """
    # Handle None or empty code values
    if not code:
        return "🌤️ Unknown"

    translation_map = TRANSLATION_MAPS.get(code_type, {})
    result = translation_map.get(code)

    # If not found in the map, provide a smart fallback based on code_type
    if result is None:
        if code_type == "weather_symbol":
            # For weather symbols, try to infer from partial matches
            if "clear" in code.lower():
                return "☀️ Clear"
            elif "cloud" in code.lower():
                return "☁️ Cloudy"
            elif "rain" in code.lower():
                return "🌧️ Rain"
            elif "snow" in code.lower():
                return "❄️ Snow"
            elif "storm" in code.lower():
                return "⛈️ Storm"
            elif "fog" in code.lower() or "mist" in code.lower():
                return "🌫️ Fog"
            else:
                # For unknown codes in valid type, return format expected by tests
                return f"❓ {code}"
        elif code_type == "condition":
            # For conditions, return a generic description
            return f"❓ {code}"
        else:
            # For unknown code types, return a generic fallback with question mark
            return f"❓ {code}"

    return result
