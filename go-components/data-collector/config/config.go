package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// Global configuration instance
var globalConfig *Config
var globalMetadata *ConfigMetadata

// Load loads configuration from file or returns defaults with metadata
func Load(configPath ...string) (*Config, *ConfigMetadata, error) {
	metadata := &ConfigMetadata{
		LoadedAt: time.Now(),
		Errors:   []string{},
		Warnings: []string{},
	}

	var config *Config
	var err error

	// Try to load from provided path first
	if len(configPath) > 0 && configPath[0] != "" {
		config, err = loadFromFile(configPath[0])
		if err != nil {
			// Log the error but don't fail - fall back to defaults
			metadata.Errors = append(metadata.Errors,
				fmt.Sprintf("Failed to load config from %s: %v", configPath[0], err))
			metadata.Warnings = append(metadata.Warnings, "Using default configuration")
			metadata.Source = LoadSourceDefault
		} else {
			metadata.FilePath = configPath[0]
			metadata.Source = LoadSourceFile
		}
	}

	// Fall back to default configuration if loading failed
	if config == nil {
		config = getDefaultConfig()
		if metadata.Source != LoadSourceFile {
			metadata.Source = LoadSourceDefault
		} else {
			metadata.Source = LoadSourceMixed
		}
	}

	// Validate the configuration
	if validationErr := validateConfig(config); validationErr != nil {
		return nil, metadata, fmt.Errorf("configuration validation failed: %w", validationErr)
	}

	// Store as global config
	globalConfig = config
	globalMetadata = metadata

	// Ensure necessary directories exist
	if err := config.EnsureDirectories(); err != nil {
		metadata.Warnings = append(metadata.Warnings,
			fmt.Sprintf("Could not create directories: %v", err))
	}

	return config, metadata, nil
}

// Get returns the global configuration instance (loads default if none exists)
func Get() *Config {
	if globalConfig == nil {
		// Auto-load default configuration
		config, _, err := Load()
		if err != nil {
			// This should never happen with default config, but be safe
			panic(fmt.Sprintf("Failed to load default configuration: %v", err))
		}
		return config
	}
	return globalConfig
}

// GetMetadata returns metadata about how the config was loaded
func GetMetadata() *ConfigMetadata {
	if globalMetadata == nil {
		// If no metadata exists, return default metadata
		return &ConfigMetadata{
			Source:   LoadSourceDefault,
			LoadedAt: time.Now(),
			Errors:   []string{},
			Warnings: []string{"Configuration metadata not available"},
		}
	}
	return globalMetadata
}

// loadFromFile loads configuration from a JSON file
func loadFromFile(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config JSON: %w", err)
	}

	return &config, nil
}

// getDefaultConfig returns sensible default configuration values
func getDefaultConfig() *Config {
	return &Config{
		API: APIConfig{
			BaseURL:    "https://api.met.no/weatherapi/locationforecast/2.0/compact",
			UserAgent:  "WeatherIntelligenceSystem/1.0 (CS50 Final Project)",
			Timeout:    30 * time.Second,
			MaxRetries: 3,
			RateLimit:  8, // Conservative rate limit (met.no allows ~20/sec)
			RetryDelay: 2 * time.Second,
		},
		Integration: IntegrationConfig{
			InputFile:     "data/integration/input_locations.json",
			OutputFile:    "data/integration/output_weather.json",
			DataDirectory: "data/integration",
			CreateDirs:    true,
		},
		Performance: PerformanceConfig{
			MaxWorkers:      5, // Conservative for API rate limits
			WorkerTimeout:   60 * time.Second,
			CollectionDelay: 125 * time.Millisecond, // ~8 requests/second
			BufferSize:      100,
		},
		Logging: LoggingConfig{
			EnableDebug:   false,
			EnableMetrics: true,
			LogToFile:     false,
			LogLevel:      2, // Info level
		},
	}
}

// validateConfig checks if configuration values are valid
func validateConfig(cfg *Config) error {
	// Validate API configuration
	if cfg.API.BaseURL == "" {
		return ValidationError{
			Field:   "api.base_url",
			Value:   cfg.API.BaseURL,
			Message: "API base URL cannot be empty",
		}
	}

	if cfg.API.Timeout <= 0 {
		return ValidationError{
			Field:   "api.timeout",
			Value:   cfg.API.Timeout,
			Message: "API timeout must be positive",
		}
	}

	if cfg.API.MaxRetries < 0 {
		return ValidationError{
			Field:   "api.max_retries",
			Value:   cfg.API.MaxRetries,
			Message: "API max retries cannot be negative",
		}
	}

	// Validate Performance configuration
	if cfg.Performance.MaxWorkers <= 0 {
		return ValidationError{
			Field:   "performance.max_workers",
			Value:   cfg.Performance.MaxWorkers,
			Message: "max workers must be positive",
		}
	}

	if cfg.Performance.MaxWorkers > 20 {
		return ValidationError{
			Field:   "performance.max_workers",
			Value:   cfg.Performance.MaxWorkers,
			Message: "max workers should not exceed 20 (API rate limits)",
		}
	}

	// Validate Integration configuration
	if cfg.Integration.InputFile == "" || cfg.Integration.OutputFile == "" {
		return ValidationError{
			Field:   "integration.files",
			Value:   fmt.Sprintf("input: %s, output: %s", cfg.Integration.InputFile, cfg.Integration.OutputFile),
			Message: "integration file paths cannot be empty",
		}
	}

	// Validate Logging configuration
	if cfg.Logging.LogLevel < 0 || cfg.Logging.LogLevel > 3 {
		return ValidationError{
			Field:   "logging.log_level",
			Value:   cfg.Logging.LogLevel,
			Message: "log level must be 0-3 (0=Error, 1=Warn, 2=Info, 3=Debug)",
		}
	}

	return nil
}

// EnsureDirectories creates necessary directories if they don't exist
func (c *Config) EnsureDirectories() error {
	if c.Integration.CreateDirs {
		if err := os.MkdirAll(c.Integration.DataDirectory, 0755); err != nil {
			return fmt.Errorf("failed to create directory %s: %w",
				c.Integration.DataDirectory, err)
		}
	}
	return nil
}

// GetInputFilePath returns the full path to the input file
func (c *Config) GetInputFilePath() string {
	if filepath.IsAbs(c.Integration.InputFile) {
		return c.Integration.InputFile
	}
	return c.Integration.InputFile
}

// GetOutputFilePath returns the full path to the output file
func (c *Config) GetOutputFilePath() string {
	if filepath.IsAbs(c.Integration.OutputFile) {
		return c.Integration.OutputFile
	}
	return c.Integration.OutputFile
}

// SaveToFile saves the current configuration to a JSON file
func (c *Config) SaveToFile(path string) error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// Reload reloads configuration from the same source it was originally loaded from
func Reload() (*Config, *ConfigMetadata, error) {
	if globalMetadata != nil && globalMetadata.FilePath != "" {
		return Load(globalMetadata.FilePath)
	}
	return Load() // Load defaults if no file path is known
}
