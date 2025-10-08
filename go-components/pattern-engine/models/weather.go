package models

import "time"

// WeatherPoint represents a single weather reading at a specific time
type WeatherPoint struct {
	Timestamp                time.Time `json:"timestamp"`
	Temperature              float64   `json:"temperature"`
	Pressure                 float64   `json:"pressure"`
	Humidity                 float64   `json:"humidity"`
	WindSpeed                float64   `json:"wind_speed"`
	WindDirection            float64   `json:"wind_direction"`
	CloudCover               float64   `json:"cloud_cover"`
	PrecipitationMm          float64   `json:"precipitation_mm"`
	PrecipitationProbability float64   `json:"precipitation_probability"`
	SymbolCode               string    `json:"symbol_code"`
}

// LocationData represents all weather data for a specific location
type LocationData struct {
	Name       string        `json:"location"`
	Coordinates Coordinates `json:"coordinates"`
	Readings   []WeatherPoint `json:"readings"`
}

// Coordinates represents geographic coordinates
type Coordinates struct {
	Latitude  float64 `json:"lat"`
	Longitude float64 `json:"lon"`
}

// Trend represents a weather trend with direction and confidence
type Trend struct {
	Variable   string  `json:"variable"`   // e.g., "temperature", "pressure"
	Trend      string  `json:"trend"`      // e.g., "rising", "falling", "stable"
	ChangeRate float64 `json:"rate_of_change"` // units per hour
	Confidence float64 `json:"confidence"` // 0.0-1.0
	Duration   string  `json:"duration"`   // e.g., "6h", "24h"
}

// Anomaly represents detected unusual weather patterns
type Anomaly struct {
	Variable  string    `json:"variable"`   // e.g., "pressure", "temperature"
	Type      string    `json:"type"`       // e.g., "sudden_drop", "spike", "unusual_pattern"
	Severity  string    `json:"severity"`   // e.g., "low", "moderate", "high"
	Value     float64   `json:"value"`      // the anomalous value
	Threshold float64   `json:"threshold"`  // baseline threshold
	Timestamp time.Time `json:"timestamp"`
}

// Pattern represents identified weather patterns
type Pattern struct {
	Name        string         `json:"name"`         // e.g., "cold_front", "warm_front", "pressure_system"
	Description string         `json:"description"`  // detailed description
	Confidence  float64        `json:"confidence"`   // 0.0-1.0
	Strength    float64        `json:"strength"`     // 0.0-1.0
	Variables   []string       `json:"variables"`    // weather variables involved
	Readings    []WeatherPoint `json:"readings"`     // data points supporting the pattern
}

// AnalysisResult represents the complete analysis output
type AnalysisResult struct {
	AnalysisType    string          `json:"analysis_type"`     // e.g., "trend_analysis", "anomaly_detection"
	Timeframe       string          `json:"timeframe"`         // e.g., "24_hours", "7_days"
	Location        string          `json:"location"`
	GeneratedAt     time.Time       `json:"generated_at"`
	Trends          []Trend         `json:"trends,omitempty"`
	Anomalies       []Anomaly       `json:"anomalies,omitempty"`
	Patterns        []Pattern       `json:"patterns,omitempty"`
	WeatherSummary  WeatherSummary  `json:"weather_summary,omitempty"`
	StatisticalData []StatisticalData `json:"statistical_data,omitempty"`
}

// WeatherSummary contains high-level weather information
type WeatherSummary struct {
	CurrentTemp     float64   `json:"current_temperature"`
	MinTemperature  float64   `json:"min_temperature"`
	MaxTemperature  float64   `json:"max_temperature"`
	CurrentPressure float64   `json:"current_pressure"`
	MinPressure     float64   `json:"min_pressure"`
	MaxPressure     float64   `json:"max_pressure"`
	TrendNextHours  string    `json:"trend_next_hours"`  // e.g., "warming", "cooling"
	ForecastSummary string    `json:"forecast_summary"`  // e.g., "storm_approaching", "clearing", "stable"
	Confidence      float64   `json:"confidence"`        // Overall confidence score
	Alerts          []string  `json:"alerts,omitempty"`  // e.g., "frost_warning", "high_wind", "precipitation_expected"
}

// StatisticalData contains statistical analysis results
type StatisticalData struct {
	Variable        string  `json:"variable"`        // e.g., "temperature", "pressure"
	Mean            float64 `json:"mean"`            // average value
	Median          float64 `json:"median"`          // median value
	Min             float64 `json:"min"`             // minimum value
	Max             float64 `json:"max"`             // maximum value
	StdDev          float64 `json:"std_dev"`         // standard deviation
	SampleSize      int     `json:"sample_size"`     // number of samples used
	ConfidenceLevel float64 `json:"confidence_level"` // confidence interval (0.0-1.0)
	TrendStrength   float64 `json:"trend_strength"`  // strength of trend (0.0-1.0)
}