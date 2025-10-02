package collector

// Location represents a geographic location for weather data collection
type Location struct {
	Name string  `json:"name"` // Human-readable name
	Lat  float64 `json:"lat"`  // Latitude (-90 to 90)
	Lon  float64 `json:"lon"`  // Longitude (-180 to 180)
}

// WeatherResult represents the collected weather data for a location
type WeatherResult struct {
	Location    Location `json:"location"`
	Temperature float64  `json:"temperature"`
	Pressure    float64  `json:"pressure"`
	Humidity    float64  `json:"humidity"`
	WindSpeed   float64  `json:"wind_speed"`
	Success     bool     `json:"success"`
	Error       string   `json:"error,omitempty"`
	Timestamp   string   `json:"timestamp"`
}

// APIResponse represents the met.no API response structure
type APIResponse struct {
	Type     string `json:"type"`
	Geometry struct {
		Coordinates []float64 `json:"coordinates"`
	} `json:"geometry"`
	Properties struct {
		Timeseries []struct {
			Time string `json:"time"`
			Data struct {
				Instant struct {
					Details struct {
						AirTemperature        float64 `json:"air_temperature"`
						AirPressureAtSeaLevel float64 `json:"air_pressure_at_sea_level"`
						RelativeHumidity      float64 `json:"relative_humidity"`
						WindSpeed             float64 `json:"wind_speed"`
					} `json:"details"`
				} `json:"instant"`
			} `json:"data"`
		} `json:"timeseries"`
	} `json:"properties"`
}
