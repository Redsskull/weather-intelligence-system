"""
Data persistence utilities for weather intelligence system

This module handles saving and loading weather data for historical analysis
and provides functions for managing weather data files.
"""

import json
import os
import glob
from datetime import datetime


def save_weather_data(weather_data, location_name):
    """
    Save weather data to a file for historical analysis

    Args:
        weather_data (dict): Parsed weather data
        location_name (str): Name of the location

    Returns:
        str: Filename if successful, None if failed
    """
    # Ensure data directory exists
    os.makedirs('data/historical', exist_ok=True)

    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/historical/{location_name.replace(' ', '_').replace(',', '')}_{timestamp}.json"

    # Add metadata
    save_data = {
        'location': location_name,
        'saved_at': datetime.now().isoformat(),
        'weather': weather_data
    }

    try:
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"💾 Weather data saved to {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to save weather data: {e}")
        return None


def load_historical_data(location_name=None):
    """
    Load historical weather data from saved files

    Args:
        location_name (str, optional): Filter by location name

    Returns:
        list: List of historical weather data
    """
    historical_data = []

    if not os.path.exists('data/historical'):
        print("📁 No historical data directory found")
        return []

    # Get all JSON files in historical directory
    pattern = 'data/historical/*.json'
    if location_name:
        safe_location = location_name.replace(' ', '_').replace(',', '')
        pattern = f'data/historical/{safe_location}_*.json'

    files = glob.glob(pattern)

    for filename in sorted(files):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                historical_data.append(data)
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    print(f"📊 Loaded {len(historical_data)} historical data points")
    return historical_data


def get_historical_summary(location_name=None):
    """
    Get summary statistics of historical data

    Args:
        location_name (str, optional): Filter by location name

    Returns:
        dict: Summary statistics
    """
    historical_data = load_historical_data(location_name)

    if not historical_data:
        return {"status": "No historical data available", "count": 0}

    temperatures = []
    humidity_values = []
    pressure_values = []

    for entry in historical_data:
        weather = entry.get('weather', {})
        if weather.get('temperature') is not None:
            temperatures.append(weather['temperature'])
        if weather.get('humidity') is not None:
            humidity_values.append(weather['humidity'])
        if weather.get('pressure') is not None:
            pressure_values.append(weather['pressure'])

    summary = {
        "status": "Summary complete",
        "count": len(historical_data),
        "date_range": {
            "first": historical_data[0]['saved_at'] if historical_data else None,
            "last": historical_data[-1]['saved_at'] if historical_data else None
        }
    }

    if temperatures:
        summary["temperature"] = {
            "min": min(temperatures),
            "max": max(temperatures),
            "avg": round(sum(temperatures) / len(temperatures), 1)
        }

    if humidity_values:
        summary["humidity"] = {
            "min": min(humidity_values),
            "max": max(humidity_values),
            "avg": round(sum(humidity_values) / len(humidity_values), 1)
        }

    if pressure_values:
        summary["pressure"] = {
            "min": min(pressure_values),
            "max": max(pressure_values),
            "avg": round(sum(pressure_values) / len(pressure_values), 1)
        }

    return summary


def cleanup_old_files(max_files=100):
    """
    Clean up old historical data files to prevent disk space issues

    Args:
        max_files (int): Maximum number of files to keep

    Returns:
        int: Number of files removed
    """
    if not os.path.exists('data/historical'):
        return 0

    files = glob.glob('data/historical/*.json')
    files.sort(key=os.path.getmtime)  # Sort by modification time

    if len(files) <= max_files:
        return 0

    files_to_remove = files[:-max_files]  # Keep the newest max_files
    removed_count = 0

    for filename in files_to_remove:
        try:
            os.remove(filename)
            removed_count += 1
        except Exception as e:
            print(f"❌ Error removing {filename}: {e}")

    if removed_count > 0:
        print(f"🧹 Cleaned up {removed_count} old weather data files")

    return removed_count
