package config

import (
	"fmt"
	"time"
)

// Config represents the complete configuration for the data collector service
type Config struct {
	API         APIConfig         `json:"api"`
	Integration IntegrationConfig `json:"integration"`
	Performance PerformanceConfig `json:"performance"`
	Logging     LoggingConfig     `json:"logging"`
}

// APIConfig contains all settings for external API calls (met.no, etc.)
type APIConfig struct {
	BaseURL    string        `json:"base_url"`    // API endpoint URL
	UserAgent  string        `json:"user_agent"`  // HTTP User-Agent header
	Timeout    time.Duration `json:"timeout"`     // Request timeout
	MaxRetries int           `json:"max_retries"` // Number of retry attempts
	RateLimit  int           `json:"rate_limit"`  // Max requests per second
	RetryDelay time.Duration `json:"retry_delay"` // Delay between retries
}

// IntegrationConfig contains settings for Python ↔ Go communication
type IntegrationConfig struct {
	InputFile     string `json:"input_file"`     // Where Python writes location requests
	OutputFile    string `json:"output_file"`    // Where Go writes weather results
	DataDirectory string `json:"data_directory"` // Base directory for integration files
	CreateDirs    bool   `json:"create_dirs"`    // Auto-create directories if missing
}

// PerformanceConfig contains settings for concurrent operations and optimization
type PerformanceConfig struct {
	MaxWorkers      int           `json:"max_workers"`      // Number of concurrent API workers
	WorkerTimeout   time.Duration `json:"worker_timeout"`   // Timeout per worker operation
	CollectionDelay time.Duration `json:"collection_delay"` // Delay between API calls (rate limiting)
	BufferSize      int           `json:"buffer_size"`      // Channel buffer size for worker communication
}

// LoggingConfig contains logging and debugging preferences
type LoggingConfig struct {
	EnableDebug   bool `json:"enable_debug"`   // Show detailed debug logs
	EnableMetrics bool `json:"enable_metrics"` // Show performance metrics
	LogToFile     bool `json:"log_to_file"`    // Write logs to file (vs stdout only)
	LogLevel      int  `json:"log_level"`      // Log level (0=Error, 1=Warn, 2=Info, 3=Debug)
}

// ValidationError represents configuration validation errors
type ValidationError struct {
	Field   string // The configuration field that failed validation
	Value   any    // The invalid value
	Message string // Human-readable error message
}

// Error implements the error interface for ValidationError
func (e ValidationError) Error() string {
	return fmt.Sprintf("config validation failed for '%s': %s (value: %v)",
		e.Field, e.Message, e.Value)
}

// LoadSource represents where configuration was loaded from
type LoadSource int

const (
	LoadSourceDefault LoadSource = iota // Loaded from default values
	LoadSourceFile                      // Loaded from JSON file
	LoadSourceEnv                       // Loaded from environment variables
	LoadSourceMixed                     // Mixed sources (some file, some defaults)
)

// ConfigMetadata contains information about how the config was loaded
type ConfigMetadata struct {
	Source   LoadSource `json:"source"`    // Where the config came from
	LoadedAt time.Time  `json:"loaded_at"` // When the config was loaded
	FilePath string     `json:"file_path"` // Path to config file (if used)
	Errors   []string   `json:"errors"`    // Any non-fatal loading errors
	Warnings []string   `json:"warnings"`  // Configuration warnings
}
