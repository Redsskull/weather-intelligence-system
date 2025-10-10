"""
Weather Intelligence System - CS50p Final Project
Main application file for weather data analysis and pattern recognition.

This file must be named 'project.py' per CS50 requirements.
"""

from datetime import datetime, date, timedelta
from collections import Counter, defaultdict
# Import custom modules
from utils.translations import translate_code
from utils.errors import display_error_help
from utils.geocoding import suggest_similar_cities
from utils.detection import get_user_location, get_manual_city_input
from utils.intelligence_persistence import save_to_timeseries
from utils.analyzer import analyze_patterns
from utils.collection import call_go_collector, load_go_collected_data

def main():
    """
    Main function - orchestrates the weather intelligence system using Go data engine
    This is the entry point of the entire application.
    """
    print("Weather Intelligence System v1.0")
    print("=" * 40)

    # Ask user once for their location preference
    auto_location = get_user_location()

    if auto_location:
        # User chose auto-detection and it worked
        location_data = auto_location
        user_input = auto_location['display_name']
    else:
        # User chose manual entry OR auto-detection failed
        location_data = None
        while True:
            user_input = get_manual_city_input()

            if user_input and isinstance(user_input, str):
                # User entered a city name
                break
            else:
                print("❌ Please enter a city name")

        # Geocode the user input
        suggestions = suggest_similar_cities(user_input, limit=5)

        if not suggestions:
            print("❌ Could not find that city, exiting")
            return

        if len(suggestions) == 1:
            # Only one option, use it
            location_data = suggestions[0]
        else:
            # Multiple options, let user choose
            print(f"\n💡 Found multiple locations for '{user_input}':")
            for i, suggestion in enumerate(suggestions, 1):
                country = suggestion.get('country', 'Unknown')
                print(f"  {i}. {suggestion['display_name']} ({country})")

            try:
                choice = input(f"\nSelect 1-{len(suggestions)} (or Enter for #{1}): ").strip()
                if choice and choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(suggestions):
                        location_data = suggestions[choice_idx]
                    else:
                        location_data = suggestions[0]  # Default to first
                else:
                    location_data = suggestions[0]  # Default to first
            except (ValueError, KeyboardInterrupt):
                location_data = suggestions[0]  # Default to first

    # Extract location information
    location_name = location_data['display_name']
    latitude = location_data['lat']
    longitude = location_data['lon']

    # Show which method was used for transparency
    source = location_data.get('source', 'geocoding')
    if source == 'ip_detection':
        print(f"📍 Using detected location: {location_name}")
    else:
        print(f"🌍 Using specified location: {location_name}")

    print(f"Fetching weather data for {location_name}...")

    # Step 1: Use Go data engine to fetch weather data
    locations = [{'name': location_name, 'lat': latitude, 'lon': longitude}]
    weather_data_list = fetch_weather_data(locations)

    if weather_data_list is None or len(weather_data_list) == 0:
        print("❌ Failed to fetch weather data")
        return

    # Step 2: Parse the weather data from Go collector
    current_weather = parse_current_weather(weather_data_list[0])

    if current_weather is None:
        print("❌ Failed to parse weather data")
        return

    # Save weather data if enabled
    if True:  # Always save historical data
        save_to_timeseries(current_weather, location_name, {
            'lat': latitude,
            'lon': longitude
        })

    # Step 3: Display current weather
    print("\n🌤️  Current Weather:")
    print(f"Temperature: {current_weather.get('temperature', 'N/A')}°C")
    print(f"Pressure: {current_weather.get('pressure', 'N/A')} hPa")
    print(f"Humidity: {current_weather.get('humidity', 'N/A')}%")
    print(f"Wind Speed: {current_weather.get('wind_speed', 'N/A')} m/s")
    print(f"Conditions: {translate_code(current_weather.get('symbol_code', 'unknown'), 'weather_symbol')}")
    print(f"Precipitation: {current_weather.get('precipitation_mm', 0)} mm (next hour)")
    print(f"Rain Chance: {current_weather.get('precipitation_probability', 0)}%")

    # Step 4: Analyze patterns (Python's specialty - intelligence layer)
    # Pass the full weather data including forecasts
    pattern_analysis = analyze_patterns(weather_data_list[0])

    print("\n📊 Weather Analysis:")
    print(f"Status: {pattern_analysis.get('status', 'N/A')}")

    patterns_count = pattern_analysis.get('patterns_detected', 0)
    if patterns_count == 0:
        print("🟢 Normal weather conditions")
    else:
        print(f"🟡 {patterns_count} notable condition{'s' if patterns_count > 1 else ''} detected:")

        # Show each condition with nice formatting
        conditions = pattern_analysis.get('conditions_detected', [])
        for condition in conditions:
            readable_condition = translate_code(condition, 'condition')
            print(f"   • {readable_condition}")

    print(f"📈 Trend: {pattern_analysis.get('trend', 'unknown').replace('_', ' ').title()}")

    # Show forecast insights if available, or inform user about stable conditions
    forecast_highlights = pattern_analysis.get('forecast_highlights', [])
    if forecast_highlights:
        print("\n🔮 Forecast Insights:")
        for highlight in forecast_highlights[:5]:  # Show top 5 highlights
            print(f"   • {highlight}")
    elif pattern_analysis.get('forecast_hours', 0) > 0:
        # If we have forecast data but no significant insights, inform user
        print("\nWeather Outlook:")
        print("   • No significant weather changes expected in the near term")
        print("   • Current conditions are expected to continue")

    # Display detailed hourly forecast for today and next 6 days
    print("\n📅 Weekly Forecast:")
    display_weekly_forecast(weather_data_list[0])


