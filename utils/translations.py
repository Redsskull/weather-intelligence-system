"""
Translation utilities for weather codes and conditions

This module contains all translation dictionaries and functions
for converting weather codes into human-readable text.
"""

# Weather symbol translations
WEATHER_SYMBOL_MAP = {
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
    'lightrain': '🌦️ Light rain',
    'heavyrain': '⛈️ Heavy rain',
    'drizzle': '🌦️ Drizzle',
    'snow': '❄️ Snow',
    'lightsnow': '🌨️ Light snow',
    'heavysnow': '❄️ Heavy snow',
    'sleet': '🌨️ Sleet',
    'snowshowers_day': '🌨️ Snow showers',
    'thunderstorm': '⛈️ Thunderstorm',
    'fog': '🌫️ Fog',
    'mist': '🌫️ Mist'
}

# Weather condition translations
CONDITION_MAP = {
    'freezing_temperature': '🧊 Freezing conditions',
    'hot_temperature': '🔥 Hot weather',
    'comfortable_temperature': '😌 Comfortable temperature',
    'high_humidity': '💧 Very humid',
    'low_humidity': '🏜️ Very dry',
    'low_pressure': '📉 Low pressure (storm possible)',
    'high_pressure': '📈 High pressure (stable weather)',
    'light_precipitation': '🌦️ Light rain/snow',
    'moderate_precipitation': '🌧️ Moderate rain/snow',
    'heavy_precipitation': '⛈️ Heavy rain/snow',
    # Forecast trend conditions
    'warming_trend': '🌡️ Temperature rising',
    'cooling_trend': '❄️ Temperature dropping',
    'pressure_rising': '🌪️ Pressure increasing',
    'pressure_dropping': '⚠️ Pressure dropping',
    'precipitation_expected': '🌧️ Rain/snow expected',
    'precipitation_soon': '☔ Precipitation coming soon',
    'light_precipitation_trend': '🌦️ Light precipitation expected'
}

# All translation maps in one place
TRANSLATION_MAPS = {
    'weather_symbol': WEATHER_SYMBOL_MAP,
    'condition': CONDITION_MAP
}


def translate_code(code, code_type):
    """
    Universal translator for weather codes and conditions

    Args:
        code (str): The code to translate
        code_type (str): Type of code ('weather_symbol' or 'condition')

    Returns:
        str: Human-readable translation
    """
    translation_map = TRANSLATION_MAPS.get(code_type, {})
    return translation_map.get(code, f"❓ {code}")



