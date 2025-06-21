import { openWeatherAPI, type WeatherData, type LocationWeather } from "./openweather-api"

interface HabitatWeatherAnalysis {
  suitabilityScore: number
  riskLevel: "low" | "medium" | "high"
  factors: {
    temperature: {
      value: number
      score: number
      optimal: boolean
    }
    humidity: {
      value: number
      score: number
      optimal: boolean
    }
    precipitation: {
      value: number
      score: number
      impact: string
    }
    pressure: {
      value: number
      score: number
    }
  }
  recommendations: string[]
  forecast: {
    nextWeek: {
      suitabilityTrend: "increasing" | "decreasing" | "stable"
      expectedChange: number
    }
  }
}

interface LocationHabitatData {
  location: {
    name: string
    coordinates: [number, number]
  }
  weather: LocationWeather
  habitatAnalysis: HabitatWeatherAnalysis
  lastUpdated: string
}

class WeatherHabitatService {
  // Optimal ranges for Mastomys Natalensis habitat
  private readonly OPTIMAL_RANGES = {
    temperature: { min: 20, max: 32, ideal: 26 }, // Celsius
    humidity: { min: 60, max: 85, ideal: 75 }, // Percentage
    precipitation: { min: 5, max: 25, ideal: 15 }, // mm per day
    pressure: { min: 1000, max: 1020, ideal: 1013 }, // hPa
  }

  private calculateTemperatureScore(temp: number): number {
    const { min, max, ideal } = this.OPTIMAL_RANGES.temperature

    if (temp < min || temp > max) return 0

    const distanceFromIdeal = Math.abs(temp - ideal)
    const maxDistance = Math.max(ideal - min, max - ideal)

    return Math.max(0, 100 - (distanceFromIdeal / maxDistance) * 100)
  }

  private calculateHumidityScore(humidity: number): number {
    const { min, max, ideal } = this.OPTIMAL_RANGES.humidity

    if (humidity < min || humidity > max) return Math.max(0, 50 - Math.abs(humidity - ideal))

    const distanceFromIdeal = Math.abs(humidity - ideal)
    const maxDistance = Math.max(ideal - min, max - ideal)

    return Math.max(0, 100 - (distanceFromIdeal / maxDistance) * 100)
  }

  private calculatePrecipitationScore(precipitation: number): number {
    const { min, max, ideal } = this.OPTIMAL_RANGES.precipitation

    if (precipitation < min) return 30 // Too dry
    if (precipitation > max) return 20 // Too wet

    const distanceFromIdeal = Math.abs(precipitation - ideal)
    const maxDistance = Math.max(ideal - min, max - ideal)

    return Math.max(0, 100 - (distanceFromIdeal / maxDistance) * 100)
  }

  private calculatePressureScore(pressure: number): number {
    const { min, max, ideal } = this.OPTIMAL_RANGES.pressure

    const distanceFromIdeal = Math.abs(pressure - ideal)
    const maxDistance = Math.max(ideal - min, max - ideal)

    return Math.max(0, 100 - (distanceFromIdeal / maxDistance) * 100)
  }

