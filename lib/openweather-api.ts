interface WeatherData {
  temperature: number
  humidity: number
  pressure: number
  windSpeed: number
  windDirection: number
  visibility: number
  cloudCover: number
  precipitation: number
  description: string
  icon: string
}

interface WeatherForecast {
  datetime: string
  temperature: {
    min: number
    max: number
  }
  humidity: number
  precipitation: number
  windSpeed: number
  description: string
  icon: string
}

interface LocationWeather {
  current: WeatherData
  forecast: WeatherForecast[]
  location: {
    name: string
    country: string
    latitude: number
    longitude: number
  }
}

class OpenWeatherAPI {
  private baseUrl: string
  private apiKey: string

  constructor() {
    this.baseUrl = "https://api.openweathermap.org/data/2.5"
    this.apiKey = process.env.NEXT_PUBLIC_OPENWEATHER_API_KEY || ""
  }

  private async makeRequest(endpoint: string): Promise<any> {
    const url = `${this.baseUrl}${endpoint}&appid=${this.apiKey}&units=metric`

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`OpenWeather API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Get current weather by coordinates
  async getCurrentWeather(lat: number, lon: number): Promise<WeatherData> {
    const data = await this.makeRequest(`/weather?lat=${lat}&lon=${lon}`)

    return {
      temperature: data.main.temp,
      humidity: data.main.humidity,
      pressure: data.main.pressure,
      windSpeed: data.wind?.speed || 0,
      windDirection: data.wind?.deg || 0,
      visibility: data.visibility || 0,
      cloudCover: data.clouds?.all || 0,
      precipitation: data.rain?.["1h"] || data.snow?.["1h"] || 0,
      description: data.weather[0]?.description || "",
      icon: data.weather[0]?.icon || "",
    }
  }

  // Get weather forecast by coordinates
  async getWeatherForecast(lat: number, lon: number): Promise<WeatherForecast[]> {
    const data = await this.makeRequest(`/forecast?lat=${lat}&lon=${lon}`)

    return data.list.map((item: any) => ({
      datetime: item.dt_txt,
      temperature: {
        min: item.main.temp_min,
        max: item.main.temp_max,
      },
      humidity: item.main.humidity,
      precipitation: item.rain?.["3h"] || item.snow?.["3h"] || 0,
      windSpeed: item.wind?.speed || 0,
      description: item.weather[0]?.description || "",
      icon: item.weather[0]?.icon || "",
    }))
  }

  // Get complete weather data for location
  async getLocationWeather(lat: number, lon: number): Promise<LocationWeather> {
    const [current, forecast] = await Promise.all([this.getCurrentWeather(lat, lon), this.getWeatherForecast(lat, lon)])

    // Get location name from reverse geocoding
    const geoData = await this.makeRequest(`/weather?lat=${lat}&lon=${lon}`)

    return {
      current,
      forecast: forecast.slice(0, 8), // Next 24 hours (8 x 3-hour intervals)
      location: {
        name: geoData.name,
        country: geoData.sys.country,
        latitude: lat,
        longitude: lon,
      },
    }
  }

  // Get weather by city name
  async getWeatherByCity(cityName: string): Promise<LocationWeather> {
    const data = await this.makeRequest(`/weather?q=${encodeURIComponent(cityName)}`)
    return this.getLocationWeather(data.coord.lat, data.coord.lon)
  }

  // Get air quality data
  async getAirQuality(lat: number, lon: number): Promise<any> {
    const url = `http://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${this.apiKey}`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`OpenWeather Air Quality API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Get historical weather data
  async getHistoricalWeather(lat: number, lon: number, timestamp: number): Promise<any> {
    const url = `https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=${lat}&lon=${lon}&dt=${timestamp}&appid=${this.apiKey}&units=metric`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`OpenWeather Historical API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }
}

export const openWeatherAPI = new OpenWeatherAPI()
export type { WeatherData, WeatherForecast, LocationWeather }
