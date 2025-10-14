"""
Intelligence-ready data persistence for pattern analysis and Go service integration.
Optimized for time-series analysis, trend detection, and statistical processing.
"""

import json
import os
import glob
from datetime import datetime, timedelta
import statistics


def save_to_timeseries(weather_data, location_name, coordinates=None):
    """
    Save weather data to location-based time-series files for intelligence analysis.

    This creates aggregated data files that Go services can easily process for:
    - Trend analysis over time
    - Pattern recognition
    - Anomaly detection
    - Statistical baseline calculation

    Args:
        weather_data (dict): Current weather reading
        location_name (str): Standardized location name
        coordinates (dict): Optional lat/lon for location metadata

    Returns:
        str: Path to timeseries file, or None if failed
    """
    # Create intelligence data directories
    os.makedirs("data/intelligence/timeseries", exist_ok=True)
    os.makedirs("data/intelligence/baselines", exist_ok=True)

    # Standardize location name for consistent file naming
    safe_location = location_name.replace(" ", "_").replace(",", "").replace("/", "_")
    timeseries_file = f"data/intelligence/timeseries/{safe_location}.json"

    # Current timestamp
    current_time = datetime.now().isoformat()
    weather_timestamp = weather_data.get("timestamp", current_time)

    # Load existing timeseries or create new
    try:
        if os.path.exists(timeseries_file):
            with open(timeseries_file, "r") as f:
                timeseries = json.load(f)
        else:
            timeseries = {
                "location": location_name,
                "coordinates": coordinates or {},
                "created_at": current_time,
                "readings": [],
                "metadata": {
                    "total_readings": 0,
                    "first_reading": current_time,
                    "last_reading": current_time,
                },
            }
    except Exception:
        timeseries = {
            "location": location_name,
            "coordinates": coordinates or {},
            "created_at": current_time,
            "readings": [],
            "metadata": {"total_readings": 0},
        }

    # Add new reading
    reading = {
        "timestamp": weather_timestamp,
        "saved_at": current_time,
        "temperature": weather_data.get("temperature"),
        "pressure": weather_data.get("pressure"),
        "humidity": weather_data.get("humidity"),
        "wind_speed": weather_data.get("wind_speed"),
        "wind_direction": weather_data.get("wind_direction"),
        "cloud_cover": weather_data.get("cloud_cover"),
        "precipitation_mm": weather_data.get("precipitation_mm", 0),
        "precipitation_probability": weather_data.get("precipitation_probability", 0),
        "symbol_code": weather_data.get("symbol_code", "unknown"),
    }

    timeseries["readings"].append(reading)

    # Update metadata
    timeseries["metadata"]["total_readings"] = len(timeseries["readings"])
    timeseries["metadata"]["last_reading"] = current_time
    if "first_reading" not in timeseries["metadata"]:
        timeseries["metadata"]["first_reading"] = current_time

    # Limit readings to prevent files from growing too large (keep last 1000)
    if len(timeseries["readings"]) > 1000:
        timeseries["readings"] = timeseries["readings"][-1000:]
        timeseries["metadata"]["note"] = "Limited to last 1000 readings"

    # Save updated timeseries
    try:
        with open(timeseries_file, "w") as f:
            json.dump(timeseries, f, indent=2)
        return timeseries_file
    except Exception:
        return None


