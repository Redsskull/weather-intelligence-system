package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"pattern-engine/analysis"
	"pattern-engine/models"
)

func main() {
	fmt.Println("🧠 Weather Pattern Engine v2.0 starting...")
	fmt.Println("🔍 Analyzing historical weather patterns with intelligent forecasting")

	timeseriesDir := "../../data/intelligence/timeseries/"
	fmt.Printf("📂 Reading time-series data from: %s\n", timeseriesDir)

	files, err := os.ReadDir(timeseriesDir)
	if err != nil {
		log.Fatalf("❌ Failed to read directory: %v", err)
	}

	// Initialize analysis components
	trendAnalyzer := analysis.NewTrendAnalyzer()
	anomalyDetector := analysis.NewAnomalyDetector()
	patternRecognizer := analysis.NewPatternRecognizer()

	// Process each location's time-series data
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".json") {
			filePath := filepath.Join(timeseriesDir, file.Name())
			fmt.Printf("\n📖 Analyzing: %s\n", file.Name())

			// Read and parse JSON data into structured format
			locationData, err := parseLocationData(filePath)
			if err != nil {
				fmt.Printf("❌ Failed to parse location data: %v\n", err)
				continue
			}

			fmt.Printf("✅ Location: %s\n", locationData.Name)
			fmt.Printf("📊 Available readings: %d\n", len(locationData.Readings))

			// Perform comprehensive analysis
			performAnalysis(&locationData, trendAnalyzer, anomalyDetector, patternRecognizer)
		}
	}

	fmt.Println("\n🎉 Advanced weather intelligence analysis complete!")
}

// parseLocationData reads and parses location data from JSON file
func parseLocationData(filePath string) (models.LocationData, error) {
	var locationData models.LocationData

	// Read JSON data
	data, err := os.ReadFile(filePath)
	if err != nil {
		return locationData, err
	}

	// Parse into structured format
	var rawData map[string]interface{}
	if err := json.Unmarshal(data, &rawData); err != nil {
		return locationData, err
	}

	// Extract location name
	if name, ok := rawData["location"].(string); ok {
		locationData.Name = name
	}

	// Extract coordinates if available
	if coords, ok := rawData["coordinates"].(map[string]interface{}); ok {
		if lat, ok := coords["lat"].(float64); ok {
			if lon, ok := coords["lon"].(float64); ok {
				locationData.Coordinates = models.Coordinates{
					Latitude:  lat,
					Longitude: lon,
				}
			}
		}
	}

	// Extract readings
	if readings, ok := rawData["readings"].([]interface{}); ok {
		for _, readingData := range readings {
			if readingMap, ok := readingData.(map[string]interface{}); ok {
				reading := parseWeatherReading(readingMap)
				if !reading.Timestamp.IsZero() { // Only add if timestamp is valid
					locationData.Readings = append(locationData.Readings, reading)
				}
			}
		}
	}

	return locationData, nil
}

// parseWeatherReading converts raw reading data to WeatherPoint
func parseWeatherReading(readingMap map[string]interface{}) models.WeatherPoint {
	var wp models.WeatherPoint

	// Parse timestamp
	if timestampStr, ok := readingMap["timestamp"].(string); ok {
		if parsedTime, err := time.Parse(time.RFC3339, timestampStr); err == nil {
			wp.Timestamp = parsedTime
		}
	}

	// Parse other fields
	if temp, ok := readingMap["temperature"].(float64); ok {
		wp.Temperature = temp
	}
	if pressure, ok := readingMap["pressure"].(float64); ok {
		wp.Pressure = pressure
	}
	if humidity, ok := readingMap["humidity"].(float64); ok {
		wp.Humidity = humidity
	}
	if windSpeed, ok := readingMap["wind_speed"].(float64); ok {
		wp.WindSpeed = windSpeed
	}
	if windDir, ok := readingMap["wind_direction"].(float64); ok {
		wp.WindDirection = windDir
	}
	if cloudCover, ok := readingMap["cloud_cover"].(float64); ok {
		wp.CloudCover = cloudCover
	}
	if precipMm, ok := readingMap["precipitation_mm"].(float64); ok {
		wp.PrecipitationMm = precipMm
	}
	if precipProb, ok := readingMap["precipitation_probability"].(float64); ok {
		wp.PrecipitationProbability = precipProb
	}
	if symbolCode, ok := readingMap["symbol_code"].(string); ok {
		wp.SymbolCode = symbolCode
	}

	return wp
}

