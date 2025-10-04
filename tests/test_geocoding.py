"""
Tests for geocoding module
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.geocoding import geocode_city, geocode_multiple_cities, suggest_similar_cities



def test_basic_geocoding():
    """Test basic city geocoding"""

    print("🧪 Testing basic geocoding...")

    # Test Paris
    result = geocode_city("Paris")
    assert result is not None
    assert 'lat' in result
    assert 'lon' in result
    assert 'display_name' in result
    assert 48.0 < result['lat'] < 49.0  # Paris latitude range
    assert 2.0 < result['lon'] < 3.0    # Paris longitude range
    print(f"✅ Paris: {result['display_name']}")


def test_multiple_cities():
    """Test batch geocoding"""

    print("🧪 Testing multiple cities...")

    cities = ["London", "Berlin", "Tokyo"]
    results = geocode_multiple_cities(cities)

    assert len(results) == 3
    for city in cities:
        assert city in results
        if results[city]:  # Some might fail due to network
            print(f"✅ {city}: {results[city]['display_name']}")


def test_suggestions():
    """Test city suggestions"""

    print("🧪 Testing suggestions...")

    suggestions = suggest_similar_cities("Springfield", limit=3)
    if suggestions:
        for suggestion in suggestions:
            print(f"💡 Suggestion: {suggestion['display_name']}")


if __name__ == "__main__":
    print("🌍 Testing Geocoding Module")
    print("=" * 30)

    test_basic_geocoding()
    test_multiple_cities()
    test_suggestions()

    print("\n🎉 Tests completed!")
