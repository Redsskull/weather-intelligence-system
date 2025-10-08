package collector

import (
	"encoding/json"
	"fmt"
	"net/http"

	"weather-collector/config"
)

// FetchWeatherForLocation makes an HTTP request to met.no API for a single location
func FetchWeatherForLocation(loc Location) WeatherResult {
	// Get configuration
	cfg := config.Get()

	// Build the API URL using config
	url := fmt.Sprintf("%s?lat=%.4f&lon=%.4f", cfg.API.BaseURL, loc.Lat, loc.Lon)

	// Create HTTP client with configured timeout
	client := &http.Client{
		Timeout: cfg.API.Timeout,
	}

	// Create request with proper User-Agent (met.no requirement)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    fmt.Sprintf("Failed to create request: %v", err),
		}
	}

	// Set User-Agent header from config (required by met.no)
	req.Header.Set("User-Agent", cfg.API.UserAgent)

	// Make the HTTP request
	resp, err := client.Do(req)
	if err != nil {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    fmt.Sprintf("HTTP request failed: %v", err),
		}
	}
	defer resp.Body.Close()

	// Check status code
	if resp.StatusCode != http.StatusOK {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    fmt.Sprintf("API returned status %d", resp.StatusCode),
		}
	}

	// Parse JSON response
	var apiResp APIResponse
	if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    fmt.Sprintf("Failed to parse JSON: %v", err),
		}
	}

	// Extract weather data from timeseries entries
	if len(apiResp.Properties.Timeseries) == 0 {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    "No weather data in API response",
		}
	}

	// Process all timeseries entries to extract current weather and forecasts
	var currentWeather *WeatherPoint
	var forecast []WeatherPoint

	for i, entry := range apiResp.Properties.Timeseries {
		details := entry.Data.Instant.Details

		// Extract precipitation data from next_1_hours forecast if available
		precipitationMm := 0.0
		precipitationProb := 0.0
		symbolCode := ""

		if entry.Data.Next1Hours.Details.PrecipitationAmount > 0 {
			precipitationMm = entry.Data.Next1Hours.Details.PrecipitationAmount
		}
		if entry.Data.Next1Hours.Details.ProbabilityOfPrecipitation > 0 {
			precipitationProb = entry.Data.Next1Hours.Details.ProbabilityOfPrecipitation
		}
		if entry.Data.Next1Hours.Summary.SymbolCode != "" {
			symbolCode = entry.Data.Next1Hours.Summary.SymbolCode
		}

		// Create weather point
		weatherPoint := WeatherPoint{
			Timestamp:                entry.Time,
			Temperature:              details.AirTemperature,
			Pressure:                 details.AirPressureAtSeaLevel,
			Humidity:                 details.RelativeHumidity,
			WindSpeed:                details.WindSpeed,
			WindDirection:            details.WindFromDirection,
			CloudCover:               details.CloudAreaFraction,
			PrecipitationMm:          precipitationMm,
			PrecipitationProbability: precipitationProb,
			SymbolCode:               symbolCode,
		}

		// First entry is current weather, rest are forecasts
		if i == 0 {
			currentWeather = &weatherPoint
		} else {
			forecast = append(forecast, weatherPoint)
		}
	}

	if currentWeather == nil {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    "No current weather data extracted",
		}
	}

	return WeatherResult{
		Location:       loc,
		CurrentWeather: *currentWeather,
		Forecast:       forecast,
		Success:        true,
	}
}
