"""
Weather Intelligence System Analyzer Module

This module provides functions for analyzing weather patterns and trends.
"""




def analyze_patterns(data):
    """
    Enhanced pattern analysis of weather data including forecasts

    Args:
        data (dict): Weather data containing current_weather and forecast

    Returns:
        dict: Pattern analysis results with forecasts and trends
    """
    if not data:
        return {
            "status": "No data to analyze",
            "patterns_detected": 0,
            "trend": "unknown",
            "data_points": 0
        }

    # Extract current weather and forecast data
    if isinstance(data, dict):
        current_weather = data
        forecast_data = data.get('forecast', [])
        # If it's the processed format from load_go_collected_data, forecast is at root level
        if 'forecast' in data:
            forecast_data = data['forecast']
        else:
            forecast_data = []
    elif isinstance(data, list) and len(data) > 0:
        # Backward compatibility for list format
        current_weather = data[0]
        forecast_data = current_weather.get('forecast', []) if isinstance(current_weather, dict) else []
        data_points = len(data)
    else:
        current_weather = {}
        forecast_data = []
        data_points = 0

    # Calculate data points (current + forecast)
    data_points = 1 + len(forecast_data)

    # Basic data quality analysis
    analysis = {
        "status": "Analysis complete",
        "data_points": data_points,
        "timestamp": current_weather.get('timestamp', 'unknown') if isinstance(current_weather, dict) else 'unknown',
        "patterns_detected": 0,
        "trend": "insufficient_data" if data_points < 2 else "analyzing",
        "forecast_hours": len(forecast_data)
    }

    # Analyze current conditions
    if isinstance(current_weather, dict):
        temp = current_weather.get('temperature')
        humidity = current_weather.get('humidity')
        pressure = current_weather.get('pressure')
        precipitation = current_weather.get('precipitation_mm', 0)
    else:
        temp = humidity = pressure = None
        precipitation = 0

    # Basic condition analysis
    conditions = []

    if temp is not None:
        if temp < 0:
            conditions.append("freezing_temperature")
        elif temp > 30:
            conditions.append("hot_temperature")
        elif 20 <= temp <= 25:
            conditions.append("comfortable_temperature")

    if humidity is not None:
        if humidity > 80:
            conditions.append("high_humidity")
        elif humidity < 30:
            conditions.append("low_humidity")

    if pressure is not None:
        if pressure < 1000:
            conditions.append("low_pressure")
        elif pressure > 1030:
            conditions.append("high_pressure")

    if precipitation > 0:
        if precipitation < 0.5:
            conditions.append("light_precipitation")
        elif precipitation > 5:
            conditions.append("heavy_precipitation")
        else:
            conditions.append("moderate_precipitation")

    # Enhanced analysis with forecast data
    forecast_insights = []
    if len(forecast_data) > 0:
        forecast_insights = analyze_forecast_trends(forecast_data, current_weather)
        conditions.extend(forecast_insights.get('conditions', []))

    analysis["conditions_detected"] = conditions
    analysis["patterns_detected"] = len(conditions)
    analysis["forecast_insights"] = forecast_insights

    # Generate human-readable summary
    if len(conditions) == 0:
        analysis["summary"] = "Normal weather conditions"
    else:
        analysis["summary"] = f"Detected {len(conditions)} notable conditions: {', '.join(conditions)}"

    # Add forecast highlights if available
    if forecast_insights and 'highlights' in forecast_insights:
        analysis["forecast_highlights"] = forecast_insights['highlights']

    return analysis


def analyze_forecast_trends(forecast_data, current_weather):
    """
    Analyze forecast trends and identify upcoming weather patterns

    Args:
        forecast_data (list): List of forecast data points
        current_weather (dict): Current weather data

    Returns:
        dict: Forecast analysis results
    """
    if not forecast_data or len(forecast_data) == 0:
        return {"conditions": [], "highlights": []}

    insights = {
        "conditions": [],
        "highlights": []
    }

    # Get current values for comparison
    current_temp = current_weather.get('temperature', 0) if current_weather else 0
    current_pressure = current_weather.get('pressure', 1013) if current_weather else 1013

    # Analyze near-term forecast (next 6-12 hours)
    near_term = forecast_data[:12]  # Next 12 hours
    if len(near_term) > 0:
        # Temperature trend analysis
        temps = [f.get('temperature', current_temp) for f in near_term if f.get('temperature') is not None]
        if temps:
            temp_change = temps[-1] - current_temp
            if temp_change > 3:
                insights["conditions"].append("warming_trend")
                insights["highlights"].append(f"🌡️  Temperature rising by {temp_change:.1f}°C in next {min(12, len(near_term))} hours")
            elif temp_change < -3:
                insights["conditions"].append("cooling_trend")
                insights["highlights"].append(f"❄️  Temperature dropping by {abs(temp_change):.1f}°C in next {min(12, len(near_term))} hours")

        # Pressure trend analysis
        pressures = [f.get('pressure', current_pressure) for f in near_term if f.get('pressure') is not None]
        if pressures:
            pressure_change = pressures[-1] - current_pressure
            if pressure_change > 5:
                insights["conditions"].append("pressure_rising")
                insights["highlights"].append(f"🌪️  Pressure increasing by {pressure_change:.1f} hPa - improving weather expected")
            elif pressure_change < -5:
                insights["conditions"].append("pressure_dropping")
                insights["highlights"].append(f"⚠️  Pressure dropping by {abs(pressure_change):.1f} hPa - stormy weather possible")

        # Precipitation analysis
        precipitations = [f.get('precipitation_mm', 0) for f in near_term]
        if any(p > 0 for p in precipitations):
            total_precip = sum(precipitations)
            insights["conditions"].append("precipitation_expected")
            insights["highlights"].append(f"🌧️  {total_precip:.1f}mm of precipitation expected in next {min(12, len(near_term))} hours")
        elif any(p > 0 for p in precipitations[:3]):  # Next 3 hours
            insights["conditions"].append("precipitation_soon")
            insights["highlights"].append("☔ Precipitation expected in next 3 hours")

    # Analyze medium-term forecast (next 24-48 hours)
    medium_term = forecast_data[:48]  # Next 48 hours
    if len(medium_term) > 24:
        # Temperature extremes
        temps_medium = [f.get('temperature') for f in medium_term if f.get('temperature') is not None]
        if temps_medium:
            max_temp = max(temps_medium)
            min_temp = min(temps_medium)
            if max_temp > 25:
                insights["highlights"].append(f"🔥 High of {max_temp:.1f}°C expected in next 48 hours")
            if min_temp < 5:
                insights["highlights"].append(f"🧊 Low of {min_temp:.1f}°C expected in next 48 hours")

        # Extended precipitation
        total_precip_medium = sum(f.get('precipitation_mm', 0) for f in medium_term)
        if total_precip_medium > 10:
            insights["highlights"].append(f"💦 Heavy precipitation ({total_precip_medium:.1f}mm) expected in next 48 hours")

    return insights
