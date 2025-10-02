package collector

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// FetchWeatherForLocation makes an HTTP request to met.no API for a single location
func FetchWeatherForLocation(loc Location) WeatherResult {
	// Build the API URL (same as Python version)
	url := fmt.Sprintf("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=%.4f&lon=%.4f",
		loc.Lat, loc.Lon)

	// Create HTTP client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
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

	// Set User-Agent header (required by met.no)
	req.Header.Set("User-Agent", "WeatherIntelligenceSystem-Go/1.0 (Educational Project)")

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

	return WeatherResult{
		Location:    loc,
		Temperature: details.AirTemperature,
		Pressure:    details.AirPressureAtSeaLevel,
		Humidity:    details.RelativeHumidity,
		WindSpeed:   details.WindSpeed,
		Success:     true,
		Timestamp:   firstEntry.Time,
	}
}
