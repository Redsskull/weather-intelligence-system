package analysis

// VariableStats holds statistical information about a variable
type VariableStats struct {
	Mean     float64
	StdDev   float64
	Min      float64
	Max      float64
	SampleSize int
}

// TrendAnalyzer performs trend analysis on weather data
type TrendAnalyzer struct {
	MinReadingsForAnalysis int
	MinTrendSignificance float64
}

// AnomalyDetector detects unusual weather patterns and anomalies
type AnomalyDetector struct {
	AnomalyThresholdFactor float64 // multiplier for standard deviation to detect anomalies
	MinReadingsForBaseline int     // minimum readings to establish baseline
}

// PatternRecognizer identifies common weather patterns in data
type PatternRecognizer struct {
	MinPatternConfidence float64 // minimum confidence to report a pattern
}

// StatisticalAnalyzer performs statistical analysis on weather data
type StatisticalAnalyzer struct {
	ConfidenceLevel float64 // Confidence level for confidence intervals (e.g., 0.95 for 95%)
}