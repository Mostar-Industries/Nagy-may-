interface FlightData {
  id: string
  ident: string
  operator?: string
  aircraft_type?: string
  origin?: Airport
  destination?: Airport
  departure_time?: string
  arrival_time?: string
  status?: string
  position?: {
    latitude: number
    longitude: number
    altitude: number
    heading: number
    speed: number
  }
}

interface Airport {
  id: string
  name: string
  code: string
  latitude: number
  longitude: number
}

interface FlightTrack {
  positions: Array<{
    latitude: number
    longitude: number
    altitude: number
    timestamp: string
  }>
}

class FlightAwareAPI {
  private baseUrl: string
  private apiKey: string

  constructor() {
    this.baseUrl = process.env.FLIGHTAWARE_BASE_URL || "https://aeroapi.flightaware.com/aeroapi"
    this.apiKey = process.env.FLIGHTAWARE_API_KEY || ""
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      ...options,
      headers: {
        "x-apikey": this.apiKey,
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`FlightAware API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Get flight information by identifier
  async getFlight(ident: string): Promise<FlightData> {
    return this.makeRequest(`/flights/${ident}`)
  }

  // Get flight position
  async getFlightPosition(id: string): Promise<any> {
    return this.makeRequest(`/flights/${id}/position`)
  }

  // Get flight track/route
  async getFlightTrack(id: string): Promise<FlightTrack> {
    return this.makeRequest(`/flights/${id}/track`)
  }

  // Get flight map data
  async getFlightMap(id: string): Promise<any> {
    return this.makeRequest(`/flights/${id}/map`)
  }

  // Search flights
  async searchFlights(params: {
    query?: string
    start?: string
    end?: string
    max_pages?: number
  }): Promise<any> {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value) queryParams.append(key, value.toString())
    })

    return this.makeRequest(`/flights/search?${queryParams.toString()}`)
  }

  // Get airport information
  async getAirport(id: string): Promise<Airport> {
    return this.makeRequest(`/airports/${id}`)
  }

  // Get airport flights
  async getAirportFlights(id: string, type: "arrivals" | "departures" = "departures"): Promise<any> {
    return this.makeRequest(`/airports/${id}/flights/${type}`)
  }

  // Get nearby airports
  async getNearbyAirports(latitude: number, longitude: number, radius = 50): Promise<Airport[]> {
    return this.makeRequest(`/airports/nearby?latitude=${latitude}&longitude=${longitude}&radius=${radius}`)
  }

  // Get weather forecast for airport
  async getAirportWeatherForecast(id: string): Promise<any> {
    return this.makeRequest(`/airports/${id}/weather/forecast`)
  }

  // Get weather observations for airport
  async getAirportWeatherObservations(id: string): Promise<any> {
    return this.makeRequest(`/airports/${id}/weather/observations`)
  }

  // Get aircraft owner information
  async getAircraftOwner(registration: string): Promise<any> {
    return this.makeRequest(`/aircraft/${registration}/owner`)
  }

  // Get aircraft type information
  async getAircraftType(type: string): Promise<any> {
    return this.makeRequest(`/aircraft/types/${type}`)
  }

  // Get historical flight data
  async getHistoricalFlight(ident: string): Promise<any> {
    return this.makeRequest(`/history/flights/${ident}`)
  }

  // Get last flight for aircraft
  async getLastFlight(registration: string): Promise<any> {
    return this.makeRequest(`/history/aircraft/${registration}/last_flight`)
  }

  // Get account usage
  async getAccountUsage(): Promise<any> {
    return this.makeRequest("/account/usage")
  }

  // Create alert
  async createAlert(alertData: any): Promise<any> {
    return this.makeRequest("/alerts", {
      method: "POST",
      body: JSON.stringify(alertData),
    })
  }

  // Get alerts
  async getAlerts(): Promise<any> {
    return this.makeRequest("/alerts")
  }

  // Update alert
  async updateAlert(id: string, alertData: any): Promise<any> {
    return this.makeRequest(`/alerts/${id}`, {
      method: "PUT",
      body: JSON.stringify(alertData),
    })
  }

  // Delete alert
  async deleteAlert(id: string): Promise<any> {
    return this.makeRequest(`/alerts/${id}`, {
      method: "DELETE",
    })
  }
}

export const flightAwareAPI = new FlightAwareAPI()
export type { FlightData, Airport, FlightTrack }