  private analyzeWeatherForHabitat(weather: WeatherData): HabitatWeatherAnalysis {
    const tempScore = this.calculateTemperatureScore(weather.temperature)
    const humidityScore = this.calculateHumidityScore(weather.humidity)
    const precipitationScore = this.calculatePrecipitationScore(weather.precipitation)
    const pressureScore = this.calculatePressureScore(weather.pressure)

    // Weighted average (temperature and humidity are most important)
    const suitabilityScore = tempScore * 0.35 + humidityScore * 0.35 + precipitationScore * 0.2 + pressureScore * 0.1

    const riskLevel: "low" | "medium" | "high" =
      suitabilityScore >= 70 ? "high" : suitabilityScore >= 40 ? "medium" : "low"

    const recommendations: string[] = []

    if (tempScore < 50) {
      recommendations.push(
        weather.temperature < this.OPTIMAL_RANGES.temperature.min
          ? "Temperature too low for optimal habitat conditions"
          : "Temperature too high for optimal habitat conditions",
      )
    }

    if (humidityScore < 50) {
      recommendations.push(
        weather.humidity < this.OPTIMAL_RANGES.humidity.min
          ? "Low humidity may reduce habitat suitability"
          : "High humidity may increase disease transmission risk",
      )
    }

    if (precipitationScore < 50) {
      recommendations.push(
        weather.precipitation < this.OPTIMAL_RANGES.precipitation.min
          ? "Dry conditions may force rodents to seek water sources near human settlements"
          : "Heavy rainfall may increase rodent movement and shelter-seeking behavior",
      )
    }

    return {
      suitabilityScore: Math.round(suitabilityScore),
      riskLevel,
      factors: {
        temperature: {
          value: weather.temperature,
          score: Math.round(tempScore),
          optimal: tempScore >= 70,
        },
        humidity: {
          value: weather.humidity,
          score: Math.round(humidityScore),
          optimal: humidityScore >= 70,
        },
        precipitation: {
          value: weather.precipitation,
          score: Math.round(precipitationScore),
          impact:
            precipitationScore >= 70
              ? "optimal"
              : weather.precipitation > this.OPTIMAL_RANGES.precipitation.max
                ? "high"
                : "low",
        },
        pressure: {
          value: weather.pressure,
          score: Math.round(pressureScore),
        },
      },
      recommendations,
      forecast: {
        nextWeek: {
          suitabilityTrend: "stable", // This would be calculated from forecast data
          expectedChange: 0,
        },
      },
    }
  }

  async getLocationHabitatData(lat: number, lon: number): Promise<LocationHabitatData> {
    try {
      const weather = await openWeatherAPI.getLocationWeather(lat, lon)
      const habitatAnalysis = this.analyzeWeatherForHabitat(weather.current)

      // Calculate forecast trend
      const forecastScores = weather.forecast.slice(0, 8).map((f) => {
        const avgTemp = (f.temperature.min + f.temperature.max) / 2
        return (
          this.calculateTemperatureScore(avgTemp) * 0.5 +
          this.calculatePrecipitationScore(f.precipitation) * 0.3 +
          this.calculateHumidityScore(f.humidity) * 0.2
        )
      })

      const currentScore = habitatAnalysis.suitabilityScore
      const avgForecastScore = forecastScores.reduce((a, b) => a + b, 0) / forecastScores.length
      const trendChange = avgForecastScore - currentScore

      habitatAnalysis.forecast.nextWeek = {
        suitabilityTrend: trendChange > 5 ? "increasing" : trendChange < -5 ? "decreasing" : "stable",
        expectedChange: Math.round(trendChange),
      }

      return {
        location: {
          name: weather.location.name,
          coordinates: [lat, lon],
        },
        weather,
        habitatAnalysis,
        lastUpdated: new Date().toISOString(),
      }
    } catch (error) {
      console.error("Error fetching habitat weather data:", error)
      throw error
    }
  }

  async getMultipleLocationsHabitatData(
    locations: Array<{ name: string; lat: number; lon: number }>,
  ): Promise<LocationHabitatData[]> {
    const promises = locations.map((loc) => this.getLocationHabitatData(loc.lat, loc.lon))
    return Promise.all(promises)
  }

  // Get habitat suitability for Nigerian states
  async getNigerianStatesHabitatData(): Promise<LocationHabitatData[]> {
    const nigerianStates = [
      { name: "Lagos", lat: 6.5244, lon: 3.3792 },
      { name: "Kano", lat: 12.0022, lon: 8.592 },
      { name: "Ibadan", lat: 7.3775, lon: 3.947 },
      { name: "Abuja", lat: 9.0765, lon: 7.3986 },
      { name: "Port Harcourt", lat: 4.8156, lon: 7.0498 },
      { name: "Benin City", lat: 6.335, lon: 5.6037 },
      { name: "Maiduguri", lat: 11.8311, lon: 13.151 },
      { name: "Zaria", lat: 11.0804, lon: 7.7076 },
      { name: "Aba", lat: 5.1066, lon: 7.3667 },
      { name: "Jos", lat: 9.9288, lon: 8.8921 },
    ]

    return this.getMultipleLocationsHabitatData(nigerianStates)
  }
}

export const weatherHabitatService = new WeatherHabitatService()
export type { HabitatWeatherAnalysis, LocationHabitatData }
