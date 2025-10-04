package config

import (
	"path/filepath"
	"testing"
	"time"
)

// TestGetDefaultConfig tests that default configuration is valid
func TestGetDefaultConfig(t *testing.T) {
	cfg := getDefaultConfig()

	// Test API config defaults
	if cfg.API.BaseURL == "" {
		t.Error("Default API base URL should not be empty")
	}

	if cfg.API.Timeout <= 0 {
		t.Error("Default API timeout should be positive")
	}

	if cfg.API.MaxRetries < 0 {
		t.Error("Default max retries should not be negative")
	}

	// Test Performance config defaults
	if cfg.Performance.MaxWorkers <= 0 {
		t.Error("Default max workers should be positive")
	}

	t.Logf("✅ Default config loaded: API timeout=%v, workers=%d",
		cfg.API.Timeout, cfg.Performance.MaxWorkers)
}

// TestValidateConfig tests configuration validation
func TestValidateConfig(t *testing.T) {
	// Test valid configuration
	validConfig := getDefaultConfig()
	if err := validateConfig(validConfig); err != nil {
		t.Errorf("Default config should be valid, got error: %v", err)
	}

	// Test invalid API URL
	invalidConfig := getDefaultConfig()
	invalidConfig.API.BaseURL = ""
	if err := validateConfig(invalidConfig); err == nil {
		t.Error("Empty API URL should fail validation")
	} else {
		t.Logf("✅ Correctly rejected empty API URL: %v", err)
	}

	// Test invalid worker count
	invalidConfig2 := getDefaultConfig()
	invalidConfig2.Performance.MaxWorkers = 0
	if err := validateConfig(invalidConfig2); err == nil {
		t.Error("Zero workers should fail validation")
	} else {
		t.Logf("✅ Correctly rejected zero workers: %v", err)
	}
}

// TestLoadDefaultConfig tests loading default configuration
func TestLoadDefaultConfig(t *testing.T) {
	cfg, metadata, err := Load()
	if err != nil {
		t.Fatalf("Failed to load default config: %v", err)
	}

	if cfg == nil {
		t.Fatal("Config should not be nil")
	}

	if metadata.Source != LoadSourceDefault {
		t.Errorf("Expected default source, got %v", metadata.Source)
	}

	t.Logf("✅ Default config loaded successfully")
	t.Logf("   Source: %v", metadata.Source)
	t.Logf("   LoadedAt: %v", metadata.LoadedAt)
}

// TestGlobalConfigAccess tests the global config pattern
func TestGlobalConfigAccess(t *testing.T) {
	// Clear any existing global config
	globalConfig = nil
	globalMetadata = nil

	// Get should auto-load
	cfg := Get()
	if cfg == nil {
		t.Fatal("Get() should never return nil")
	}

	// Should return the same instance
	cfg2 := Get()
	if cfg != cfg2 {
		t.Error("Get() should return the same instance")
	}

	t.Logf("✅ Global config access working")
}

// TestConfigFilePaths tests path helper methods
func TestConfigFilePaths(t *testing.T) {
	cfg := getDefaultConfig()

	inputPath := cfg.GetInputFilePath()
	outputPath := cfg.GetOutputFilePath()

	if inputPath == "" {
		t.Error("Input file path should not be empty")
	}

	if outputPath == "" {
		t.Error("Output file path should not be empty")
	}

	t.Logf("✅ File paths working")
	t.Logf("   Input: %s", inputPath)
	t.Logf("   Output: %s", outputPath)
}

// TestConfigSaveLoad tests saving and loading config from file
func TestConfigSaveLoad(t *testing.T) {
	// Create a temporary config file
	tempDir := t.TempDir()
	configPath := filepath.Join(tempDir, "test_config.json")

	// Save default config to file
	originalConfig := getDefaultConfig()
	originalConfig.API.MaxRetries = 99 // Unique value for testing

	err := originalConfig.SaveToFile(configPath)
	if err != nil {
		t.Fatalf("Failed to save config: %v", err)
	}

	// Load config from file
	loadedConfig, metadata, err := Load(configPath)
	if err != nil {
		t.Fatalf("Failed to load config from file: %v", err)
	}

	// Verify it loaded from file
	if metadata.Source != LoadSourceFile {
		t.Errorf("Expected file source, got %v", metadata.Source)
	}

	if metadata.FilePath != configPath {
		t.Errorf("Expected file path %s, got %s", configPath, metadata.FilePath)
	}

	// Verify the unique value was preserved
	if loadedConfig.API.MaxRetries != 99 {
		t.Errorf("Expected MaxRetries=99, got %d", loadedConfig.API.MaxRetries)
	}

	t.Logf("✅ Config save/load working")
	t.Logf("   File: %s", configPath)
	t.Logf("   MaxRetries preserved: %d", loadedConfig.API.MaxRetries)
}

// TestConfigValidation tests various validation scenarios
func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name        string
		modifyFunc  func(*Config)
		shouldError bool
	}{
		{
			name:        "Valid config",
			modifyFunc:  func(c *Config) {}, // No modification
			shouldError: false,
		},
		{
			name: "Negative timeout",
			modifyFunc: func(c *Config) {
				c.API.Timeout = -1 * time.Second
			},
			shouldError: true,
		},
		{
			name: "Too many workers",
			modifyFunc: func(c *Config) {
				c.Performance.MaxWorkers = 50
			},
			shouldError: true,
		},
		{
			name: "Invalid log level",
			modifyFunc: func(c *Config) {
				c.Logging.LogLevel = 99
			},
			shouldError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cfg := getDefaultConfig()
			tt.modifyFunc(cfg)

			err := validateConfig(cfg)
			if tt.shouldError && err == nil {
				t.Errorf("Expected validation error for %s", tt.name)
			}
			if !tt.shouldError && err != nil {
				t.Errorf("Unexpected validation error for %s: %v", tt.name, err)
			}

			if err != nil {
				t.Logf("✅ Validation correctly caught: %v", err)
			}
		})
	}
}
