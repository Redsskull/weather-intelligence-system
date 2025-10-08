package analysis

import (
	"math"
	"sort"

	"pattern-engine/models"
	"pattern-engine/utils"
)

// NewPatternRecognizer creates a new pattern recognizer with default settings
func NewPatternRecognizer() *PatternRecognizer {
	return &PatternRecognizer{
		MinPatternConfidence: 0.6, // minimum 60% confidence
	}
}

// RecognizePatterns identifies weather patterns in the data
func (pr *PatternRecognizer) RecognizePatterns(locationData *models.LocationData) []models.Pattern {
	if len(locationData.Readings) < 3 {
		return []models.Pattern{} // Not enough data for pattern recognition
	}

	// Sort readings by timestamp
	sort.Slice(locationData.Readings, func(i, j int) bool {
		return locationData.Readings[i].Timestamp.Before(locationData.Readings[j].Timestamp)
	})

	var patterns []models.Pattern

	// Detect warming/cooling trends
	if warmingPattern := pr.detectWarmingPattern(locationData.Readings); warmingPattern != nil {
		patterns = append(patterns, *warmingPattern)
	}

	// Detect cooling trends
	if coolingPattern := pr.detectCoolingPattern(locationData.Readings); coolingPattern != nil {
		patterns = append(patterns, *coolingPattern)
	}

	// Detect high pressure systems
	if highPressurePattern := pr.detectHighPressurePattern(locationData.Readings); highPressurePattern != nil {
		patterns = append(patterns, *highPressurePattern)
	}

	// Detect low pressure systems
	if lowPressurePattern := pr.detectLowPressurePattern(locationData.Readings); lowPressurePattern != nil {
		patterns = append(patterns, *lowPressurePattern)
	}

	// Detect precipitation patterns
	if precipitationPattern := pr.detectPrecipitationPattern(locationData.Readings); precipitationPattern != nil {
		patterns = append(patterns, *precipitationPattern)
	}

	// Detect stable weather patterns
	if stablePattern := pr.detectStablePattern(locationData.Readings); stablePattern != nil {
		patterns = append(patterns, *stablePattern)
	}

	return patterns
}

// detectWarmingPattern detects warming temperature trends
func (pr *PatternRecognizer) detectWarmingPattern(readings []models.WeatherPoint) *models.Pattern {
	if len(readings) < 4 {
		return nil
	}

	// Calculate average temperature difference over time
	var tempChanges []float64
	for i := 1; i < len(readings); i++ {
		change := readings[i].Temperature - readings[i-1].Temperature
		tempChanges = append(tempChanges, change)
	}

	// Count positive temperature changes
	positiveChanges := 0
	for _, change := range tempChanges {
		if change > 0.5 { // threshold for significant warming
			positiveChanges++
		}
	}

	// Calculate confidence based on percentage of positive changes
	confidence := float64(positiveChanges) / float64(len(tempChanges))

	if confidence >= pr.MinPatternConfidence && positiveChanges > 1 {
		return &models.Pattern{
			Name:        "warming_trend",
			Description: "Temperature is increasing consistently over time",
			Confidence:  confidence,
			Strength:    calculateTrendStrength(tempChanges),
			Variables:   []string{"temperature"},
			Readings:    readings,
		}
	}

	return nil
}

// detectCoolingPattern detects cooling temperature trends
func (pr *PatternRecognizer) detectCoolingPattern(readings []models.WeatherPoint) *models.Pattern {
	if len(readings) < 4 {
		return nil
	}

	// Calculate average temperature difference over time
	var tempChanges []float64
	for i := 1; i < len(readings); i++ {
		change := readings[i].Temperature - readings[i-1].Temperature
		tempChanges = append(tempChanges, change)
	}

	// Count negative temperature changes
	negativeChanges := 0
	for _, change := range tempChanges {
		if change < -0.5 { // threshold for significant cooling
			negativeChanges++
		}
	}

	// Calculate confidence based on percentage of negative changes
	confidence := float64(negativeChanges) / float64(len(tempChanges))

	if confidence >= pr.MinPatternConfidence && negativeChanges > 1 {
		return &models.Pattern{
			Name:        "cooling_trend",
			Description: "Temperature is decreasing consistently over time",
			Confidence:  confidence,
			Strength:    calculateTrendStrength(tempChanges),
			Variables:   []string{"temperature"},
			Readings:    readings,
		}
	}

	return nil
}

// detectHighPressurePattern detects high-pressure system patterns
func (pr *PatternRecognizer) detectHighPressurePattern(readings []models.WeatherPoint) *models.Pattern {
	if len(readings) < 3 {
		return nil
	}

	// Check for consistently high pressure readings
	highPressureCount := 0
	totalPressure := 0.0
	for _, reading := range readings {
		totalPressure += reading.Pressure
		if reading.Pressure > 1020.0 { // typical high pressure threshold
			highPressureCount++
		}
	}

	avgPressure := totalPressure / float64(len(readings))
	confidence := float64(highPressureCount) / float64(len(readings))

	if confidence >= pr.MinPatternConfidence && avgPressure > 1015.0 {
		return &models.Pattern{
			Name:        "high_pressure_system",
			Description: "High pressure system with consistently elevated atmospheric pressure",
			Confidence:  confidence,
			Strength:    math.Min(1.0, avgPressure/1030.0), // normalize strength
			Variables:   []string{"pressure"},
			Readings:    readings,
		}
	}

	return nil
}

