"""
Test file for Weather Intelligence System - CS50 Final Project

This file must be named 'test_project.py' per CS50 requirements.
All functions in project.py must and will be tested here using pytest.
"""

import pytest
from project import fetch_weather_data, parse_current_weather, analyze_patterns


def test_fetch_weather_data():
    """
    Test the fetch_weather_data function
    """
    # Test with valid coordinates (London)
    result = fetch_weather_data(51.5074, -0.1278)

    # Should return a dictionary with weather data
    assert result is not None
    assert isinstance(result, dict)
    assert 'type' in result  # GeoJSON feature
    assert 'properties' in result
    assert 'timeseries' in result['properties']
    assert len(result['properties']['timeseries']) > 0

    # Should have at least one weather data point
    timeseries = result['properties']['timeseries']
    assert len(timeseries) > 0
    assert 'time' in timeseries[0]
    assert 'data' in timeseries[0]



def test_parse_current_weather_real_api():
    """
    Test parse_current_weather with real API data (integration test)
    """
    # Get real weather data
    real_api_data = fetch_weather_data(51.5074, -0.1278)  # London

    # Parse the real data
    result = parse_current_weather(real_api_data)

    # Test structure and data types (not specific values)
    assert result is not None
    assert isinstance(result, dict)

    # Test that all expected keys exist
    expected_keys = ['temperature', 'pressure', 'humidity', 'wind_speed',
                    'symbol_code', 'precipitation_mm', 'timestamp']
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"

    # Test data types and reasonable ranges
    temp = result['temperature']
    assert isinstance(temp, (int, float)), "Temperature should be a number"
    assert -50 < temp < 60, f"Temperature {temp}°C seems unreasonable"

    humidity = result['humidity']
    assert isinstance(humidity, (int, float)), "Humidity should be a number"
    assert 0 <= humidity <= 100, f"Humidity {humidity}% should be 0-100%"

    pressure = result['pressure']
    assert isinstance(pressure, (int, float)), "Pressure should be a number"
    assert 900 < pressure < 1100, f"Pressure {pressure} hPa seems unreasonable"

    # Test that symbol_code is a string
    assert isinstance(result['symbol_code'], str)
    assert len(result['symbol_code']) > 0

    print(f"✅ Integration test passed with real data: {temp}°C, {humidity}% humidity")






def test_analyze_patterns():
    """
    Test the analyze_patterns function with various scenarios
    """
    # Test 1: Empty data
    result = analyze_patterns([])
    assert result['status'] == "No data to analyze"
    assert result['patterns_detected'] == 0
    assert result['data_points'] == 0

    # Test 2: Normal weather conditions
    normal_weather = [{
        'temperature': 22.0,        # Comfortable
        'humidity': 50.0,           # Normal
        'pressure': 1015.0,         # Normal
        'precipitation_mm': 0.0,    # No rain
        'timestamp': '2025-09-30T12:00:00Z'
    }]

    result = analyze_patterns(normal_weather)
    assert result['status'] == "Analysis complete"
    assert result['data_points'] == 1
    assert result['patterns_detected'] == 1  # Should detect comfortable_temperature
    assert 'comfortable_temperature' in result['conditions_detected']
    assert result['summary'] == "Detected 1 notable conditions: comfortable_temperature"

    # Test 3: Extreme weather conditions
    extreme_weather = [{
        'temperature': -5.0,        # Freezing
        'humidity': 95.0,           # High humidity
        'pressure': 980.0,          # Low pressure
        'precipitation_mm': 8.0,    # Heavy precipitation
        'timestamp': '2025-09-30T12:00:00Z'
    }]

    result = analyze_patterns(extreme_weather)
    assert result['data_points'] == 1
    assert result['patterns_detected'] == 4  # Should detect 4 conditions

    expected_conditions = ['freezing_temperature', 'high_humidity',
                            'low_pressure', 'heavy_precipitation']
    for condition in expected_conditions:
        assert condition in result['conditions_detected'], f"Should detect {condition}"

    # Test 4: Hot and dry conditions
    hot_dry_weather = [{
        'temperature': 35.0,        # Hot
        'humidity': 20.0,           # Low humidity
        'pressure': 1035.0,         # High pressure
        'precipitation_mm': 0.0,    # No rain
        'timestamp': '2025-09-30T12:00:00Z'
    }]

    result = analyze_patterns(hot_dry_weather)
    assert result['patterns_detected'] == 3  # hot_temperature, low_humidity, high_pressure
    assert 'hot_temperature' in result['conditions_detected']
    assert 'low_humidity' in result['conditions_detected']
    assert 'high_pressure' in result['conditions_detected']

    print("✅ All pattern analysis scenarios passed!")
