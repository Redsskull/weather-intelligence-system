package analysis

import (
	"fmt"
	"math"
	"sort"

	"pattern-engine/models"
)

// NewTrendAnalyzer creates a new trend analyzer with default settings
func NewTrendAnalyzer() *TrendAnalyzer {
	return &TrendAnalyzer{
		MinReadingsForAnalysis: 3,
		MinTrendSignificance:   0.1, // minimum change rate to consider a trend
	}
}

// AnalyzeTrends analyzes trends in weather data (both historical and forecast)
func (ta *TrendAnalyzer) AnalyzeTrends(locationData *models.LocationData) []models.Trend {
	if len(locationData.Readings) < ta.MinReadingsForAnalysis {
		return []models.Trend{} // Not enough readings for trend analysis
	}

	// Sort readings by timestamp to ensure chronological order
	sort.Slice(locationData.Readings, func(i, j int) bool {
		return locationData.Readings[i].Timestamp.Before(locationData.Readings[j].Timestamp)
	})

	var trends []models.Trend

	// Analyze temperature trend
	if tempTrend := ta.analyzeTemperatureTrend(locationData.Readings); tempTrend != nil {
		trends = append(trends, *tempTrend)
	}

	// Analyze pressure trend
	if pressureTrend := ta.analyzePressureTrend(locationData.Readings); pressureTrend != nil {
		trends = append(trends, *pressureTrend)
	}

	// Analyze humidity trend
	if humidityTrend := ta.analyzeHumidityTrend(locationData.Readings); humidityTrend != nil {
		trends = append(trends, *humidityTrend)
	}

	// Analyze wind speed trend
	if windSpeedTrend := ta.analyzeWindSpeedTrend(locationData.Readings); windSpeedTrend != nil {
		trends = append(trends, *windSpeedTrend)
	}

	return trends
}

// analyzeTemperatureTrend analyzes temperature trends
func (ta *TrendAnalyzer) analyzeTemperatureTrend(readings []models.WeatherPoint) *models.Trend {
	if len(readings) < 2 {
		return nil
	}

	// Calculate linear regression for temperature trend
	slope, confidence := calculateLinearTrend(readings, func(wp models.WeatherPoint) float64 {
		return wp.Temperature
	})

	if math.Abs(slope) < ta.MinTrendSignificance {
		return &models.Trend{
			Variable:   "temperature",
			Trend:      "stable",
			ChangeRate: slope,
			Confidence: confidence,
			Duration:   calculateDuration(readings),
		}
	}

	trendType := "stable"
	if slope > 0.1 {
		trendType = "rising"
	} else if slope < -0.1 {
		trendType = "falling"
	}

	return &models.Trend{
		Variable:   "temperature",
		Trend:      trendType,
		ChangeRate: slope,
		Confidence: confidence,
		Duration:   calculateDuration(readings),
	}
}

// analyzePressureTrend analyzes pressure trends
func (ta *TrendAnalyzer) analyzePressureTrend(readings []models.WeatherPoint) *models.Trend {
	if len(readings) < 2 {
		return nil
	}

	// Calculate linear regression for pressure trend
	slope, confidence := calculateLinearTrend(readings, func(wp models.WeatherPoint) float64 {
		return wp.Pressure
	})

	if math.Abs(slope) < ta.MinTrendSignificance {
		return &models.Trend{
			Variable:   "pressure",
			Trend:      "stable",
			ChangeRate: slope,
			Confidence: confidence,
			Duration:   calculateDuration(readings),
		}
	}

	trendType := "stable"
	if slope > 0.5 {
		trendType = "rising" // pressure rising
	} else if slope < -0.5 {
		trendType = "falling" // pressure dropping
	}

	return &models.Trend{
		Variable:   "pressure",
		Trend:      trendType,
		ChangeRate: slope,
		Confidence: confidence,
		Duration:   calculateDuration(readings),
	}
}

