package collector

import (
	"log"
	"time"

	"weather-collector/config"
)

// CollectWeatherData orchestrates weather collection for multiple locations
// Uses config for performance settings and rate limiting
func CollectWeatherData(locations []Location) []WeatherResult {
	cfg := config.Get()

	log.Printf("Starting weather collection for %d locations...", len(locations))
	if cfg.Logging.EnableDebug {
		log.Printf("Using collection delay: %v (rate limiting)", cfg.Performance.CollectionDelay)
	}

	var results []WeatherResult

	// Sequential collection with rate limiting
	// TODO: Make this concurrent with goroutines using cfg.Performance.MaxWorkers
	for i, location := range locations {
		log.Printf("Fetching weather for location %d/%d: %s", i+1, len(locations), location.Name)

		// Add rate limiting delay between requests (except for first request)
		if i > 0 {
			time.Sleep(cfg.Performance.CollectionDelay)
		}

		result := FetchWeatherForLocation(location)
		results = append(results, result)

		if result.Success {
			log.Printf("✅ Success: %s - %.1f°C", location.Name, result.CurrentWeather.Temperature)
		} else {
			log.Printf("❌ Failed: %s - %s", location.Name, result.Error)
		}
	}

	return results
}
