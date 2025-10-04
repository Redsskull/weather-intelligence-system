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

	// Extract weather data from first timeseries entry
	if len(apiResp.Properties.Timeseries) == 0 {
		return WeatherResult{
			Location: loc,
			Success:  false,
			Error:    "No weather data in API response",
		}
	}

	firstEntry := apiResp.Properties.Timeseries[0]
	details := firstEntry.Data.Instant.Details

	// Extract precipitation data from next_1_hours forecast
	precipitationMm := 0.0
	precipitationProb := 0.0
	symbolCode := ""

	if firstEntry.Data.Next1Hours.Details.PrecipitationAmount > 0 {
		precipitationMm = firstEntry.Data.Next1Hours.Details.PrecipitationAmount
	}
	if firstEntry.Data.Next1Hours.Details.ProbabilityOfPrecipitation > 0 {
		precipitationProb = firstEntry.Data.Next1Hours.Details.ProbabilityOfPrecipitation
	}
	if firstEntry.Data.Next1Hours.Summary.SymbolCode != "" {
		symbolCode = firstEntry.Data.Next1Hours.Summary.SymbolCode
	}

	return WeatherResult{
		Location:                 loc,
		Temperature:              details.AirTemperature,
		Pressure:                 details.AirPressureAtSeaLevel,
		Humidity:                 details.RelativeHumidity,
		WindSpeed:                details.WindSpeed,
		WindDirection:            details.WindFromDirection,
		CloudCover:               details.CloudAreaFraction,
		PrecipitationMm:          precipitationMm,
		PrecipitationProbability: precipitationProb,
		SymbolCode:               symbolCode,
		Success:                  true,
		Timestamp:                firstEntry.Time,
	}
}