def load_location_timeseries(location_name):
    """
    Load time-series data for a specific location.
    Optimized for Go service consumption and Python analysis.

    Args:
        location_name (str): Location to load data for

    Returns:
        dict: Time-series data structure, or None if not found
    """
    safe_location = location_name.replace(" ", "_").replace(",", "").replace("/", "_")
    timeseries_file = f"data/intelligence/timeseries/{safe_location}.json"

    if not os.path.exists(timeseries_file):
        return None

    try:
        with open(timeseries_file, "r") as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def calculate_location_baseline(location_name, days_back=30):
    """
    Calculate statistical baseline for a location for anomaly detection.

    Args:
        location_name (str): Location to analyze
        days_back (int): Number of days to use for baseline calculation

    Returns:
        dict: Baseline statistics, or None if insufficient data
    """
    timeseries = load_location_timeseries(location_name)
    if not timeseries or not timeseries["readings"]:
        return None

    # Filter readings to last N days
    cutoff_date = datetime.now() - timedelta(days=days_back)
    recent_readings = []

    for reading in timeseries["readings"]:
        try:
            reading_date = datetime.fromisoformat(
                reading["saved_at"].replace("Z", "+00:00")
            )
            if reading_date >= cutoff_date:
                recent_readings.append(reading)
        except:
            continue  # Skip readings with bad timestamps

    if len(recent_readings) < 3:
        return None

    # Calculate statistics for numeric fields
    baseline = {
        "location": location_name,
        "calculation_date": datetime.now().isoformat(),
        "readings_used": len(recent_readings),
        "days_analyzed": days_back,
        "statistics": {},
    }

    # Collect values for each metric
    metrics = ["temperature", "pressure", "humidity", "wind_speed", "precipitation_mm"]

    for metric in metrics:
        values = []
        for reading in recent_readings:
            value = reading.get(metric)
            if value is not None and isinstance(value, (int, float)):
                values.append(value)

        if len(values) >= 2:  # Need at least 2 values for statistics
            baseline["statistics"][metric] = {
                "mean": round(statistics.mean(values), 2),
                "median": round(statistics.median(values), 2),
                "min": min(values),
                "max": max(values),
                "std_dev": round(statistics.stdev(values) if len(values) > 1 else 0, 2),
                "sample_size": len(values),
            }

    # Save baseline for Go service consumption
    safe_location = location_name.replace(" ", "_").replace(",", "").replace("/", "_")
    baseline_file = f"data/intelligence/baselines/{safe_location}_baseline.json"

    try:
        with open(baseline_file, "w") as f:
            json.dump(baseline, f, indent=2)
        return baseline
    except Exception:
        return baseline  # Return data even if save failed


def prepare_go_analysis_input(location_names=None, max_days=7):
    """
    Prepare data for Go pattern analysis services.
    Creates standardized JSON input files that Go services can consume.

    Args:
        location_names (list): Specific locations to analyze, or None for all
        max_days (int): Maximum days of history to include

    Returns:
        str: Path to prepared analysis input file
    """
    os.makedirs("data/intelligence/go_input", exist_ok=True)

    # Get all locations if none specified
    if location_names is None:
        timeseries_dir = "data/intelligence/timeseries"
        if os.path.exists(timeseries_dir):
            location_files = glob.glob(f"{timeseries_dir}/*.json")
            location_names = []
            for file_path in location_files:
                filename = os.path.basename(file_path).replace(".json", "")
                location_names.append(filename)
        else:
            location_names = []

    analysis_input = {
        "request_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "created_at": datetime.now().isoformat(),
        "analysis_type": ["trends", "anomalies", "patterns"],
        "max_days_history": max_days,
        "locations": [],
    }

    cutoff_date = datetime.now() - timedelta(days=max_days)

    for location_name in location_names:
        timeseries = load_location_timeseries(location_name)
        if not timeseries:
            continue

        # Filter to recent readings
        recent_readings = []
        for reading in timeseries["readings"]:
            try:
                reading_date = datetime.fromisoformat(
                    reading["saved_at"].replace("Z", "+00:00")
                )
                if reading_date >= cutoff_date:
                    recent_readings.append(reading)
            except:
                continue

        if len(recent_readings) >= 2:  # Need minimum data for analysis
            location_data = {
                "name": timeseries["location"],
                "coordinates": timeseries.get("coordinates", {}),
                "readings_count": len(recent_readings),
                "readings": recent_readings,
                "metadata": {
                    "first_reading": (
                        recent_readings[0]["timestamp"] if recent_readings else None
                    ),
                    "last_reading": (
                        recent_readings[-1]["timestamp"] if recent_readings else None
                    ),
                },
            }
            analysis_input["locations"].append(location_data)

    # Save Go analysis input
    input_file = f"data/intelligence/go_input/analysis_request_{analysis_input['request_id']}.json"

    try:
        with open(input_file, "w") as f:
            json.dump(analysis_input, f, indent=2)

        return input_file
    except Exception:
        return None
