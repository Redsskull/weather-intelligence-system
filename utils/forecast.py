"""
Refactored version of display_weekly_forecast with better structure
"""

from datetime import datetime, date, timedelta
from collections import Counter, defaultdict

from utils.translations import translate_code


def display_weekly_forecast(go_weather_result):
    """
    Display compact weekly forecast showing today's hourly forecast and next 6 days

    Args:
        go_weather_result (dict): Weather data from Go collector including forecast
    """
    if not go_weather_result.get("forecast"):
        print("   • No detailed forecast data available")
        return

    # Get forecast data
    forecast_data = go_weather_result["forecast"]
    forecast_by_date = group_forecasts_by_date(forecast_data)

    # Get today's date and next 6 days
    days_to_show = get_seven_day_range()

    # Display forecasts in a compact format
    for i, date_key in enumerate(days_to_show):
        if date_key in forecast_by_date:
            day_forecasts = forecast_by_date[date_key]
            day_obj = datetime.strptime(date_key, "%Y-%m-%d")

            # Format day name (Today, Tomorrow, or abbreviated day)
            day_name = get_day_name(i, day_obj)

            if i == 0:  # Today
                display_today_forecast(day_forecasts, day_name, day_obj)
            else:  # Future days
                display_future_day_forecast(day_forecasts, day_name, day_obj)
        else:
            print(f"   {date_key} (Day {i+1}): No forecast data available")


def group_forecasts_by_date(forecast_data):
    """
    Groups forecast data by date

    Args:
        forecast_data (list): List of forecast data points

    Returns:
        dict: Dictionary with dates as keys and forecast lists as values
    """
    forecast_by_date = {}
    for forecast_point in forecast_data:
        timestamp_str = forecast_point.get("timestamp", "")
        if timestamp_str:
            try:
                # Handle ISO format: "2025-10-10T07:00:00Z"
                forecast_time = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                )
                date_key = forecast_time.strftime("%Y-%m-%d")

                if date_key not in forecast_by_date:
                    forecast_by_date[date_key] = []
                forecast_by_date[date_key].append(forecast_point)
            except ValueError:
                continue  # Skip invalid timestamps

    return forecast_by_date


def get_seven_day_range():
    """
    Gets today and the next 6 days

    Returns:
        list: Date strings for 7 days starting from today
    """
    today = date.today()
    days_to_show = []

    # Add today
    days_to_show.append(today.strftime("%Y-%m-%d"))

    # Add next 6 days
    for i in range(1, 7):
        future_date = today + timedelta(days=i)
        days_to_show.append(future_date.strftime("%Y-%m-%d"))

    return days_to_show


def get_day_name(index, day_obj):
    """
    Formats day name based on index (Today, Tomorrow, or weekday)

    Args:
        index (int): Index of day in forecast (0 = today)
        day_obj (datetime): Datetime object for the day

    Returns:
        str: Formatted day name
    """
    if index == 0:
        return "Today"
    elif index == 1:
        return "Tomorrow"
    else:
        return day_obj.strftime("%a")  # Abbreviated day name


def display_today_forecast(day_forecasts, day_name, day_obj):
    """
    Displays forecast for today with hourly details

    Args:
        day_forecasts (list): List of forecast data for today
        day_name (str): Name of the day (e.g. "Today")
        day_obj (datetime): Datetime object of the day
    """
    temps = [
        f.get("temperature", 0)
        for f in day_forecasts
        if f.get("temperature") is not None
    ]
    if temps:
        min_temp = min(temps)
        max_temp = max(temps)

        total_precip = sum(f.get("precipitation_mm", 0) for f in day_forecasts)

        # Display day header with min/max and precipitation info
        if total_precip > 0:
            precip_icon = "🌧️" if total_precip >= 1.0 else "🌦️"
            print(
                f"   {day_name} ({day_obj.strftime('%b %d')}): {min_temp:.0f}° → {max_temp:.0f}° {precip_icon}{total_precip:.1f}mm"
            )
        else:
            print(
                f"   {day_name} ({day_obj.strftime('%b %d')}): {min_temp:.0f}° → {max_temp:.0f}°"
            )

        # Get hourly forecasts for today
        selected_forecasts = get_representative_hourly_forecasts(day_forecasts)

        # Display hourly forecast in a single horizontal line
        hourly_items = []
        for forecast in selected_forecasts[:5]:  # Take max 5
            hour_time = datetime.fromisoformat(
                forecast["timestamp"].replace("Z", "+00:00")
            )
            temp = forecast.get("temperature", "N/A")
            # Use the translation function which returns emoji + description
            full_translation = translate_code(
                forecast.get("symbol_code", "unknown"), "weather_symbol"
            )
            # Extract just the emoji (first part before space) if it contains a space
            if " " in full_translation:
                icon = full_translation.split(" ", 1)[0]  # Get part before first space
            else:
                icon = full_translation  # Use as-is if no space

            temp_str = f"{temp:.0f}°" if isinstance(temp, (int, float)) else str(temp)
            hourly_items.append(f"{hour_time.strftime('%H')}h {icon} {temp_str}")

        # Print as a single line with pipe separators
        if hourly_items:
            print(f"      {' | '.join(hourly_items)}")


