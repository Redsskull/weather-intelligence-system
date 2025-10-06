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

    print("🌍 Detecting your location via IP address...")

    # Try multiple services for reliability
    services = [
        {
            'name': 'ipapi.co',
            'url': 'https://ipapi.co/json/',
            'parser': _parse_ipapi_response
        },
        {
            'name': 'ip-api.com',
            'url': 'http://ip-api.com/json/',
            'parser': _parse_ip_api_response
        }
    ]

    for service in services:
        try:
            print(f"📍 Trying {service['name']}...")

            response = requests.get(
                service['url'],
                headers={'User-Agent': 'WeatherIntelligenceSystem/1.0'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                location = service['parser'](data)

                if location:
                    print(f"✅ Location detected: {location['city']}, {location['country']}")
                    return location

        except Exception as e:
            print(f"⚠️  {service['name']} failed: {e}")
            continue

    print("❌ Could not detect location via IP")
    return None


def _parse_ipapi_response(data):
    """Parse response from ipapi.co service"""
    try:
        if not data.get('city') or not data.get('country_name'):
            return None

        return {
            'city': data.get('city'),
            'country': data.get('country_name'),
            'region': data.get('region'),
            'lat': float(data.get('latitude', 0)),
            'lon': float(data.get('longitude', 0)),
            'source': 'ipapi.co',
            'accuracy': 'city_level'
        }
    except (ValueError, TypeError):
        return None


def _parse_ip_api_response(data):
    """Parse response from ip-api.com service"""
    try:
        if data.get('status') != 'success' or not data.get('city'):
            return None

        return {
            'city': data.get('city'),
            'country': data.get('country'),
            'region': data.get('regionName'),
            'lat': float(data.get('lat', 0)),
            'lon': float(data.get('lon', 0)),
            'source': 'ip-api.com',
            'accuracy': 'city_level'
        }
    except (ValueError, TypeError):
        return None


def ask_location_permission():
    """
    Ask user for permission to detect their location via IP.

    Returns:
        bool: True if user gives permission, False otherwise
    """

    print("\n🎯 LOCATION DETECTION OPTION")
    print("=" * 40)
    print("📍 I can try to detect your current location using your IP address.")
    print("   This will show weather for your approximate area.")
    print("")
    print("🔒 Privacy Notes:")
    print("   • This uses your IP address only (not GPS)")
    print("   • Accurate to city level (not your exact address)")
    print("   • No personal data is stored")
    print("   • You can always enter a city name manually")
    print("")

    while True:
        choice = input("🤔 Would you like me to detect your location? (y/n): ").strip().lower()

        if choice in ['y', 'yes', '1', 'true']:
            return True
        elif choice in ['n', 'no', '0', 'false']:
            return False
        else:
            print("   Please enter 'y' for yes or 'n' for no")


def get_location_with_fallback():
    """
    Complete location detection flow with manual fallback.

    1. Ask user permission for IP detection
    2. If permitted, try to detect location via IP
    3. If detection fails or not permitted, ask for manual input

    Returns:
        dict: Location data with lat, lon, display_name or None for manual fallback
    """

    # First, ask if user wants automatic detection
    if ask_location_permission():
        detected_location = detect_location_via_ip()

        if detected_location:
            # Format for compatibility with existing geocoding system
            return {
                'lat': detected_location['lat'],
                'lon': detected_location['lon'],
                'display_name': f"{detected_location['city']}, {detected_location['country']}",
                'city': detected_location['city'],
                'country': detected_location['country'],
                'source': 'ip_detection'
            }

    # Fall back to manual entry
    print("\n🌍 MANUAL LOCATION ENTRY")
    print("=" * 40)
    return None  # Will trigger manual input in main()


def offer_current_location_option():
    """
    Enhanced input interface that offers current location as an option.

    Returns:
        dict: Location data if user requested current location and it worked
        str: City name if user entered one manually
        None: If user entered nothing
    """

    print("💡 Quick options:")
    print("   • Type any city name (e.g., 'Paris', 'Tokyo', 'New York')")
    print("   • Type 'current' or 'here' to use your current location")
    print("")

    user_input = input("🌍 Enter city name or 'current': ").strip()

    if user_input.lower() in ['current', 'here', 'my location', 'current location']:
        # User explicitly requested current location
        print("\n📍 You requested your current location...")

        detected_location = detect_location_via_ip()

        if detected_location:
            return {
                'lat': detected_location['lat'],
                'lon': detected_location['lon'],
                'display_name': f"{detected_location['city']}, {detected_location['country']}",
                'city': detected_location['city'],
                'country': detected_location['country'],
                'source': 'ip_detection'
            }
        else:
            print("❌ Could not detect your location. Please enter a city name manually.")
            return None

    # Return the user input for normal city name processing
    return user_input if user_input else None
