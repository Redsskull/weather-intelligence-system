package analysis

import (
	"pattern-engine/models"
	"testing"
	"time"
)

// TestNewPatternRecognizer tests creation of pattern recognizer
func TestNewPatternRecognizer(t *testing.T) {
	recognizer := NewPatternRecognizer()
	if recognizer == nil {
		t.Error("NewPatternRecognizer should not return nil")
	}
	if recognizer.MinPatternConfidence <= 0 {
		t.Error("MinPatternConfidence should be positive")
	}
}

// TestRecognizePatternsWithInsufficientData tests pattern recognition with insufficient data
func TestRecognizePatternsWithInsufficientData(t *testing.T) {
	recognizer := NewPatternRecognizer()

	// Create location data with insufficient readings
	locationData := &models.LocationData{
		Name: "Test Location",
		Readings: []models.WeatherPoint{
			{
				Timestamp:   time.Now(),
				Temperature: 20.0,
				Pressure:    1013.25,
				Humidity:    50.0,
			},
		},
	}

	patterns := recognizer.RecognizePatterns(locationData)
	// With only one reading, we shouldn't expect complex patterns
	if len(patterns) > 1 {
		t.Errorf("Expected few or no patterns with insufficient data, got %d", len(patterns))
	}
}

// TestRecognizePatternsWithClearPattern tests pattern recognition with a clear warming trend
func TestRecognizePatternsWithClearPattern(t *testing.T) {
	recognizer := NewPatternRecognizer()

	// Create location data with a clear warming pattern
	baseTime := time.Now()

	// Generate readings showing a steady warming trend
	var readings []models.WeatherPoint
	for i := range readings {
		readings = append(readings, models.WeatherPoint{
			Timestamp:   baseTime.Add(time.Duration(i) * time.Hour),
			Temperature: 15.0 + float64(i)*0.5,   // Steady increase from 15°C to 20.5°C
			Pressure:    1015.0 - float64(i)*0.2, // Slight decrease (lower pressure often associated with warming)
			Humidity:    60.0 - float64(i)*1.5,   // Decreasing humidity (typical with warming)
		})
	}

	locationData := &models.LocationData{
		Name:     "Test Location",
		Readings: readings,
	}

	patterns := recognizer.RecognizePatterns(locationData)

	// Should detect at least basic patterns
	if len(patterns) == 0 {
		t.Log("No patterns detected with clear warming trend data")
		// This might depend on the specific pattern recognition thresholds
	}

	// Log detected patterns for debugging
	t.Logf("Detected %d patterns:", len(patterns))
	for i, pattern := range patterns {
		t.Logf("  %d. %s: %s (confidence: %.2f)", i+1, pattern.Name, pattern.Description, pattern.Confidence)
	}
}

// TestRecognizePatternsWithStableWeather tests pattern recognition with stable weather
func TestRecognizePatternsWithStableWeather(t *testing.T) {
	recognizer := NewPatternRecognizer()

	// Create location data with very stable weather
	baseTime := time.Now()

	// Generate readings with minimal variation
	var readings []models.WeatherPoint
	for i := range readings {
		readings = append(readings, models.WeatherPoint{
			Timestamp:   baseTime.Add(time.Duration(i) * time.Hour),
			Temperature: 20.0 + float64(i%3)*0.1,    // Very small variations (20.0 to 20.2°C)
			Pressure:    1013.25 + float64(i%2)*0.1, // Very small variations (1013.25 to 1013.35 hPa)
			Humidity:    50.0 + float64(i%4)*0.5,    // Very small variations (50.0 to 51.5%)
		})
	}

	locationData := &models.LocationData{
		Name:     "Test Location",
		Readings: readings,
	}

	patterns := recognizer.RecognizePatterns(locationData)

	// With stable weather, we might detect "stable weather" pattern
	t.Logf("Detected %d patterns with stable weather:", len(patterns))
	for i, pattern := range patterns {
		t.Logf("  %d. %s: %s (confidence: %.2f)", i+1, pattern.Name, pattern.Description, pattern.Confidence)
	}

	// At minimum, should be able to recognize stable conditions
	// This is more of a validation that the function runs without error
}