def fetch_weather_data(locations):
    """
    Fetch weather data using Go data collector (high-performance engine)

    Args:
        locations (list): List of location dictionaries with 'name', 'lat', 'lon'

    Returns:
        list: List of weather data dictionaries or None if failed
    """
    # Delegate to Go data collector for fast, concurrent data collection
    success = call_go_collector(locations)

    if not success:
        display_error_help('go_collector_failed', 'Go data collector failed to execute')
        return None

    # Load the results from Go collector
    weather_data = load_go_collected_data()

    if weather_data is None:
        display_error_help('go_data_load_failed', 'Failed to load Go collector results')
        return None


    return weather_data


def parse_current_weather(go_weather_result):
    """
    Parse current weather from Go collector result

    Args:
        go_weather_result (dict): Weather data from Go collector

    Returns:
        dict: Structured weather information or None if failed
    """
    try:
        # Check if Go collection was successful
        if not go_weather_result.get('success', False):
            error_msg = go_weather_result.get('error', 'Unknown error')
            display_error_help('go_collection_error', f"Go collector error: {error_msg}")
            return None

        # Extract weather data from the processed structure (values already extracted to root level by load_go_collected_data)
        weather = {
            'temperature': go_weather_result.get('temperature'),
            'pressure': go_weather_result.get('pressure'),
            'humidity': go_weather_result.get('humidity'),
            'wind_speed': go_weather_result.get('wind_speed'),
            'wind_direction': go_weather_result.get('wind_direction'),
            'cloud_cover': go_weather_result.get('cloud_cover'),
            'precipitation_mm': go_weather_result.get('precipitation_mm', 0),
            'precipitation_probability': go_weather_result.get('precipitation_probability', 0),
            'symbol_code': go_weather_result.get('symbol_code', 'unknown'),
            'timestamp': go_weather_result.get('timestamp')
        }


        return weather

    except Exception as e:
        display_error_help('data_parsing_error', str(e))
        return None


