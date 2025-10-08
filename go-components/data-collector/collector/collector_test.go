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
		Location: loc,
		CurrentWeather: WeatherPoint{
			Temperature:              20.5,
			PrecipitationMm:          1.2,
			PrecipitationProbability: 75.0,
			SymbolCode:               "lightrain",
			Timestamp:                "2025-10-03T01:00:00Z",
		},
		Success: true,
	}

	if result.CurrentWeather.Temperature != 20.5 {
		t.Errorf("Expected temperature 20.5, got %f", result.CurrentWeather.Temperature)
	}

	if result.CurrentWeather.PrecipitationMm != 1.2 {
		t.Errorf("Expected precipitation 1.2mm, got %f", result.CurrentWeather.PrecipitationMm)
	}

	if result.CurrentWeather.PrecipitationProbability != 75.0 {
		t.Errorf("Expected precipitation probability 75%%, got %f", result.CurrentWeather.PrecipitationProbability)
	}

	if result.CurrentWeather.SymbolCode != "lightrain" {
		t.Errorf("Expected symbol code 'lightrain', got '%s'", result.CurrentWeather.SymbolCode)
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
		t.Logf("✅ API call successful: %.1f°C, %.1fhPa, %.1fmm rain (%.0f%% chance), %s",
			result.CurrentWeather.Temperature, result.CurrentWeather.Pressure, result.CurrentWeather.PrecipitationMm,
			result.CurrentWeather.PrecipitationProbability, result.CurrentWeather.SymbolCode)

		// Basic sanity checks for weather data
		if result.CurrentWeather.Temperature < -50 || result.CurrentWeather.Temperature > 60 {
			t.Errorf("Temperature seems unrealistic: %.1f°C", result.CurrentWeather.Temperature)
		}

		if result.CurrentWeather.Pressure < 800 || result.CurrentWeather.Pressure > 1200 {
			t.Errorf("Pressure seems unrealistic: %.1f hPa", result.CurrentWeather.Pressure)
		}

		if result.CurrentWeather.PrecipitationMm < 0 || result.CurrentWeather.PrecipitationMm > 100 {
			t.Errorf("Precipitation seems unrealistic: %.1f mm", result.CurrentWeather.PrecipitationMm)
		}

		if result.CurrentWeather.PrecipitationProbability < 0 || result.CurrentWeather.PrecipitationProbability > 100 {
			t.Errorf("Precipitation probability seems unrealistic: %.1f%%", result.CurrentWeather.PrecipitationProbability)
		}

		if result.CurrentWeather.Timestamp == "" {
			t.Error("Timestamp should not be empty")
		}

		// Symbol code should be present (even if empty string is valid)
		t.Logf("Weather symbol: '%s'", result.CurrentWeather.SymbolCode)
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
		if result.Success {
			t.Logf("  Weather: %.1f°C, %.1fmm rain, %s",
				result.CurrentWeather.Temperature, result.CurrentWeather.PrecipitationMm, result.CurrentWeather.SymbolCode)
		} else {
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
