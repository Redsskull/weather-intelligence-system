"""
Test cases for location detection functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from utils.detection import (
    detect_location_via_ip,
    _parse_ipapi_response,
    _parse_ip_api_response,
    ask_user_location_choice
)


def test_parse_ipapi_response():
    """Test parsing ipapi.co response"""
    # Valid response
    valid_data = {
        'city': 'San Francisco',
        'country_name': 'United States',
        'region': 'California',
        'latitude': 37.7749,
        'longitude': -122.4194
    }

    result = _parse_ipapi_response(valid_data)
    assert result is not None
    assert result['city'] == 'San Francisco'
    assert result['country'] == 'United States'
    assert result['lat'] == 37.7749
    assert result['lon'] == -122.4194
    assert result['source'] == 'ipapi.co'

    # Invalid response
    invalid_data = {'error': 'Invalid IP'}
    result = _parse_ipapi_response(invalid_data)
    assert result is None


def test_parse_ip_api_response():
    """Test parsing ip-api.com response"""
    # Valid response
    valid_data = {
        'status': 'success',
        'city': 'New York',
        'country': 'United States',
        'regionName': 'New York',
        'lat': 40.7128,
        'lon': -74.0060
    }

    result = _parse_ip_api_response(valid_data)
    assert result is not None
    assert result['city'] == 'New York'
    assert result['country'] == 'United States'
    assert result['lat'] == 40.7128
    assert result['lon'] == -74.0060
    assert result['source'] == 'ip-api.com'

    # Failed response
    failed_data = {'status': 'fail', 'message': 'Invalid query'}
    result = _parse_ip_api_response(failed_data)
    assert result is None


@patch('builtins.input', return_value='1')
def test_ask_user_location_choice_auto(mock_input):
    """Test user chooses auto-detection"""
    result = ask_user_location_choice()
    assert result == 'auto'


@patch('builtins.input', return_value='2')
def test_ask_user_location_choice_manual(mock_input):
    """Test user chooses manual entry"""
    result = ask_user_location_choice()
    assert result == 'manual'


if __name__ == "__main__":
    pytest.main([__file__])
