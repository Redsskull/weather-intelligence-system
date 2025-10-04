package main

import (
	"encoding/json"
	"log"
	"os"

	"weather-collector/collector"
	"weather-collector/config"
)

func main() {
	log.Println("🌤️  Weather Data Collector v1.0 starting...")

	// Load configuration
	cfg, metadata, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Log configuration info
	log.Printf("Configuration loaded from: %v", metadata.Source)
	if cfg.Logging.EnableDebug {
		log.Printf("API URL: %s", cfg.API.BaseURL)
		log.Printf("Max workers: %d", cfg.Performance.MaxWorkers)
		log.Printf("Input file: %s", cfg.GetInputFilePath())
		log.Printf("Output file: %s", cfg.GetOutputFilePath())
	}

	// Read locations from Python input file using config
	locations, err := readLocationsFromFile(cfg.GetInputFilePath())
	if err != nil {
		log.Fatalf("Failed to read locations from %s: %v", cfg.GetInputFilePath(), err)
	}

	log.Printf("Collecting weather for %d locations...", len(locations))

	// Use collector package for actual work
	results := collector.CollectWeatherData(locations)

	// Write results for Python to read using config
	err = writeResultsToFile(results, cfg.GetOutputFilePath())
	if err != nil {
		log.Fatalf("Failed to write results to %s: %v", cfg.GetOutputFilePath(), err)
	}

	log.Printf("Successfully completed collection for %d locations", len(results))

	// Show metrics if enabled
	if cfg.Logging.EnableMetrics {
		successful := 0
		for _, result := range results {
			if result.Success {
				successful++
			}
		}
		log.Printf("Metrics: %d/%d locations successful (%.1f%%)",
			successful, len(results), float64(successful)/float64(len(results))*100)
	}
}

// readLocationsFromFile reads location data from JSON file (Go 1.16+ style)
func readLocationsFromFile(filename string) ([]collector.Location, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	var locations []collector.Location
	err = json.Unmarshal(data, &locations)
	return locations, err
}

// writeResultsToFile writes results to JSON file (Go 1.16+ style)
func writeResultsToFile(results []collector.WeatherResult, filename string) error {
	data, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filename, data, 0644)
}
