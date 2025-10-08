package analysis

import (
	"testing"
	"time"
	"pattern-engine/models"
)

// TestNewTrendAnalyzer tests creation of trend analyzer
func TestNewTrendAnalyzer(t *testing.T) {
	analyzer := NewTrendAnalyzer()
	if analyzer == nil {
		t.Error("NewTrendAnalyzer should not return nil")
	}
	if analyzer.MinReadingsForAnalysis <= 0 {
		t.Error("MinReadingsForAnalysis should be positive")
	}
	if analyzer.MinTrendSignificance <= 0 {
		t.Error("MinTrendSignificance should be positive")
	}
}

// TestAnalyzeTrendsWithInsufficientData tests trend analysis with insufficient data
func TestAnalyzeTrendsWithInsufficientData(t *testing.T) {
	analyzer := NewTrendAnalyzer()
	
	// Create location data with insufficient readings
	locationData := &models.LocationData{
		Name: "Test Location",
		Readings: []models.WeatherPoint{
			{
				Timestamp: time.Now(),
				Temperature: 20.0,
				Pressure: 1013.25,
			},
		},
	}
	
	trends := analyzer.AnalyzeTrends(locationData)
	if len(trends) != 0 {
		t.Errorf("Expected no trends with insufficient data, got %d", len(trends))
	}
}

// TestAnalyzeTrendsWithValidData tests trend analysis with valid data
func TestAnalyzeTrendsWithValidData(t *testing.T) {
	analyzer := NewTrendAnalyzer()
	
	// Create location data with valid readings showing a warming trend
	baseTime := time.Now()
	locationData := &models.LocationData{
		Name: "Test Location",
		Readings: []models.WeatherPoint{
			{
				Timestamp: baseTime.Add(-2 * time.Hour),
				Temperature: 18.0,
				Pressure: 1013.0,
			},
			{
				Timestamp: baseTime.Add(-1 * time.Hour),
				Temperature: 20.0,
				Pressure: 1013.5,
			},
			{
				Timestamp: baseTime,
				Temperature: 22.0,
				Pressure: 1014.0,
			},
		},
	}
	
	trends := analyzer.AnalyzeTrends(locationData)
	// We expect at least temperature and pressure trends
	if len(trends) == 0 {
		t.Error("Expected trends with valid data")
	}
	
	// Find temperature trend
	tempTrendFound := false
	for _, trend := range trends {
		if trend.Variable == "temperature" {
			tempTrendFound = true
			if trend.Trend != "rising" && trend.Trend != "warming" {
				t.Errorf("Expected temperature trend to be 'rising' or 'warming', got '%s'", trend.Trend)
			}
			break
		}
	}
	
	if !tempTrendFound {
		t.Error("Expected temperature trend not found")
	}
}