def display_weekly_forecast(go_weather_result):
    """
    Display compact weekly forecast showing today's hourly forecast and next 6 days

    Args:
        go_weather_result (dict): Weather data from Go collector including forecast
    """
    if not go_weather_result.get('forecast'):
        print("   • No detailed forecast data available")
        return

    # Get forecast data
    forecast_data = go_weather_result['forecast']

    # Group forecast by date
    forecast_by_date = {}
    for forecast_point in forecast_data:
        # Parse the timestamp to extract the date
        timestamp_str = forecast_point.get('timestamp', '')
        if timestamp_str:
            try:
                # Handle ISO format: "2025-10-10T07:00:00Z"
                forecast_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                date_key = forecast_time.strftime('%Y-%m-%d')

                if date_key not in forecast_by_date:
                    forecast_by_date[date_key] = []
                forecast_by_date[date_key].append(forecast_point)
            except ValueError:
                continue  # Skip invalid timestamps

    # Get today's date and next 6 days
    today = date.today()
    days_to_show = []

    # Add today
    days_to_show.append(today.strftime('%Y-%m-%d'))

    # Add next 6 days
    for i in range(1, 7):
        future_date = today + timedelta(days=i)
        days_to_show.append(future_date.strftime('%Y-%m-%d'))

    # Display forecasts in a more compact format
    for i, date_key in enumerate(days_to_show):
        if date_key in forecast_by_date:
            day_forecasts = forecast_by_date[date_key]
            day_obj = datetime.strptime(date_key, '%Y-%m-%d')

            # Format day name (Today, Tomorrow, or abbreviated day)
            if i == 0:
                day_name = "Today"
            elif i == 1:
                day_name = "Tomorrow"
            else:
                day_name = day_obj.strftime('%a')  # Abbreviated day name

            # For today, show compact hourly forecast with icons
            if i == 0:
                # Get key hourly forecasts for today - select representative times throughout the day
                if len(day_forecasts) > 0:
                    # Group forecasts by hour to find the best representative for each time period
                    hourly_forecasts = defaultdict(list)

                    for forecast in day_forecasts:
                        hour_time = datetime.fromisoformat(forecast['timestamp'].replace('Z', '+00:00'))
                        hour = hour_time.hour
                        hourly_forecasts[hour].append(forecast)

                    # Select forecasts for key times of day: early morning (7-9), late morning (10-11),
                    # noon (12), afternoon (15-16), evening (18-20)
                    selected_forecasts = []

                    # Define time periods and select first forecast from each period if available
                    time_periods = [
                        (range(6, 10), "early morning"),     # 6-9 AM
                        (range(10, 13), "late morning"),     # 10-12 AM
                        (range(13, 17), "afternoon"),        # 1-4 PM
                        (range(17, 21), "evening"),          # 5-8 PM
                        (range(21, 24), "night")             # 9-11 PM
                    ]

                    for period_range, period_name in time_periods:
                        # Look for forecasts in this time period
                        found_forecast = None
                        for hour in period_range:
                            if hour in hourly_forecasts and len(hourly_forecasts[hour]) > 0:
                                found_forecast = hourly_forecasts[hour][0]  # Take first one in the hour
                                break
                        if found_forecast:
                            selected_forecasts.append(found_forecast)

                    # If we don't have 5 forecasts, supplement with evenly distributed ones
                    if len(selected_forecasts) < 5 and len(day_forecasts) > 0:
                        all_hours_sorted = sorted(day_forecasts, key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
                        needed = 5 - len(selected_forecasts)
                        stride = max(1, len(all_hours_sorted) // needed)
                        for j in range(0, len(all_hours_sorted), stride):
                            if len(selected_forecasts) >= 5:
                                break
                            if all_hours_sorted[j] not in selected_forecasts:
                                selected_forecasts.append(all_hours_sorted[j])

                    temps = [f.get('temperature', 0) for f in day_forecasts if f.get('temperature') is not None]
                    if temps:
                        min_temp = min(temps)
                        max_temp = max(temps)

                        total_precip = sum(f.get('precipitation_mm', 0) for f in day_forecasts)

                        # Display day header with min/max
                        if total_precip > 0:
                            precip_icon = "🌧️" if total_precip >= 1.0 else "🌦️"
                            print(f"   {day_name} ({day_obj.strftime('%b %d')}): {min_temp:.0f}° → {max_temp:.0f}° {precip_icon}{total_precip:.1f}mm")
                        else:
                            print(f"   {day_name} ({day_obj.strftime('%b %d')}): {min_temp:.0f}° → {max_temp:.0f}°")

                        # Display hourly forecast in a single horizontal line
                        hourly_items = []
                        for forecast in selected_forecasts[:5]:  # Take max 5
                            hour_time = datetime.fromisoformat(forecast['timestamp'].replace('Z', '+00:00'))
                            temp = forecast.get('temperature', 'N/A')
                            # Use the translation function which returns emoji + description
                            full_translation = translate_code(forecast.get('symbol_code', 'unknown'), 'weather_symbol')
                            # Extract just the emoji (first part before space) if it contains a space
                            if ' ' in full_translation:
                                icon = full_translation.split(' ', 1)[0]  # Get part before first space
                            else:
                                icon = full_translation  # Use as-is if no space

                            temp_str = f"{temp:.0f}°" if isinstance(temp, (int, float)) else str(temp)
                            hourly_items.append(f"{hour_time.strftime('%H')}h {icon} {temp_str}")

                        # Print as a single line with pipe separators
                        if hourly_items:
                            print(f"      {' | '.join(hourly_items)}")
            else:
                # For other days, show min/max temperatures and condition in a single line
                temps = [f.get('temperature', 0) for f in day_forecasts if f.get('temperature') is not None]
                if temps:
                    min_temp = min(temps)
                    max_temp = max(temps)

                    # Calculate total precipitation for the day
                    total_precip = sum(f.get('precipitation_mm', 0) for f in day_forecasts)

                    # Find the most common weather condition for the day (excluding empty strings)
                    conditions = [f.get('symbol_code', 'unknown') for f in day_forecasts if f.get('symbol_code', '') != '']
                    if conditions:
                        # Find the most common condition
                        condition_counts = Counter(conditions)
                        main_translation = translate_code(condition_counts.most_common(1)[0][0], 'weather_symbol')
                        # Get the emoji by splitting on space (emoji part before space)
                        if ' ' in main_translation:
                            main_icon = main_translation.split(' ', 1)[0]
                        else:
                            main_icon = main_translation

                        # Show precipitation amount with the precipitation icon OR just the weather icon
                        if total_precip > 0:
                            precip_info = f" ({total_precip:.1f}mm)"
                            print(f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}° {main_icon}{precip_info}")
                        else:
                            print(f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}° {main_icon}")
                    else:
                        # No conditions available, just show temps and any precipitation
                        if total_precip > 0:
                            precip_icon = "🌧️" if total_precip >= 1.0 else "🌦️"
                            print(f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}° {precip_icon} ({total_precip:.1f}mm)")
                        else:
                            print(f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}°")
        else:
            print(f"   {date_key} (Day {i+1}): No forecast data available")


def get_forecast_for_time(forecast_data, target_time):
    """
    Helper function to get forecast closest to a specific time

    Args:
        forecast_data (list): List of forecast data points
        target_time (datetime): Target time to find forecast for

    Returns:
        dict: Forecast data point closest to the target time, or None
    """
    if not forecast_data:
        return None

    # Find forecast closest to target_time
    closest_forecast = forecast_data[0]
    closest_diff = abs((datetime.fromisoformat(closest_forecast['timestamp'].replace('Z', '+00:00')) - target_time).total_seconds())

    for forecast in forecast_data:
        try:
            forecast_time = datetime.fromisoformat(forecast['timestamp'].replace('Z', '+00:00'))
            diff = abs((forecast_time - target_time).total_seconds())
            if diff < closest_diff:
                closest_diff = diff
                closest_forecast = forecast
        except ValueError:
            continue

    return closest_forecast


if __name__ == "__main__":
    main()
