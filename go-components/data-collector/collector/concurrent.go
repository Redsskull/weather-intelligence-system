package collector

import (
	"log"
	"sync"

	"weather-collector/config"
)

// CollectWeatherData orchestrates weather collection for multiple locations
// Uses config for performance settings and rate limiting
func CollectWeatherData(locations []Location) []WeatherResult {
	cfg := config.Get()

	log.Printf("Starting weather collection for %d locations...", len(locations))
	if cfg.Logging.EnableDebug {
		log.Printf("Using max workers: %d", cfg.Performance.MaxWorkers)
	}

	// Create job and result channels
	jobs := make(chan job, len(locations))
	results := make(chan workerResult, len(locations))

	// Start worker pool
	var wg sync.WaitGroup
	for w := 0; w < cfg.Performance.MaxWorkers; w++ {
		wg.Add(1)
		go worker(jobs, results, &wg)
	}

	// Send jobs to workers
	go func() {
		defer close(jobs)
		for i, location := range locations {
			jobs <- job{index: i, location: location}
		}
	}()

	// Close results channel when all workers are done
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results
	jobResults := make([]WeatherResult, len(locations))
	completed := 0
	for res := range results {
		jobResults[res.index] = res.result
		completed++

		// Log the result
		if res.result.Success {
			log.Printf("✅ Success: %s - %.1f°C", res.result.Location.Name, res.result.CurrentWeather.Temperature)
		} else {
			log.Printf("❌ Failed: %s - %s", res.result.Location.Name, res.result.Error)
		}
	}

	log.Printf("Completed collection for %d/%d locations", completed, len(locations))
	return jobResults
}

// worker processes jobs from the jobs channel and sends results to the results channel
func worker(jobs <-chan job, results chan<- workerResult, wg *sync.WaitGroup) {
	defer wg.Done()

	for job := range jobs {
		result := FetchWeatherForLocation(job.location)
		results <- workerResult{index: job.index, result: result}
	}
}