// detectLowPressurePattern detects low-pressure system patterns
func (pr *PatternRecognizer) detectLowPressurePattern(readings []models.WeatherPoint) *models.Pattern {
	if len(readings) < 3 {
		return nil
	}

	// Check for consistently low pressure readings
	lowPressureCount := 0
	totalPressure := 0.0
	for _, reading := range readings {
		totalPressure += reading.Pressure
		if reading.Pressure < 1000.0 { // typical low pressure threshold
			lowPressureCount++
		}
	}

	avgPressure := totalPressure / float64(len(readings))
	confidence := float64(lowPressureCount) / float64(len(readings))

	if confidence >= pr.MinPatternConfidence && avgPressure < 1010.0 {
		return &models.Pattern{
			Name:        "low_pressure_system",
			Description: "Low pressure system with consistently reduced atmospheric pressure",
			Confidence:  confidence,
			Strength:    math.Min(1.0, (1030.0-avgPressure)/20.0), // normalize strength
			Variables:   []string{"pressure", "symbol_code"},
			Readings:    readings,
		}
	}

	return nil
}

// detectPrecipitationPattern detects precipitation-related patterns
func (pr *PatternRecognizer) detectPrecipitationPattern(readings []models.WeatherPoint) *models.Pattern {
	if len(readings) < 2 {
		return nil
	}

	// Look for increasing precipitation patterns
	precipitationEvents := 0
	for _, reading := range readings {
		if reading.PrecipitationMm > 0.1 || reading.PrecipitationProbability > 50 {
			precipitationEvents++
		}
	}

	confidence := float64(precipitationEvents) / float64(len(readings))

	if precipitationEvents > 0 {
		description := "Precipitation expected or occurring"
		patternName := "precipitation_pattern"

		if confidence >= 0.7 {
			description = "Consistent precipitation pattern"
			patternName = "consistent_precipitation"
		} else if confidence >= 0.4 {
			description = "Intermittent precipitation pattern"
			patternName = "intermittent_precipitation"
		}

		return &models.Pattern{
			Name:        patternName,
			Description: description,
			Confidence:  confidence,
			Strength:    calculatePrecipitationStrength(readings),
			Variables:   []string{"precipitation_mm", "precipitation_probability", "symbol_code"},
			Readings:    readings,
		}
	}

	return nil
}

// detectStablePattern detects stable weather conditions
func (pr *PatternRecognizer) detectStablePattern(readings []models.WeatherPoint) *models.Pattern {
	if len(readings) < 4 {
		return nil
	}

	// Calculate variations in temperature, pressure, and humidity
	tempVariations := calculateVariations(utils.GetTemperatureValues(readings))
	pressureVariations := calculateVariations(utils.GetPressureValues(readings))
	humidityVariations := calculateVariations(utils.GetHumidityValues(readings))

	// Calculate overall stability based on low variations
	avgTempVariation := calculateAverage(tempVariations)
	avgPressureVariation := calculateAverage(pressureVariations)
	avgHumidityVariation := calculateAverage(humidityVariations)

	// If all variations are low, it's a stable pattern
	// High stability = low variation
	stabilityScore := (1.0 / (avgTempVariation + 1.0)) * (1.0 / (avgPressureVariation + 1.0)) * (1.0 / (avgHumidityVariation + 1.0))
	confidence := math.Min(1.0, stabilityScore)

	if confidence >= pr.MinPatternConfidence {
		return &models.Pattern{
			Name:        "stable_weather",
			Description: "Weather conditions are stable with minimal variation",
			Confidence:  confidence,
			Strength:    1.0 - math.Min(1.0, (avgTempVariation+avgPressureVariation+avgHumidityVariation)/3.0),
			Variables:   []string{"temperature", "pressure", "humidity"},
			Readings:    readings,
		}
	}

	return nil
}

// calculateTrendStrength calculates the strength of a temperature trend
func calculateTrendStrength(changes []float64) float64 {
	if len(changes) == 0 {
		return 0
	}

	var sum float64
	for _, change := range changes {
		sum += math.Abs(change)
	}
	avgChange := sum / float64(len(changes))

	// Normalize to 0-1 scale
	return math.Min(1.0, avgChange/2.0) // assuming 2°C average change is significant
}

// calculatePrecipitationStrength calculates the strength of precipitation patterns
func calculatePrecipitationStrength(readings []models.WeatherPoint) float64 {
	if len(readings) == 0 {
		return 0
	}

	var totalPrecip float64
	for _, reading := range readings {
		totalPrecip += reading.PrecipitationMm
	}

	avgPrecip := totalPrecip / float64(len(readings))
	return math.Min(1.0, avgPrecip/5.0) // normalize assuming 5mm average is significant
}

// calculateVariations calculates variations between consecutive readings
func calculateVariations(values []float64) []float64 {
	if len(values) < 2 {
		return []float64{}
	}

	variations := make([]float64, len(values)-1)
	for i := 1; i < len(values); i++ {
		variations[i-1] = math.Abs(values[i] - values[i-1])
	}

	return variations
}

// calculateAverage calculates the average of a slice of float64
func calculateAverage(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}

	var sum float64
	for _, v := range values {
		sum += v
	}
	return sum / float64(len(values))
}