def get_representative_hourly_forecasts(day_forecasts):
    """
    Gets representative forecasts for key times of the day

    Args:
        day_forecasts (list): List of forecast data for a day

    Returns:
        list: Selected forecasts for key times
    """
    # Group forecasts by hour to find the best representative for each time period
    hourly_forecasts = defaultdict(list)

    for forecast in day_forecasts:
        hour_time = datetime.fromisoformat(forecast["timestamp"].replace("Z", "+00:00"))
        hour = hour_time.hour
        hourly_forecasts[hour].append(forecast)

    # Select forecasts for key times of day: early morning (7-9), late morning (10-11),
    # noon (12), afternoon (15-16), evening (18-20)
    selected_forecasts = []

    # Define time periods and select first forecast from each period if available
    time_periods = [
        (range(6, 10), "early morning"),  # 6-9 AM
        (range(10, 13), "late morning"),  # 10-12 AM
        (range(13, 17), "afternoon"),  # 1-4 PM
        (range(17, 21), "evening"),  # 5-8 PM
        (range(21, 24), "night"),  # 9-11 PM
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
        all_hours_sorted = sorted(
            day_forecasts,
            key=lambda x: datetime.fromisoformat(x["timestamp"].replace("Z", "+00:00")),
        )
        needed = 5 - len(selected_forecasts)
        stride = max(1, len(all_hours_sorted) // needed)
        for j in range(0, len(all_hours_sorted), stride):
            if len(selected_forecasts) >= 5:
                break
            if all_hours_sorted[j] not in selected_forecasts:
                selected_forecasts.append(all_hours_sorted[j])

    return selected_forecasts


def display_future_day_forecast(day_forecasts, day_name, day_obj):
    """
    Displays forecast for future days

    Args:
        day_forecasts (list): List of forecast data for the day
        day_name (str): Name of the day (e.g. "Mon")
        day_obj (datetime): Datetime object of the day
    """
    temps = [
        f.get("temperature", 0)
        for f in day_forecasts
        if f.get("temperature") is not None
    ]
    if temps:
        min_temp = min(temps)
        max_temp = max(temps)

        # Calculate total precipitation for the day
        total_precip = sum(f.get("precipitation_mm", 0) for f in day_forecasts)

        # Find the most common weather condition for the day (excluding empty strings)
        conditions = [
            f.get("symbol_code", "unknown")
            for f in day_forecasts
            if f.get("symbol_code", "") != ""
        ]
        if conditions:
            # Find the most common condition
            condition_counts = Counter(conditions)
            main_translation = translate_code(
                condition_counts.most_common(1)[0][0], "weather_symbol"
            )
            # Get the emoji by splitting on space (emoji part before space)
            if " " in main_translation:
                main_icon = main_translation.split(" ", 1)[0]
            else:
                main_icon = main_translation

            # Show precipitation amount with the precipitation icon OR just the weather icon
            if total_precip > 0:
                precip_info = f" ({total_precip:.1f}mm)"
                print(
                    f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}° {main_icon}{precip_info}"
                )
            else:
                print(
                    f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}° {main_icon}"
                )
        else:
            # No conditions available, just show temps and any precipitation
            if total_precip > 0:
                precip_icon = "🌧️" if total_precip >= 1.0 else "🌦️"
                print(
                    f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}° {precip_icon} ({total_precip:.1f}mm)"
                )
            else:
                print(
                    f"   {day_name} {day_obj.strftime('%b %d')}: {max_temp:.0f}°/{min_temp:.0f}°"
                )
