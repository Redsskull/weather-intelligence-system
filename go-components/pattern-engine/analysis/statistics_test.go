package analysis

import (
	"pattern-engine/models"
	"testing"
	"time"
)

// TestNewStatisticalAnalyzer tests creation of statistical analyzer
func TestNewStatisticalAnalyzer(t *testing.T) {
	analyzer := NewStatisticalAnalyzer()
	if analyzer == nil {
		t.Error("NewStatisticalAnalyzer should not return nil")
	}
	if analyzer.ConfidenceLevel <= 0 || analyzer.ConfidenceLevel > 1 {
		t.Error("ConfidenceLevel should be between 0 and 1")
	}
}

// TestCalculateStatisticsWithEmptyData tests statistical calculation with empty data
func TestCalculateStatisticsWithEmptyData(t *testing.T) {
	analyzer := NewStatisticalAnalyzer()

	var readings []models.WeatherPoint
	locationData := &models.LocationData{
		Name:     "Test Location",
		Readings: readings,
	}
	stats := analyzer.AnalyzeStatistics(locationData)

	// With no data, we should get empty statistics
	if len(stats) != 0 {
		t.Errorf("Expected no statistics with empty data, got %d", len(stats))
	}
}

// TestCalculateStatisticsWithSingleReading tests statistical calculation with single reading
func TestCalculateStatisticsWithSingleReading(t *testing.T) {
	analyzer := NewStatisticalAnalyzer()

	reading := models.WeatherPoint{
		Timestamp:   time.Now(),
		Temperature: 20.0,
		Pressure:    1013.25,
		Humidity:    50.0,
		WindSpeed:   5.0,
	}

	readings := []models.WeatherPoint{reading}
	locationData := &models.LocationData{
		Name:     "Test Location",
		Readings: readings,
	}
	stats := analyzer.AnalyzeStatistics(locationData)

	// With one reading, we should get NO statistics (need at least 2 values)
	if len(stats) != 0 {
		t.Errorf("Expected no statistics with single reading, got %d", len(stats))
		for _, stat := range stats {
			t.Logf("Unexpected statistic: %s - Mean: %.2f, StdDev: %.2f", stat.Variable, stat.Mean, stat.StdDev)
		}
	}
}

// TestCalculateStatisticsWithMultipleReadings tests statistical calculation with multiple readings
func TestCalculateStatisticsWithMultipleReadings(t *testing.T) {
	analyzer := NewStatisticalAnalyzer()

	baseTime := time.Now()
	var readings []models.WeatherPoint

	// Create multiple readings with known values
	testTemperatures := []float64{18.0, 20.0, 22.0, 19.0, 21.0}        // Mean = 20.0, StdDev ≈ 1.58
	testPressures := []float64{1010.0, 1015.0, 1020.0, 1012.0, 1018.0} // Mean = 1015.0, StdDev ≈ 3.94

	for i := 0; i < 5; i++ {
		readings = append(readings, models.WeatherPoint{
			Timestamp:   baseTime.Add(time.Duration(i) * time.Hour),
			Temperature: testTemperatures[i],
			Pressure:    testPressures[i],
			Humidity:    50.0, // Constant for simplicity
		})
	}

	locationData := &models.LocationData{
		Name:     "Test Location",
		Readings: readings,
	}
	stats := analyzer.AnalyzeStatistics(locationData)

	if len(stats) == 0 {
		t.Error("Expected statistics with multiple readings")
	}

	// Check temperature statistics
	tempStat := findStatByVariable(stats, "temperature")
	if tempStat == nil {
		t.Error("Expected temperature statistics")
	} else {
		// Allow for small floating point differences
		if abs(tempStat.Mean-20.0) > 0.1 {
			t.Errorf("Expected temperature mean close to 20.0, got %.2f", tempStat.Mean)
		}
		if tempStat.StdDev < 1.0 || tempStat.StdDev > 2.5 {
			t.Errorf("Expected temperature std dev between 1.0 and 2.5, got %.2f", tempStat.StdDev)
		}
		if tempStat.SampleSize != 5 {
			t.Errorf("Expected sample size 5, got %d", tempStat.SampleSize)
		}
	}

	// Check pressure statistics
	pressureStat := findStatByVariable(stats, "pressure")
	if pressureStat == nil {
		t.Error("Expected pressure statistics")
	} else {
		if abs(pressureStat.Mean-1015.0) > 1.0 {
			t.Errorf("Expected pressure mean close to 1015.0, got %.2f", pressureStat.Mean)
		}
		if pressureStat.SampleSize != 5 {
			t.Errorf("Expected sample size 5, got %d", pressureStat.SampleSize)
		}
	}
}

// Helper function to find statistic by variable name
func findStatByVariable(stats []models.StatisticalData, variable string) *models.StatisticalData {
	for _, stat := range stats {
		if stat.Variable == variable {
			return &stat
		}
	}
	return nil
}

// Helper function for absolute value
func abs(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}
