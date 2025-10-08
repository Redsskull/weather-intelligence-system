package analysis

import (
	"math"
	"sort"
	"time"

	"pattern-engine/models"
	"pattern-engine/utils"
)

// AnomalyDetector detects unusual weather patterns and anomalies

// NewAnomalyDetector creates a new anomaly detector with default settings
func NewAnomalyDetector() *AnomalyDetector {
	return &AnomalyDetector{
		AnomalyThresholdFactor: 2.0, // 2 standard deviations from mean
		MinReadingsForBaseline: 5,   // minimum readings for baseline calculation
	}
}

// DetectAnomalies identifies anomalous weather readings by comparing to statistical baselines
func (ad *AnomalyDetector) DetectAnomalies(locationData *models.LocationData) []models.Anomaly {
	if len(locationData.Readings) < ad.MinReadingsForBaseline {
		return []models.Anomaly{} // Not enough data for anomaly detection
	}

	// Sort readings by timestamp
	sort.Slice(locationData.Readings, func(i, j int) bool {
		return locationData.Readings[i].Timestamp.Before(locationData.Readings[j].Timestamp)
	})

	var anomalies []models.Anomaly

	// Calculate statistical baselines for different variables
	temperatureStats := ad.calculateVariableStats(utils.GetTemperatureValues(locationData.Readings))
	pressureStats := ad.calculateVariableStats(utils.GetPressureValues(locationData.Readings))
	humidityStats := ad.calculateVariableStats(utils.GetHumidityValues(locationData.Readings))
	windSpeedStats := ad.calculateVariableStats(utils.GetWindSpeedValues(locationData.Readings))

	// Check each reading for anomalies
	for _, reading := range locationData.Readings {
		// Check for temperature anomalies
		if tempAnomaly := ad.checkVariableAnomaly("temperature", reading.Temperature, temperatureStats, reading.Timestamp); tempAnomaly != nil {
			anomalies = append(anomalies, *tempAnomaly)
		}

		// Check for pressure anomalies
		if pressureAnomaly := ad.checkVariableAnomaly("pressure", reading.Pressure, pressureStats, reading.Timestamp); pressureAnomaly != nil {
			anomalies = append(anomalies, *pressureAnomaly)
		}

		// Check for humidity anomalies
		if humidityAnomaly := ad.checkVariableAnomaly("humidity", reading.Humidity, humidityStats, reading.Timestamp); humidityAnomaly != nil {
			anomalies = append(anomalies, *humidityAnomaly)
		}

		// Check for wind speed anomalies
		if windAnomaly := ad.checkVariableAnomaly("wind_speed", reading.WindSpeed, windSpeedStats, reading.Timestamp); windAnomaly != nil {
			anomalies = append(anomalies, *windAnomaly)
		}

		// Check for rapid pressure changes (pressure trend anomalies)
		if pressureTrendAnomaly := ad.detectRapidPressureChange(reading, locationData.Readings); pressureTrendAnomaly != nil {
			anomalies = append(anomalies, *pressureTrendAnomaly)
		}
	}

	return anomalies
}

// calculateVariableStats calculates statistical measures for a variable
func (ad *AnomalyDetector) calculateVariableStats(values []float64) VariableStats {
	if len(values) == 0 {
		return VariableStats{}
	}

	// Calculate mean
	var sum float64
	for _, v := range values {
		sum += v
	}
	mean := sum / float64(len(values))

	// Calculate standard deviation
	var sumSquares float64
	for _, v := range values {
		diff := v - mean
		sumSquares += diff * diff
	}
	stdDev := math.Sqrt(sumSquares / float64(len(values)))

	// Calculate min and max
	min := values[0]
	max := values[0]
	for _, v := range values {
		if v < min {
			min = v
		}
		if v > max {
			max = v
		}
	}

	return VariableStats{
		Mean:       mean,
		StdDev:     stdDev,
		Min:        min,
		Max:        max,
		SampleSize: len(values),
	}
}

// checkVariableAnomaly checks if a single reading value is anomalous
func (ad *AnomalyDetector) checkVariableAnomaly(variableName string, value float64, stats VariableStats, timestamp time.Time) *models.Anomaly {
	if stats.SampleSize < ad.MinReadingsForBaseline {
		return nil
	}

	// Calculate how many standard deviations away from the mean the value is
	deviation := math.Abs(value - stats.Mean)
	if deviation <= ad.AnomalyThresholdFactor*stats.StdDev {
		return nil // Not an anomaly
	}

	severity := "low"
	if deviation > (3.0 * stats.StdDev) {
		severity = "high"
	} else if deviation > (2.0 * stats.StdDev) {
		severity = "moderate"
	}

	// Determine anomaly type based on value relative to mean
	anomalyType := "unusual_high"
	if value < stats.Mean {
		anomalyType = "unusual_low"
	}

	return &models.Anomaly{
		Variable:  variableName,
		Type:      anomalyType,
		Severity:  severity,
		Value:     value,
		Threshold: stats.Mean + (ad.AnomalyThresholdFactor * stats.StdDev),
		Timestamp: timestamp,
	}
}

// detectRapidPressureChange detects sudden pressure changes which might indicate weather fronts
func (ad *AnomalyDetector) detectRapidPressureChange(currentReading models.WeatherPoint, allReadings []models.WeatherPoint) *models.Anomaly {
	if len(allReadings) < 3 {
		return nil
	}

	// Find recent readings within a few hours for pressure change detection
	recentReadings := []models.WeatherPoint{}
	timeWindow := 4 * time.Hour // Look for changes within 4 hours

	for _, reading := range allReadings {
		timeDiff := currentReading.Timestamp.Sub(reading.Timestamp)
		if timeDiff > 0 && timeDiff <= timeWindow {
			recentReadings = append(recentReadings, reading)
		}
	}

	if len(recentReadings) == 0 {
		return nil
	}

	// Calculate the pressure change from the most recent reading
	mostRecent := recentReadings[len(recentReadings)-1]
	pressureChange := currentReading.Pressure - mostRecent.Pressure
	absChange := math.Abs(pressureChange)

	// A rapid pressure change can indicate weather systems
	if absChange > 3.0 { // 3 hPa change within 4 hours
		severity := "moderate"
		anomalyType := "pressure_rise"
		if pressureChange < 0 {
			anomalyType = "pressure_drop"
		}
		if absChange > 5.0 {
			severity = "high"
		}

		return &models.Anomaly{
			Variable:  "pressure",
			Type:      anomalyType,
			Severity:  severity,
			Value:     pressureChange,
			Threshold: 3.0,
			Timestamp: currentReading.Timestamp,
		}
	}

	return nil
}
