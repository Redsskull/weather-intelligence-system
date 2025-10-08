package collector

// Location represents a geographic location for weather data collection
type Location struct {
	Name string  `json:"name"` // Human-readable name
	Lat  float64 `json:"lat"`  // Latitude (-90 to 90)
	Lon  float64 `json:"lon"`  // Longitude (-180 to 180)
}

// WeatherResult represents the collected weather data for a location
type WeatherResult struct {
	Location                 Location         `json:"location"`
	CurrentWeather           WeatherPoint     `json:"current_weather"`
	Forecast                 []WeatherPoint   `json:"forecast,omitempty"`
	Success                  bool             `json:"success"`
	Error                    string           `json:"error,omitempty"`
}

// WeatherPoint represents a single weather reading with timestamp
type WeatherPoint struct {
	Timestamp                string  `json:"timestamp"`
	Temperature              float64 `json:"temperature"`
	Pressure                 float64 `json:"pressure"`
	Humidity                 float64 `json:"humidity"`
	WindSpeed                float64 `json:"wind_speed"`
	WindDirection            float64 `json:"wind_direction"`
	CloudCover               float64 `json:"cloud_cover"`
	PrecipitationMm          float64 `json:"precipitation_mm"`
	PrecipitationProbability float64 `json:"precipitation_probability"`
	SymbolCode               string  `json:"symbol_code"`
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
						WindFromDirection     float64 `json:"wind_from_direction"`
						CloudAreaFraction     float64 `json:"cloud_area_fraction"`
					} `json:"details"`
				} `json:"instant"`
				Next1Hours struct {
					Summary struct {
						SymbolCode string `json:"symbol_code"`
					} `json:"summary"`
					Details struct {
						PrecipitationAmount        float64 `json:"precipitation_amount"`
						ProbabilityOfPrecipitation float64 `json:"probability_of_precipitation"`
					} `json:"details"`
				} `json:"next_1_hours"`
			} `json:"data"`
		} `json:"timeseries"`
	} `json:"properties"`
}