// analyzeHumidityTrend analyzes humidity trends
func (ta *TrendAnalyzer) analyzeHumidityTrend(readings []models.WeatherPoint) *models.Trend {
	if len(readings) < 2 {
		return nil
	}

	// Calculate linear regression for humidity trend
	slope, confidence := calculateLinearTrend(readings, func(wp models.WeatherPoint) float64 {
		return wp.Humidity
	})

	if math.Abs(slope) < ta.MinTrendSignificance {
		return &models.Trend{
			Variable:   "humidity",
			Trend:      "stable",
			ChangeRate: slope,
			Confidence: confidence,
			Duration:   calculateDuration(readings),
		}
	}

	trendType := "stable"
	if slope > 1.0 {
		trendType = "increasing"
	} else if slope < -1.0 {
		trendType = "decreasing"
	}

	return &models.Trend{
		Variable:   "humidity",
		Trend:      trendType,
		ChangeRate: slope,
		Confidence: confidence,
		Duration:   calculateDuration(readings),
	}
}

// analyzeWindSpeedTrend analyzes wind speed trends
func (ta *TrendAnalyzer) analyzeWindSpeedTrend(readings []models.WeatherPoint) *models.Trend {
	if len(readings) < 2 {
		return nil
	}

	// Calculate linear regression for wind speed trend
	slope, confidence := calculateLinearTrend(readings, func(wp models.WeatherPoint) float64 {
		return wp.WindSpeed
	})

	if math.Abs(slope) < ta.MinTrendSignificance {
		return &models.Trend{
			Variable:   "wind_speed",
			Trend:      "stable",
			ChangeRate: slope,
			Confidence: confidence,
			Duration:   calculateDuration(readings),
		}
	}

	trendType := "stable"
	if slope > 0.1 {
		trendType = "increasing"
	} else if slope < -0.1 {
		trendType = "decreasing"
	}

	return &models.Trend{
		Variable:   "wind_speed",
		Trend:      trendType,
		ChangeRate: slope,
		Confidence: confidence,
		Duration:   calculateDuration(readings),
	}
}

// calculateLinearTrend calculates the slope of a linear trend using least squares regression
func calculateLinearTrend(readings []models.WeatherPoint, valueExtractor func(models.WeatherPoint) float64) (float64, float64) {
	n := len(readings)
	if n < 2 {
		return 0, 0
	}

	// Convert timestamps to time since Unix epoch in hours for slope calculation
	var xValues []float64
	var yValues []float64

	baseTime := readings[0].Timestamp.Unix()
	for _, reading := range readings {
		x := float64(reading.Timestamp.Unix()-baseTime) / 3600.0 // Time in hours since first reading
		y := valueExtractor(reading)
		xValues = append(xValues, x)
		yValues = append(yValues, y)
	}

	// Calculate means
	var sumX, sumY float64
	for i := range xValues {
		sumX += xValues[i]
		sumY += yValues[i]
	}
	meanX := sumX / float64(n)
	meanY := sumY / float64(n)

	// Calculate slope using least squares regression
	var numerator, denominator float64
	for i := range xValues {
		numerator += (xValues[i] - meanX) * (yValues[i] - meanY)
		denominator += (xValues[i] - meanX) * (xValues[i] - meanX)
	}

	if denominator == 0 {
		return 0, 0
	}

	slope := numerator / denominator

	// Calculate correlation coefficient for confidence
	correlation := calculateCorrelation(xValues, yValues, meanX, meanY, slope)
	confidence := math.Abs(correlation)

	return slope, confidence
}

// calculateCorrelation calculates the Pearson correlation coefficient
func calculateCorrelation(xValues, yValues []float64, meanX, meanY, slope float64) float64 {
	n := len(xValues)
	if n < 2 {
		return 0
	}

	var sumXY, sumXX, sumYY float64
	for i := 0; i < n; i++ {
		xDiff := xValues[i] - meanX
		yDiff := yValues[i] - meanY
		sumXY += xDiff * yDiff
		sumXX += xDiff * xDiff
		sumYY += yDiff * yDiff
	}

	denominator := math.Sqrt(sumXX * sumYY)
	if denominator == 0 {
		return 0
	}

	return sumXY / denominator
}

// calculateDuration calculates the duration span of the readings
func calculateDuration(readings []models.WeatherPoint) string {
	if len(readings) < 2 {
		return "0h"
	}

	duration := readings[len(readings)-1].Timestamp.Sub(readings[0].Timestamp)
	hours := int(duration.Hours())

	if hours >= 24 {
		days := hours / 24
		return fmt.Sprintf("%dd", days)
	}

	return fmt.Sprintf("%dh", hours)
}
