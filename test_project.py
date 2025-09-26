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

 Start with basic tests and make them more
    sophisticated as we implement the actual functions.
    """
    # Test with valid coordinates
    # For now, we expect None since function isn't implemented
    result = fetch_weather_data(51.5074, -0.1278)  # London coordinates
    assert result is None  # Will change once implemented

    # TODO: Add tests for error handling
    # TODO: Add tests with mocked API responses


def test_parse_current_weather():
    """
    Test the parse_current_weather function
    """
    # Test with None input (current behavior)
    result = parse_current_weather(None)
    assert result is None

    # TODO: Add tests with sample weather data
    # TODO: Add tests for malformed data


def test_analyze_patterns():
    """
    Test the analyze_patterns function
    """
    # Test with empty data
    result = analyze_patterns([])
    assert isinstance(result, dict)
    assert "status" in result

    # Test with sample data (basic test for now)
    sample_data = [{"temperature": 20}]
    result = analyze_patterns(sample_data)
    assert isinstance(result, dict)
    assert "patterns_detected" in result

    # TODO: Add more sophisticated pattern tests
