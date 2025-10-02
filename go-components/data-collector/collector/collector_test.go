package collector

import (
	"testing"
)

// TestLocationCreation tests basic Location struct creation
func TestLocationCreation(t *testing.T) {
	loc := Location{
		Name: "Test Location",
		Lat:  51.5074,
		Lon:  -0.1278,
	}

	if loc.Name != "Test Location" {
		t.Errorf("Expected name 'Test Location', got '%s'", loc.Name)
	}

	if loc.Lat != 51.5074 {
		t.Errorf("Expected latitude 51.5074, got %f", loc.Lat)
	}

	if loc.Lon != -0.1278 {
		t.Errorf("Expected longitude -0.1278, got %f", loc.Lon)
	}
}

// TestWeatherResultCreation tests WeatherResult struct
func TestWeatherResultCreation(t *testing.T) {
	loc := Location{Name: "London", Lat: 51.5, Lon: -0.1}

	result := WeatherResult{
		Location:    loc,
		Temperature: 20.5,
		Success:     true,
		Timestamp:   "2025-10-03T01:00:00Z",
	}

	if result.Temperature != 20.5 {
		t.Errorf("Expected temperature 20.5, got %f", result.Temperature)
	}

	if !result.Success {
		t.Errorf("Expected success to be true")
	}

	if result.Location.Name != "London" {
		t.Errorf("Expected location name 'London', got '%s'", result.Location.Name)
	}
}

// TestFetchWeatherForLocation tests the actual API call (integration test)
// This will make a real HTTP request to met.no
func TestFetchWeatherForLocation(t *testing.T) {
	// Use London coordinates for testing
	london := Location{
		Name: "London, UK",
		Lat:  51.5074,
		Lon:  -0.1278,
	}

	result := FetchWeatherForLocation(london)

	// Test that we got a result
	if result.Location.Name != london.Name {
		t.Errorf("Expected location name '%s', got '%s'", london.Name, result.Location.Name)
	}

	// If the API call succeeded, check the data makes sense
	if result.Success {
		t.Logf("✅ API call successful: %.1f°C, %.1fhPa", result.Temperature, result.Pressure)

		// Basic sanity checks for weather data
		if result.Temperature < -50 || result.Temperature > 60 {
			t.Errorf("Temperature seems unrealistic: %.1f°C", result.Temperature)
		}

		if result.Pressure < 800 || result.Pressure > 1200 {
			t.Errorf("Pressure seems unrealistic: %.1f hPa", result.Pressure)
		}

		if result.Timestamp == "" {
			t.Error("Timestamp should not be empty")
		}
	} else {
		t.Logf("⚠️  API call failed (this might be OK): %s", result.Error)
		// Don't fail the test if API is down - just log it
	}
}

// TestCollectWeatherData tests the collection orchestration
func TestCollectWeatherData(t *testing.T) {
	locations := []Location{
		{Name: "London, UK", Lat: 51.5074, Lon: -0.1278},
		{Name: "Invalid Location", Lat: 999, Lon: 999}, // This should fail
	}

	results := CollectWeatherData(locations)

	// Should get results for all locations (even failed ones)
	if len(results) != len(locations) {
		t.Errorf("Expected %d results, got %d", len(locations), len(results))
	}

	// Check that we got results for each location
	for i, result := range results {
		expectedName := locations[i].Name
		if result.Location.Name != expectedName {
			t.Errorf("Result %d: expected location '%s', got '%s'",
				i, expectedName, result.Location.Name)
		}

		t.Logf("Location %d (%s): Success=%v", i+1, result.Location.Name, result.Success)
		if !result.Success {
			t.Logf("  Error: %s", result.Error)
		}
	}
}

// TestInvalidCoordinates tests handling of invalid coordinates
func TestInvalidCoordinates(t *testing.T) {
	invalidLocation := Location{
		Name: "Invalid Location",
		Lat:  999, // Invalid latitude
		Lon:  999, // Invalid longitude
	}

	result := FetchWeatherForLocation(invalidLocation)

	// Should fail gracefully
	if result.Success {
		t.Error("Expected API call to fail for invalid coordinates")
	}

	if result.Error == "" {
		t.Error("Expected error message for failed API call")
	}

	t.Logf("Invalid coordinates handled correctly: %s", result.Error)
}
