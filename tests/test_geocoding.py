"""
Tests for geocoding module - focused on active functions only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.geocoding import suggest_similar_cities, GeocodeCache


def test_suggestions():
    """Test city suggestions functionality"""

    print("🧪 Testing city suggestions...")

    # Test with ambiguous city name
    suggestions = suggest_similar_cities("Springfield", limit=3)

    if suggestions:
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3  # Should respect limit

        for suggestion in suggestions:
            # Verify structure of each suggestion
            assert 'display_name' in suggestion
            assert 'lat' in suggestion
            assert 'lon' in suggestion
            assert 'country' in suggestion
            assert isinstance(suggestion['lat'], float)
            assert isinstance(suggestion['lon'], float)

            print(f"💡 Suggestion: {suggestion['display_name']}")
    else:
        print("⚠️  No suggestions found (network might be down)")


def test_suggestions_with_limit():
    """Test that suggestion limit is respected"""

    print("🧪 Testing suggestion limit...")

    # Test with limit of 1
    suggestions = suggest_similar_cities("Paris", limit=1)

    if suggestions:
        assert len(suggestions) <= 1
        print(f"✅ Limit respected: got {len(suggestions)} result(s)")


def test_cache_functionality():
    """Test the geocoding cache system"""

    print("🧪 Testing cache functionality...")

    # Create a test cache
    test_cache = GeocodeCache("data/cache/test_geocode_cache.json")

    # Test cache set and get
    test_location = {
        'display_name': 'Test City, Test Country',
        'lat': 12.345,
        'lon': 67.890,
        'country': 'Test Country'
    }

    test_cache.set("Test City", test_location)
    cached_result = test_cache.get("Test City")

    assert cached_result is not None
    assert cached_result['display_name'] == 'Test City, Test Country'
    assert cached_result['lat'] == 12.345
    assert cached_result['lon'] == 67.890
    assert 'cached_at' in cached_result  # Should have timestamp

    print("✅ Cache set and get working correctly")

    # Test case insensitive lookup
    cached_result_upper = test_cache.get("TEST CITY")
    assert cached_result_upper is not None
    assert cached_result_upper['lat'] == 12.345

    print("✅ Case insensitive cache lookup working")


def test_suggestions_empty_input():
    """Test suggestions with empty or invalid input"""

    print("🧪 Testing edge cases...")

    # Empty string
    suggestions = suggest_similar_cities("", limit=3)
    # Should handle gracefully (might return empty list or None)

    # Very short string
    suggestions = suggest_similar_cities("A", limit=2)
    # Should handle gracefully

    print("✅ Edge cases handled without crashing")


if __name__ == "__main__":
    print("🌍 Testing Geocoding Module")
    print("=" * 30)

    test_suggestions()
    test_suggestions_with_limit()
    test_cache_functionality()
    test_suggestions_empty_input()

    print("\n🎉 All geocoding tests completed!")
