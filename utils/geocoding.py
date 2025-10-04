"""
Geocoding utilities using OpenStreetMap Nominatim API
Converts city names to coordinates and handles caching for performance.
"""

import requests
import json
import os
import time


class GeocodeCache:
    """Simple file-based cache for geocoding results"""

    def __init__(self, cache_file="data/cache/geocode_cache.json"):
        self.cache_file = cache_file
        self.cache_data = {}
        self._ensure_cache_dir()
        self._load_cache()

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

    def _load_cache(self):
        """Load existing cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                    print(f"📊 Loaded {len(self.cache_data)} cached locations")
        except Exception as e:
            print(f"⚠️  Could not load geocode cache: {e}")
            self.cache_data = {}

    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save geocode cache: {e}")

    def get(self, city_name):
        """Get cached result for city"""
        normalized_name = city_name.lower().strip()
        return self.cache_data.get(normalized_name)

    def set(self, city_name, result):
        """Cache result for city"""
        normalized_name = city_name.lower().strip()
        result['cached_at'] = time.time()
        self.cache_data[normalized_name] = result
        self._save_cache()


# Global cache instance
_cache = GeocodeCache()


def geocode_city(city_name):
    """
    Convert city name to coordinates using OpenStreetMap Nominatim

    Args:
        city_name: City name (e.g., "Paris", "London, UK", "New York, USA")

    Returns:
        dict with lat, lon, display_name, or None if not found

    Example:
        result = geocode_city("Paris")
        # Returns: {
        #     "lat": 48.8566,
        #     "lon": 2.3522,
        #     "display_name": "Paris, Île-de-France, France",
        #     "country": "France"
        # }
    """

    if not city_name or not city_name.strip():
        return None

    # Check cache first
    cached_result = _cache.get(city_name)
    if cached_result:
        print(f"📍 Using cached location for {city_name}")
        return cached_result

    # Query Nominatim API
    print(f"🌍 Looking up coordinates for {city_name}...")

    try:
        # Nominatim API endpoint (free, no API key required)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': city_name,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }

        # Required headers (per Nominatim usage policy)
        headers = {
            'User-Agent': 'WeatherIntelligenceSystem/1.0 (CS50 Educational Project)'
        }

        # Make API request with reasonable timeout
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            results = response.json()

            if results and len(results) > 0:
                location = results[0]

                # Extract and clean the data
                result = {
                    'lat': float(location['lat']),
                    'lon': float(location['lon']),
                    'display_name': location['display_name'],
                    'country': location.get('address', {}).get('country', ''),
                    'city': location.get('address', {}).get('city',
                           location.get('address', {}).get('town',
                           location.get('address', {}).get('village', city_name))),
                    'state': location.get('address', {}).get('state', ''),
                    'source': 'nominatim'
                }

                # Cache the successful result
                _cache.set(city_name, result)

                print(f"✅ Found {result['display_name']}")
                return result
            else:
                print(f"❌ No results found for '{city_name}'")
                return None

        else:
            print(f"❌ Geocoding API error: HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print(f"⏰ Geocoding timeout for '{city_name}'")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🌐 Network error during geocoding for '{city_name}'")
        return None
    except Exception as e:
        print(f"💥 Unexpected geocoding error for '{city_name}': {e}")
        return None


def geocode_multiple_cities(city_names):
    """
    Geocode multiple cities efficiently

    Args:
        city_names: List of city names to geocode

    Returns:
        dict mapping city_name -> location_data
    """
    results = {}

    for city_name in city_names:
        # Add small delay to respect API rate limits
        time.sleep(0.1)  # 10 requests/second max
        results[city_name] = geocode_city(city_name)

    return results


def suggest_similar_cities(city_name, limit=5):
    """
    Get multiple suggestions for ambiguous city names

    Args:
        city_name: Partial or ambiguous city name
        limit: Maximum number of suggestions

    Returns:
        list of possible locations
    """

    try:
        print(f"💡 Finding suggestions for '{city_name}'...")

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': city_name,
            'format': 'json',
            'limit': limit,
            'addressdetails': 1
        }

        headers = {
            'User-Agent': 'WeatherIntelligenceSystem/1.0 (CS50 Educational Project)'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            results = response.json()

            suggestions = []
            seen_locations = set()  # Track duplicates by display_name

            for location in results:
                display_name = location['display_name']

                # Skip duplicates
                if display_name in seen_locations:
                    continue

                seen_locations.add(display_name)

                suggestion = {
                    'display_name': display_name,
                    'lat': float(location['lat']),
                    'lon': float(location['lon']),
                    'country': location.get('address', {}).get('country', ''),
                    'city': location.get('address', {}).get('city', city_name)
                }
                suggestions.append(suggestion)

            return suggestions
        else:
            return []

    except Exception as e:
        print(f"💥 Error getting suggestions: {e}")
        return []
