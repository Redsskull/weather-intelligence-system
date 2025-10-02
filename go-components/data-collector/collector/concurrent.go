package collector

import "log"

// CollectWeatherData orchestrates weather collection for multiple locations
// For now, this is a simple sequential implementation
// Later we'll make it concurrent with goroutines
func CollectWeatherData(locations []Location) []WeatherResult {
	log.Printf("Starting weather collection for %d locations...", len(locations))

	var results []WeatherResult

	// For now: simple sequential collection
	// TODO: Make this concurrent with goroutines
	for i, location := range locations {
		log.Printf("Fetching weather for location %d/%d: %s", i+1, len(locations), location.Name)
		result := FetchWeatherForLocation(location)
		results = append(results, result)

		if result.Success {
			log.Printf("✅ Success: %s - %.1f°C", location.Name, result.Temperature)
		} else {
			log.Printf("❌ Failed: %s - %s", location.Name, result.Error)
		}
	}

	return results
}
