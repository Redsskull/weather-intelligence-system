"""
Test file for translation utilities

Tests all translation functions and dictionaries in utils/translations.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.translations import translate_code, WEATHER_SYMBOL_MAP, CONDITION_MAP


def test_translate_code_universal():
    """Test universal translate_code function"""
    # Test weather symbols
    result = translate_code("fair_day", "weather_symbol")
    assert result == "🌤️ Fair weather"

    # Test conditions
    result = translate_code("comfortable_temperature", "condition")
    assert result == "😌 Comfortable temperature"

    # Test unknown code type
    result = translate_code("some_code", "unknown_type")
    assert result == "❓ some_code"

    # Test unknown code in valid type
    result = translate_code("unknown_weather", "weather_symbol")
    assert result == "❓ unknown_weather"


def test_weather_symbol_map_completeness():
    """Test that weather symbol map has expected entries"""
    # Test key symbols exist
    expected_symbols = [
        "clearsky_day",
        "clearsky_night",
        "fair_day",
        "fair_night",
        "partlycloudy_day",
        "partlycloudy_night",
        "cloudy",
        "rainshowers_day",
        "rainshowers_night",
        "rain",
        "snow",
        "snowshowers_day",
        "thunderstorm",
        "fog",
    ]

    for symbol in expected_symbols:
        assert symbol in WEATHER_SYMBOL_MAP
        assert len(WEATHER_SYMBOL_MAP[symbol]) > 0


def test_condition_map_completeness():
    """Test that condition map has expected entries"""
    # Test key conditions exist
    expected_conditions = [
        "freezing_temperature",
        "hot_temperature",
        "comfortable_temperature",
        "high_humidity",
        "low_humidity",
        "low_pressure",
        "high_pressure",
        "light_precipitation",
        "moderate_precipitation",
        "heavy_precipitation",
    ]

    for condition in expected_conditions:
        assert condition in CONDITION_MAP
        assert len(CONDITION_MAP[condition]) > 0


def test_all_translations_have_emojis():
    """Test that all translations include emojis for better UX"""
    # Check weather symbols have emojis or special characters
    for symbol, translation in WEATHER_SYMBOL_MAP.items():
        # Should have at least one non-ASCII character (emoji)
        assert any(
            ord(char) > 127 for char in translation
        ), f"Translation for {symbol} lacks emoji"

    # Check conditions have emojis
    for condition, translation in CONDITION_MAP.items():
        assert any(
            ord(char) > 127 for char in translation
        ), f"Translation for {condition} lacks emoji"


def test_translation_consistency():
    """Test that translations are consistent and well-formatted"""
    all_translations = list(WEATHER_SYMBOL_MAP.values()) + list(CONDITION_MAP.values())

    for translation in all_translations:
        # Should not be empty
        assert len(translation.strip()) > 0

        # Should not start or end with whitespace
        assert translation == translation.strip()

        # Should not contain multiple consecutive spaces
        assert "  " not in translation
