package main

import (
	"encoding/json"
	"log"
	"os"

	"weather-collector/collector"
)

func main() {
	log.Println("🌤️  Weather Data Collector v1.0 starting...")

	// Read locations from Python input file
	locations, err := readLocationsFromFile("../../data/integration/input_locations.json")
	if err != nil {
		log.Fatalf("Failed to read locations: %v", err)
	}

	log.Printf("Collecting weather for %d locations...", len(locations))

	// Use collector package for actual work
	results := collector.CollectWeatherData(locations)

	// Write results for Python to read
	err = writeResultsToFile(results, "../../data/integration/output_weather.json")
	if err != nil {
		log.Fatalf("Failed to write results: %v", err)
	}

	log.Printf("Successfully completed collection for %d locations", len(results))
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
