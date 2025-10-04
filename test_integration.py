"""
Integration test for Python ↔ Go communication
"""

from project import call_go_collector, load_go_collected_data

def test_integration():
    print("🧪 Testing Python ↔ Go Integration")
    print("=" * 40)

    # Test locations
    test_locations = [
        {'name': 'London, UK', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'Paris, France', 'lat': 48.8566, 'lon': 2.3522}
    ]

    # Step 1: Call Go collector
    print("\n📝 Step 1: Calling Go collector...")
    success = call_go_collector(test_locations)

    if not success:
        print("❌ Go collector failed!")
        return False

    # Step 2: Load results
    print("\n📊 Step 2: Loading results...")
    results = load_go_collected_data()

    if results is None:
        print("❌ Failed to load results!")
        return False

    # Step 3: Display results
    print(f"\n✅ Successfully got data for {len(results)} locations:")
    for result in results:
        location = result['location']
        temp = result['temperature']
        success = result['success']
        status = "✅" if success else "❌"
        print(f"  {status} {location['name']}: {temp}°C")

    return True

if __name__ == "__main__":
    test_integration()
