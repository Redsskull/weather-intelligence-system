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
        # Check if this is the Go collector format (has location, current_weather, forecast at root level)
        if 'current_weather' in data and 'forecast' in data:
            # This is the full structure from Go collector
            current_weather = data.get('current_weather', {})
            forecast_data = data.get('forecast', [])
        else:
            # This might be just current weather data or other format
            current_weather = data
            forecast_data = data.get('forecast', []) if 'forecast' in data else []
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

    # Analyze current conditions with enhanced analysis
    conditions = []

    if temp is not None:
        if temp < 0:
            conditions.append("freezing_temperature")
        elif temp > 30:
            conditions.append("hot_temperature")
        elif 20 <= temp <= 25:
            conditions.append("comfortable_temperature")
        elif temp < 5:  # Cold condition
            conditions.append("very_cold_temperature")
        elif temp > 25:  # Warm condition
            conditions.append("warm_temperature")

    if humidity is not None:
        if humidity > 80:
            conditions.append("high_humidity")
        elif humidity > 60:
            conditions.append("moderate_humidity")
        elif humidity < 30:
            conditions.append("low_humidity")

    if pressure is not None:
        if pressure < 1000:
            conditions.append("low_pressure")
        elif pressure > 1030:
            conditions.append("high_pressure")
        elif pressure < 1013:  # Below average
            conditions.append("below_average_pressure")
        elif pressure > 1020:  # Above average
            conditions.append("above_average_pressure")

    if precipitation > 0:
        if precipitation < 0.5:
            conditions.append("light_precipitation")
        elif precipitation > 5:
            conditions.append("heavy_precipitation")
        else:
            conditions.append("moderate_precipitation")
    elif precipitation == 0 and current_weather.get('symbol_code', '').startswith('rain'):
        # Sometimes symbol shows rain but measurement is 0, still add condition
        conditions.append("potential_precipitation")
    
    # Enhanced analysis - adding detailed weather condition analysis
    if isinstance(current_weather, dict):
        wind_speed = current_weather.get('wind_speed')
        wind_direction = current_weather.get('wind_direction')
        cloud_cover = current_weather.get('cloud_cover')
        precipitation_prob = current_weather.get('precipitation_probability', 0)
        
        # Storm analysis - make thresholds more sensitive
        if wind_speed is not None:
            if wind_speed > 15:  # Lowered threshold
                conditions.append("high_wind_warning")
            elif wind_speed > 8:  # More realistic moderate wind
                conditions.append("moderate_wind_warning")
            elif wind_speed > 3:  # Light breeze
                conditions.append("light_wind_condition")
        
        # Cloud cover analysis with more sensitivity
        if cloud_cover is not None:
            if cloud_cover > 90:
                conditions.append("overcast_conditions")
            elif cloud_cover > 70:
                conditions.append("mostly_cloudy")
            elif cloud_cover > 40:
                conditions.append("partly_cloudy")
            elif cloud_cover < 20:
                conditions.append("clear_sky_conditions")
        
        # Enhanced precipitation analysis
        if precipitation > 0 and temp is not None:
            if temp < 0:
                conditions.append("freezing_precipitation_warning")  # Ice/sleet warning
            elif temp < 4 and precipitation > 0.5:
                conditions.append("snow_rain_mix_warning")  # Sleet warning
        
        # Precipitation probability analysis - more sensitive
        if precipitation_prob > 70:
            conditions.append("very_high_precipitation_probability")
        elif precipitation_prob > 40:
            conditions.append("high_precipitation_probability")
        elif precipitation_prob > 20:
            conditions.append("moderate_precipitation_probability")
        
        # Additional atmospheric analysis
        if temp is not None and humidity is not None:
            # Calculate heat index when appropriate
            if temp > 20 and humidity > 60:
                conditions.append("humid_and_warm_condition")

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

    # Analyze near-term forecast (next 6-12 hours) with enhanced storm/rain/snow analysis
    near_term = forecast_data[:12]  # Next 12 hours
    if len(near_term) > 0:
        # Temperature trend analysis - made more sensitive
        temps = [f.get('temperature', current_temp) for f in near_term if f.get('temperature') is not None]
        if temps:
            temp_change = temps[-1] - current_temp
            if temp_change > 1.5:  # Lowered threshold
                insights["conditions"].append("warming_trend")
                insights["highlights"].append(f"🌡️  Temperature rising by {temp_change:.1f}°C in next {min(12, len(near_term))} hours")
            elif temp_change < -1.5:  # Lowered threshold
                insights["conditions"].append("cooling_trend")
                insights["highlights"].append(f"❄️  Temperature dropping by {abs(temp_change):.1f}°C in next {min(12, len(near_term))} hours")
            elif abs(temp_change) > 0.5:  # Detect even small changes
                if temp_change > 0:
                    insights["highlights"].append(f"🌡️  Slight temperature rise of {temp_change:.1f}°C expected")
                else:
                    insights["highlights"].append(f"❄️  Slight temperature drop of {abs(temp_change):.1f}°C expected")

        # Pressure trend analysis for storm warnings - made more sensitive
        pressures = [f.get('pressure', current_pressure) for f in near_term if f.get('pressure') is not None]
        if pressures:
            pressure_change = pressures[-1] - current_pressure
            if pressure_change > 2:  # Lowered threshold
                insights["conditions"].append("pressure_rising")
                insights["highlights"].append(f"🌪️  Pressure increasing by {pressure_change:.1f} hPa - improving weather expected")
            elif pressure_change < -2:  # Lowered threshold
                insights["conditions"].append("pressure_dropping")
                insights["highlights"].append(f"⚠️  Pressure dropping by {abs(pressure_change):.1f} hPa - potential weather changes")
            elif abs(pressure_change) > 0.5:  # Detect small changes
                if pressure_change > 0:
                    insights["highlights"].append(f"📈  Slight pressure rise of {pressure_change:.1f} hPa")
                else:
                    insights["highlights"].append(f"📉  Slight pressure drop of {abs(pressure_change):.1f} hPa")

        # Enhanced precipitation analysis with rain/snow/storm warnings
        precipitations = [f.get('precipitation_mm', 0) for f in near_term]
        precipitation_probs = [f.get('precipitation_probability', 0) for f in near_term]
        temps_with_precip = [f.get('temperature', current_temp) for f in near_term if f.get('precipitation_mm', 0) > 0]
        
        if any(p > 0 for p in precipitations):
            total_precip = sum(precipitations)
            max_precip_prob = max(precipitation_probs) if precipitation_probs else 0
            
            # Determine if it's rain, snow, or mix based on temperature
            cold_precip_hours = [i for i, f in enumerate(near_term) if f.get('temperature', current_temp) < 2 and f.get('precipitation_mm', 0) > 0]
            warm_precip_hours = [i for i, f in enumerate(near_term) if f.get('temperature', current_temp) > 4 and f.get('precipitation_mm', 0) > 0]
            mix_precip_hours = [i for i, f in enumerate(near_term) if 2 <= f.get('temperature', current_temp) <= 4 and f.get('precipitation_mm', 0) > 0]
            
            precip_type = "precipitation_expected"
            if len(cold_precip_hours) > len(warm_precip_hours) and len(cold_precip_hours) > len(mix_precip_hours):
                precip_type = "snow_precipitation_expected"
                insights["highlights"].append(f"❄️  {total_precip:.1f}mm of snow expected in next {min(12, len(near_term))} hours")
            elif len(mix_precip_hours) > 0:
                precip_type = "mix_precipitation_expected" 
                insights["highlights"].append(f"🌨️  {total_precip:.1f}mm of mixed rain/snow expected in next {min(12, len(near_term))} hours")
            else:
                insights["highlights"].append(f"🌧️  {total_precip:.1f}mm of rain expected in next {min(12, len(near_term))} hours")
            
            insights["conditions"].append(precip_type)
            
            # Add probability information
            if max_precip_prob > 50:
                insights["highlights"].append(f"⚠️  High confidence ({max_precip_prob:.0f}%) in precipitation forecast")
            elif max_precip_prob > 20:
                insights["highlights"].append(f"📊 {max_precip_prob:.0f}% chance of precipitation")
        elif any(p > 0 for p in precipitations[:3]):  # Next 3 hours
            insights["conditions"].append("precipitation_soon")
            insights["highlights"].append("☔ Precipitation expected in next 3 hours")
        else:
            # Check if precipitation was expected but not happening (clearing trend)
            if current_weather.get('precipitation_mm', 0) > 0 and all(p == 0 for p in precipitations):
                insights["highlights"].append("🌤️  Precipitation clearing - weather improving")
                insights["conditions"].append("clearing_trend")

        # Wind analysis for storm warnings - made more sensitive
        winds = [f.get('wind_speed', 0) for f in near_term if f.get('wind_speed') is not None]
        if winds:
            max_wind = max(winds)
            avg_wind = sum(winds) / len(winds)
            wind_change = max_wind - current_weather.get('wind_speed', 0) if current_weather.get('wind_speed') is not None else 0
            
            if max_wind > 12:  # Lowered threshold
                insights["conditions"].append("high_wind_warning_forecast")
                insights["highlights"].append(f"💨 Strong winds up to {max_wind:.1f} m/s expected in next {min(12, len(near_term))} hours")
            elif wind_change > 3:  # Lowered threshold
                insights["conditions"].append("increasing_wind_forecast")
                insights["highlights"].append(f"💨 Wind speeds increasing to {max_wind:.1f} m/s in next {min(12, len(near_term))} hours")
            elif wind_change > 1.5:  # Detect smaller increases
                insights["highlights"].append(f"💨 Wind speeds increasing to {max_wind:.1f} m/s")
            
            # Also check for decreasing winds
            min_wind = min(winds)
            wind_change_min = min_wind - current_weather.get('wind_speed', 0) if current_weather.get('wind_speed') is not None else 0
            if wind_change_min < -1.5:  # Wind decreasing
                insights["highlights"].append(f"💨 Wind speeds decreasing to {min_wind:.1f} m/s")

        # Humidity trend analysis
        humidities = [f.get('humidity', current_weather.get('humidity', 0)) for f in near_term if f.get('humidity') is not None]
        if humidities:
            avg_humidity = sum(humidities) / len(humidities)
            humidity_change = avg_humidity - current_weather.get('humidity', 0) if current_weather.get('humidity') is not None else 0
            if humidity_change > 10:  # Significant increase
                insights["highlights"].append(f"💧 Humidity increasing significantly (Δ{humidity_change:.1f}%) - possible rain")
            elif humidity_change < -10:  # Significant decrease
                insights["highlights"].append(f"🏜️ Humidity decreasing significantly (Δ{humidity_change:.1f}%) - drier conditions")

    # Analyze medium-term forecast (next 24-48 hours) with enhanced storm/rain/snow analysis
    medium_term = forecast_data[:48]  # Next 48 hours
    if len(medium_term) > 24:
        # Temperature extremes - made more sensitive
        temps_medium = [f.get('temperature') for f in medium_term if f.get('temperature') is not None]
        if temps_medium:
            max_temp = max(temps_medium)
            min_temp = min(temps_medium)
            
            # Detect significant temperature changes
            temp_range = max_temp - min_temp
            if temp_range > 8:  # Large temperature swing
                insights["highlights"].append(f"🌡️  Large temperature swing of {temp_range:.1f}°C expected")
            elif temp_range > 5:  # Moderate temperature swing
                insights["highlights"].append(f"🌡️  Moderate temperature swing of {temp_range:.1f}°C expected")
            
            if max_temp > 25:
                insights["highlights"].append(f"🔥 High of {max_temp:.1f}°C expected in next 48 hours")
            if min_temp < 5:
                insights["highlights"].append(f"🧊 Low of {min_temp:.1f}°C expected in next 48 hours")
            if min_temp < 0:
                insights["highlights"].append(f"🧊 Freezing temperatures down to {min_temp:.1f}°C expected in next 48 hours")

        # Extended precipitation analysis with type differentiation
        total_precip_medium = sum(f.get('precipitation_mm', 0) for f in medium_term)
        cold_hours = [f for f in medium_term if f.get('temperature', 10) < 2 and f.get('precipitation_mm', 0) > 0]
        warm_hours = [f for f in medium_term if f.get('temperature', 10) > 4 and f.get('precipitation_mm', 0) > 0]
        mix_hours = [f for f in medium_term if 2 <= f.get('temperature', 10) <= 4 and f.get('precipitation_mm', 0) > 0]
        
        if total_precip_medium > 0:
            if len(cold_hours) > len(warm_hours) and len(cold_hours) > len(mix_hours):
                insights["highlights"].append(f"❄️ Snow ({total_precip_medium:.1f}mm) expected in next 48 hours")
            elif len(mix_hours) > 0:
                insights["highlights"].append(f"🌨️ Mixed precipitation ({total_precip_medium:.1f}mm) expected in next 48 hours")
            elif total_precip_medium > 10:
                insights["highlights"].append(f"💦 Heavy rain ({total_precip_medium:.1f}mm) expected in next 48 hours")
            else:
                insights["highlights"].append(f"🌧️ Rain ({total_precip_medium:.1f}mm) expected in next 48 hours")
        elif total_precip_medium == 0 and any(f.get('precipitation_mm', 0) > 0 for f in forecast_data[:12]):
            # If no further precipitation but some was in near term, suggest clearing
            insights["highlights"].append(f"🌤️  Precipitation clearing in next 48 hours")
        
        # Storm and severe weather analysis - made more sensitive
        winds_medium = [f.get('wind_speed', 0) for f in medium_term if f.get('wind_speed') is not None]
        if winds_medium:
            max_wind_medium = max(winds_medium)
            avg_wind_medium = sum(winds_medium) / len(winds_medium) if winds_medium else 0
            
            if max_wind_medium > 18:  # Lowered threshold
                insights["highlights"].append(f"💨 Strong winds up to {max_wind_medium:.1f} m/s expected in next 48 hours")
                insights["conditions"].append("high_wind_warning")
            elif max_wind_medium > 12:  # More realistic threshold
                insights["highlights"].append(f"💨 Moderate winds up to {max_wind_medium:.1f} m/s expected in next 48 hours")
            elif avg_wind_medium > 8:  # High average winds
                insights["highlights"].append(f"💨 Sustained moderate winds (avg {avg_wind_medium:.1f} m/s) expected")
        
        # Pressure pattern analysis for storm prediction - made more sensitive
        pressures_medium = [f.get('pressure', current_pressure) for f in medium_term if f.get('pressure') is not None]
        if len(pressures_medium) > 1:
            pressure_trend = pressures_medium[-1] - pressures_medium[0]
            if pressure_trend < -5:  # Lowered threshold
                insights["highlights"].append(f"⚠️ Pressure drop ({pressure_trend:.1f} hPa) - changing weather expected in next 48 hours")
                if pressure_trend < -10:
                    insights["conditions"].append("storm_prediction")
            elif pressure_trend > 5:  # Lowered threshold
                insights["highlights"].append(f"🌪️ Pressure rise ({pressure_trend:.1f} hPa) - improving weather expected in next 48 hours")
            elif abs(pressure_trend) > 1:  # Detect small changes
                trend_type = "rise" if pressure_trend > 0 else "drop"
                insights["highlights"].append(f"📊 Small {trend_type} in pressure ({pressure_trend:.1f} hPa) expected")

    return insights
