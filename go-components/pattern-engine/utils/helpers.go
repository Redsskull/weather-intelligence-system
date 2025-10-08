package utils

import "pattern-engine/models"

// GetTemperatureValues extracts temperature values from readings
func GetTemperatureValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.Temperature)
	}
	return values
}

// GetPressureValues extracts pressure values from readings
func GetPressureValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.Pressure)
	}
	return values
}

// GetHumidityValues extracts humidity values from readings
func GetHumidityValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.Humidity)
	}
	return values
}

// GetWindSpeedValues extracts wind speed values from readings
func GetWindSpeedValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.WindSpeed)
	}
	return values
}

// GetPrecipitationValues extracts precipitation values from readings
func GetPrecipitationValues(readings []models.WeatherPoint) []float64 {
	var values []float64
	for _, r := range readings {
		values = append(values, r.PrecipitationMm)
	}
	return values
}