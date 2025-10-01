"""
Configuration management utilities for weather intelligence system

This module handles loading and managing configuration settings,
including location data and application preferences.
"""

import json


def load_config():
    """
    Load configuration from config/locations.json

    Returns:
        dict: Configuration data or default values
    """
    try:
        with open('config/locations.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded successfully")
        return config
    except FileNotFoundError:
        print("⚠️  Config file not found, using defaults")
        return {
            "default_location": "London, UK",
            "locations": {
                "London, UK": {"latitude": 51.5074, "longitude": -0.1278}
            },
            "settings": {"save_historical_data": True}
        }
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {"default_location": "London, UK", "locations": {}, "settings": {}}


def get_location_coordinates(location_name, config):
    """
    Get coordinates for a location from config

    Args:
        location_name (str): Name of the location
        config (dict): Configuration data

    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    locations = config.get('locations', {})

    if location_name in locations:
        loc_data = locations[location_name]
        return loc_data['latitude'], loc_data['longitude']
    else:
        print(f"❌ Location '{location_name}' not found in config")
        return None, None


def select_location(config):
    """
    Let user select a location from available options

    Args:
        config (dict): Configuration data

    Returns:
        str: Selected location name or None if cancelled
    """
    locations = config.get('locations', {})

    if not locations:
        print("❌ No locations available in config")
        return None

    print("\n🌍 Available Locations:")
    location_list = list(locations.keys())

    for i, location in enumerate(location_list, 1):
        coords = locations[location]
        print(f"  {i}. {location} ({coords['latitude']}, {coords['longitude']})")

    print(f"  0. Use default ({config.get('default_location', 'London, UK')})")

    try:
        choice = input("\nSelect location (0-{}): ".format(len(location_list)))
        choice_num = int(choice)

        if choice_num == 0:
            return config.get('default_location')
        elif 1 <= choice_num <= len(location_list):
            return location_list[choice_num - 1]
        else:
            print("❌ Invalid selection")
            return None

    except ValueError:
        print("❌ Please enter a number")
        return None
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return None


def get_setting(config, setting_name, default_value=None):
    """
    Get a specific setting value from configuration

    Args:
        config (dict): Configuration data
        setting_name (str): Name of the setting
        default_value: Default value if setting not found

    Returns:
        Setting value or default_value
    """
    settings = config.get('settings', {})
    return settings.get(setting_name, default_value)


def validate_coordinates(latitude, longitude):
    """
    Validate that coordinates are within valid ranges

    Args:
        latitude (float): Latitude value
        longitude (float): Longitude value

    Returns:
        bool: True if coordinates are valid
    """
    try:
        lat = float(latitude)
        lon = float(longitude)

        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        else:
            print(f"❌ Coordinates out of range: lat={lat} (must be -90 to 90), lon={lon} (must be -180 to 180)")
            return False
    except (ValueError, TypeError):
        print("❌ Coordinates must be numeric values")
        return False


def add_location_to_config(config_path, name, latitude, longitude, timezone=None):
    """
    Add a new location to the configuration file

    Args:
        config_path (str): Path to configuration file
        name (str): Location name
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        timezone (str, optional): Timezone identifier

    Returns:
        bool: True if successfully added
    """
    if not validate_coordinates(latitude, longitude):
        return False

    try:
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Add new location
        new_location = {
            "latitude": float(latitude),
            "longitude": float(longitude)
        }

        if timezone:
            new_location["timezone"] = timezone

        config["locations"][name] = new_location

        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Added location '{name}' to configuration")
        return True

    except Exception as e:
        print(f"❌ Error adding location to config: {e}")
        return False
