package analysis

import (
	"math"
	"sort"

	"pattern-engine/models"
)

// NewStatisticalAnalyzer creates a new statistical analyzer with default settings
func NewStatisticalAnalyzer() *StatisticalAnalyzer {
	return &StatisticalAnalyzer{
		ConfidenceLevel: 0.95, // 95% confidence interval
	}
}

// AnalyzeStatistics performs statistical analysis on weather data
func (sa *StatisticalAnalyzer) AnalyzeStatistics(locationData *models.LocationData) []models.StatisticalData {
	var stats []models.StatisticalData

	// Analyze temperature statistics
	if tempStats := sa.analyzeVariableStats("temperature", getTemperatureValues(locationData.Readings)); tempStats != nil {
		stats = append(stats, *tempStats)
	}

	// Analyze pressure statistics
	if pressureStats := sa.analyzeVariableStats("pressure", getPressureValues(locationData.Readings)); pressureStats != nil {
		stats = append(stats, *pressureStats)
	}

	// Analyze humidity statistics
	if humidityStats := sa.analyzeVariableStats("humidity", getHumidityValues(locationData.Readings)); humidityStats != nil {
		stats = append(stats, *humidityStats)
	}

	// Analyze wind speed statistics
	if windSpeedStats := sa.analyzeVariableStats("wind_speed", getWindSpeedValues(locationData.Readings)); windSpeedStats != nil {
		stats = append(stats, *windSpeedStats)
	}

	// Analyze precipitation statistics
	if precipStats := sa.analyzeVariableStats("precipitation_mm", getPrecipitationValues(locationData.Readings)); precipStats != nil {
		stats = append(stats, *precipStats)
	}

	return stats
}

// analyzeVariableStats calculates statistical measures for a specific variable
func (sa *StatisticalAnalyzer) analyzeVariableStats(variableName string, values []float64) *models.StatisticalData {
	if len(values) < 2 {
		return nil // Need at least 2 values for statistics
	}

	// Sort values for median calculation
	sortedValues := make([]float64, len(values))
	copy(sortedValues, values)
	sort.Float64s(sortedValues)

	// Calculate mean
	var sum float64
	for _, v := range values {
		sum += v
	}
	mean := sum / float64(len(values))

	// Calculate median
	var median float64
	n := len(sortedValues)
	if n%2 == 0 {
		median = (sortedValues[n/2-1] + sortedValues[n/2]) / 2
	} else {
		median = sortedValues[n/2]
	}

	// Calculate standard deviation
	var sumSquares float64
	for _, v := range values {
		diff := v - mean
		sumSquares += diff * diff
	}
	stdDev := math.Sqrt(sumSquares / float64(len(values)))

	// Calculate min and max
	min := sortedValues[0]
	max := sortedValues[n-1]

	// Calculate trend strength based on standard deviation and sample size
	trendStrength := calculateTrendStrengthFromStats(mean, stdDev, len(values))

	return &models.StatisticalData{
		Variable:        variableName,
		Mean:            mean,
		Median:          median,
		Min:             min,
		Max:             max,
		StdDev:          stdDev,
		SampleSize:      len(values),
		ConfidenceLevel: sa.ConfidenceLevel,
		TrendStrength:   trendStrength,
	}
}

// getTemperatureValues extracts temperature values from readings
func getTemperatureValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.Temperature)
	}
	return values
}

// getPressureValues extracts pressure values from readings
func getPressureValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.Pressure)
	}
	return values
}

// getHumidityValues extracts humidity values from readings
func getHumidityValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.Humidity)
	}
	return values
}

// getWindSpeedValues extracts wind speed values from readings
func getWindSpeedValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.WindSpeed)
	}
	return values
}

// getPrecipitationValues extracts precipitation values from readings
func getPrecipitationValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.PrecipitationMm)
	}
	return values
}

// calculateTrendStrengthFromStats calculates trend strength based on statistical measures
func calculateTrendStrengthFromStats(mean, stdDev float64, sampleSize int) float64 {
	// Higher trend strength if there's more variation relative to the mean
	// and if there are more samples
	variationRatio := stdDev / math.Abs(mean+0.001)                // Add small value to avoid division by zero
	sampleFactor := math.Log(float64(sampleSize)+1) / math.Log(10) // Log scale for sample effect

	strength := variationRatio * sampleFactor
	return math.Min(1.0, strength) // Cap at 1.0
}
