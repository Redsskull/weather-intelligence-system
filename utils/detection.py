"""
IP-based location detection utilities for automatic location discovery.
Respects user privacy by asking permission before detecting location.
"""

import requests


def detect_location_via_ip():
    """
    Detect user's approximate location using their IP address.

    Uses free IP geolocation services to determine city/country.
    This is less accurate than GPS but works without device permissions.

    Returns:
        dict: Location data with city, country, lat, lon or None if failed

    Example return:
        {
            'city': 'San Francisco',
            'country': 'United States',
            'lat': 37.7749,
            'lon': -122.4194,
            'region': 'California',
            'source': 'ip_detection',
            'accuracy': 'city_level'
        }
    """

    # Try multiple services for reliability
    services = [
        {
            "name": "ipapi.co",
            "url": "https://ipapi.co/json/",
            "parser": _parse_ipapi_response,
        },
        {
            "name": "ip-api.com",
            "url": "http://ip-api.com/json/",
            "parser": _parse_ip_api_response,
        },
    ]

    for service in services:
        try:
            response = requests.get(
                service["url"],
                headers={"User-Agent": "WeatherIntelligenceSystem/1.0"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                location = service["parser"](data)

                if location:
                    return location

        except Exception:
            continue

    return None


def _parse_ipapi_response(data):
    """Parse response from ipapi.co service"""
    try:
        if not data.get("city") or not data.get("country_name"):
            return None

        return {
            "city": data.get("city"),
            "country": data.get("country_name"),
            "region": data.get("region"),
            "lat": float(data.get("latitude", 0)),
            "lon": float(data.get("longitude", 0)),
            "source": "ipapi.co",
            "accuracy": "city_level",
        }
    except (ValueError, TypeError):
        return None


def _parse_ip_api_response(data):
    """Parse response from ip-api.com service"""
    try:
        if data.get("status") != "success" or not data.get("city"):
            return None

        return {
            "city": data.get("city"),
            "country": data.get("country"),
            "region": data.get("regionName"),
            "lat": float(data.get("lat", 0)),
            "lon": float(data.get("lon", 0)),
            "source": "ip-api.com",
            "accuracy": "city_level",
        }
    except (ValueError, TypeError):
        return None


def ask_user_location_choice():
    """
    Ask user to choose between automatic location detection or manual entry.

    Returns:
        str: 'auto' for automatic detection, 'manual' for manual entry
    """

    print("\n🎯 HOW WOULD YOU LIKE TO SET YOUR LOCATION?")
    print("=" * 50)
    print("Choose one of the following options:")
    print("")
    print("🤖 1. AUTO-DETECT my location (using IP address)")
    print("   • Quick and convenient")
    print("   • Accurate to city level (not your exact address)")
    print("   • Uses IP address only (not GPS)")
    print("   • No personal data is stored")
    print("")
    print("✍️  2. MANUAL entry (I'll type a city name)")
    print("   • Full control over location")
    print("   • Works with any city worldwide")
    print("   • No automatic detection")
    print("")

    while True:
        choice = input("🤔 Choose option (1 for auto-detect, 2 for manual): ").strip()

        if choice in ["1", "auto", "automatic", "detect"]:
            return "auto"
        elif choice in ["2", "manual", "type", "enter"]:
            return "manual"
        else:
            print("   Please enter '1' for auto-detect or '2' for manual entry")


def get_user_location():
    """
    Complete location flow - ask user once for their preference.

    Returns:
        dict: Location data with lat, lon, display_name, source
        None: If user chose manual entry or auto-detection failed
    """

    choice = ask_user_location_choice()

    if choice == "auto":
        detected_location = detect_location_via_ip()

        if detected_location:
            # Format for compatibility with existing geocoding system
            return {
                "lat": detected_location["lat"],
                "lon": detected_location["lon"],
                "display_name": f"{detected_location['city']}, {detected_location['country']}",
                "city": detected_location["city"],
                "country": detected_location["country"],
                "source": "ip_detection",
            }
        else:
            # User will be prompted for manual entry
            pass

    # User chose manual OR auto-detection failed
    return None  # Will trigger manual input in main()


def get_manual_city_input():
    """
    Simple manual city input without location detection options.

    Returns:
        str: City name entered by user
        None: If user entered nothing
    """

    print("💡 Enter any city name worldwide:")
    print("   Examples: 'Paris', 'Tokyo', 'New York', 'London', 'Sydney'")
    print("")

    user_input = input("🌍 City name: ").strip()
    return user_input if user_input else None
