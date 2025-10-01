"""
Error handling utilities for weather intelligence system

This module contains all error handling functions and error message definitions
for providing helpful troubleshooting information to users.
"""

# Error message definitions
ERROR_MESSAGES = {
    'network_error': {
        'title': '🌐 Network Connection Problem',
        'message': 'Cannot connect to the weather service.',
        'tips': [
            '• Check your internet connection',
            '• Try again in a few moments',
            '• Make sure you\'re not behind a restrictive firewall'
        ]
    },
    'api_timeout': {
        'title': '⏰ Request Timeout',
        'message': 'The weather service is taking too long to respond.',
        'tips': [
            '• The service might be busy - try again',
            '• Check if your internet connection is slow',
            '• Wait a minute and retry'
        ]
    },
    'api_error': {
        'title': '🚫 Weather Service Error',
        'message': 'The weather service returned an error.',
        'tips': [
            '• The service might be temporarily down',
            '• Try a different location',
            '• Check if coordinates are valid (lat: -90 to 90, lon: -180 to 180)'
        ]
    },
    'data_parsing_error': {
        'title': '📊 Data Processing Error',
        'message': 'Could not understand the weather data format.',
        'tips': [
            '• This might be a temporary service issue',
            '• Try again in a few minutes',
            '• If it persists, the weather service may have changed their format'
        ]
    },
    'missing_data_field': {
        'title': '📋 Missing Weather Data Field',
        'message': 'The weather service response is missing expected information.',
        'tips': [
            '• The weather service may have changed their data format',
            '• Try a different location',
            '• This location might not have complete weather data available'
        ]
    },
    'incomplete_data_structure': {
        'title': '📊 Incomplete Weather Data',
        'message': 'The weather data structure is not complete.',
        'tips': [
            '• The weather service might be having issues',
            '• Try again in a few minutes',
            '• Some locations may have limited data availability'
        ]
    },
    'config_error': {
        'title': '⚙️ Configuration Error',
        'message': 'Problem with configuration file.',
        'tips': [
            '• Check that config/locations.json exists',
            '• Verify the JSON format is correct',
            '• Make sure all required fields are present'
        ]
    }
}


def display_error_help(error_type, details=None):
    """
    Display helpful error messages with troubleshooting tips

    Args:
        error_type (str): Type of error encountered
        details (str, optional): Additional error details
    """
    error_info = ERROR_MESSAGES.get(error_type, {
        'title': '❓ Unknown Error',
        'message': 'An unexpected error occurred.',
        'tips': ['• Try running the program again', '• Check if all files are in place']
    })

    print(f"\n{error_info['title']}")
    print(f"{error_info['message']}")
    if details:
        print(f"Details: {details}")

    print("\n💡 Troubleshooting Tips:")
    for tip in error_info['tips']:
        print(f"   {tip}")
    print()