// performAnalysis performs comprehensive analysis on the location data
func performAnalysis(locationData *models.LocationData, ta *analysis.TrendAnalyzer, ad *analysis.AnomalyDetector, pr *analysis.PatternRecognizer) {
	if len(locationData.Readings) < 2 {
		fmt.Printf("⚠️  Insufficient data for analysis (need at least 2 readings, got %d)\n", len(locationData.Readings))
		return
	}

	// Initialize statistical analyzer
	statAnalyzer := analysis.NewStatisticalAnalyzer()

	// Perform trend analysis
	fmt.Printf("📈 Trend Analysis:\n")
	trends := ta.AnalyzeTrends(locationData)
	for _, trend := range trends {
		fmt.Printf("   📊 %s: %s (%.3f units/hour, confidence: %.2f)\n", 
			trend.Variable, trend.Trend, trend.ChangeRate, trend.Confidence)
	}

	// Perform anomaly detection
	fmt.Printf("🔍 Anomaly Detection:\n")
	anomalies := ad.DetectAnomalies(locationData)
	for _, anomaly := range anomalies {
		fmt.Printf("   ⚠️  %s: %s (%.2f, severity: %s)\n", 
			anomaly.Variable, anomaly.Type, anomaly.Value, anomaly.Severity)
	}

	// Perform pattern recognition
	fmt.Printf("🧩 Pattern Recognition:\n")
	patterns := pr.RecognizePatterns(locationData)
	for _, pattern := range patterns {
		fmt.Printf("   🌦️  %s: %s (confidence: %.2f, strength: %.2f)\n", 
			pattern.Name, pattern.Description, pattern.Confidence, pattern.Strength)
	}

	// Perform statistical analysis
	fmt.Printf("📈 Statistical Analysis:\n")
	statistics := statAnalyzer.AnalyzeStatistics(locationData)
	for _, stat := range statistics {
		fmt.Printf("   📊 %s: mean=%.2f, std=%.2f, range=[%.2f,%.2f] (n=%d)\n",
			stat.Variable, stat.Mean, stat.StdDev, stat.Min, stat.Max, stat.SampleSize)
	}

	// Generate summary statistics
	fmt.Printf("📊 Statistical Summary:\n")
	summary := generateWeatherSummary(locationData)
	fmt.Printf("   🌡️  Temp: %.1f°C → %.1f°C (Δ%.1f°C)\n", 
		summary.MinTemperature, summary.MaxTemperature, summary.MaxTemperature-summary.MinTemperature)
	fmt.Printf("   🌪️  Pressure: %.1f → %.1f hPa\n", 
		summary.MinPressure, summary.MaxPressure)
	fmt.Printf("   📅 Duration: %s\n", calculateDuration(locationData.Readings))

	// Create and save comprehensive analysis result
	saveAnalysisResult(locationData, trends, anomalies, patterns, statistics, summary)
}

// generateWeatherSummary creates a weather summary from the readings
func generateWeatherSummary(locationData *models.LocationData) models.WeatherSummary {
	if len(locationData.Readings) == 0 {
		return models.WeatherSummary{}
	}

	var summary models.WeatherSummary

	// Initialize with first reading values
	summary.CurrentTemp = locationData.Readings[len(locationData.Readings)-1].Temperature
	summary.MinTemperature = locationData.Readings[0].Temperature
	summary.MaxTemperature = locationData.Readings[0].Temperature
	summary.CurrentPressure = locationData.Readings[len(locationData.Readings)-1].Pressure
	summary.MinPressure = locationData.Readings[0].Pressure
	summary.MaxPressure = locationData.Readings[0].Pressure

	// Find min/max values across all readings
	for _, reading := range locationData.Readings {
		if reading.Temperature < summary.MinTemperature {
			summary.MinTemperature = reading.Temperature
		}
		if reading.Temperature > summary.MaxTemperature {
			summary.MaxTemperature = reading.Temperature
		}
		if reading.Pressure < summary.MinPressure {
			summary.MinPressure = reading.Pressure
		}
		if reading.Pressure > summary.MaxPressure {
			summary.MaxPressure = reading.Pressure
		}
	}

	// Calculate an overall confidence based on data availability
	if len(locationData.Readings) >= 10 {
		summary.Confidence = 0.9
	} else if len(locationData.Readings) >= 5 {
		summary.Confidence = 0.7
	} else {
		summary.Confidence = 0.5
	}

	return summary
}

// calculateDuration calculates the time span of the readings
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

// saveAnalysisResult saves the comprehensive analysis to a JSON file
func saveAnalysisResult(locationData *models.LocationData, trends []models.Trend, anomalies []models.Anomaly, 
	patterns []models.Pattern, statistics []models.StatisticalData, summary models.WeatherSummary) {
	
	// Create AnalysisResult structure
	analysisResult := models.AnalysisResult{
		AnalysisType:    "comprehensive_weather_analysis",
		Timeframe:       calculateDuration(locationData.Readings),
		Location:        locationData.Name,
		GeneratedAt:     time.Now(),
		Trends:          trends,
		Anomalies:       anomalies,
		Patterns:        patterns,
		StatisticalData: statistics,
		WeatherSummary:  summary,
	}

	// Create output directory if it doesn't exist
	outputDir := "../../data/intelligence/analysis"
	os.MkdirAll(outputDir, 0755)

	// Generate filename based on location and timestamp
	safeLocation := strings.ReplaceAll(locationData.Name, " ", "_")
	safeLocation = strings.ReplaceAll(safeLocation, ",", "")
	safeLocation = strings.ReplaceAll(safeLocation, "/", "_")
	
	filename := fmt.Sprintf("%s/%s_analysis_%s.json", outputDir, safeLocation, 
		time.Now().Format("20060102_150405"))
	
	// Convert to JSON with indentation
	jsonData, err := json.MarshalIndent(analysisResult, "", "  ")
	if err != nil {
		fmt.Printf("❌ Error marshaling analysis to JSON: %v\n", err)
		return
	}

	// Write to file
	err = os.WriteFile(filename, jsonData, 0644)
	if err != nil {
		fmt.Printf("❌ Error writing analysis to file: %v\n", err)
		return
	}

	fmt.Printf("💾 Analysis saved to: %s\n", filename)
}
