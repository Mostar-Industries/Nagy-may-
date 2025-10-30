"use client"

import { useState, useEffect } from "react"

interface WeatherData {
  main: {
    temp: number;
    humidity: number;
  };
  rain?: {
    "1h": number;
  };
}

export default function WeatherChart() {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        // TODO: Make location dynamic based on user's map view or profile
        const lat = 6.5244 // Lagos, Nigeria
        const lon = 3.3792

        const response = await fetch(`/api/current-weather?lat=${lat}&lon=${lon}`)
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || "Failed to fetch weather data")
        }
        const data = await response.json()
        setWeather(data)
      } catch (err) {
        const message = err instanceof Error ? err.message : "An unknown error occurred"
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    fetchWeather()
  }, [])

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center">☁️ Weather & Climate Impact</h3>
      </div>
      <div className="p-4">
        {loading ? (
          <div className="h-48 flex items-center justify-center text-gray-500">Loading weather...</div>
        ) : error ? (
          <div className="h-48 flex items-center justify-center text-red-500">Error: {error}</div>
        ) : weather ? (
          <>
            <div className="grid grid-cols-3 gap-4 text-center mb-4">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900">
                <div className="text-2xl font-bold">{Math.round(weather.main.temp)}°C</div>
                <div className="text-xs text-gray-500 dark:text-gray-300 mt-1">Temperature</div>
              </div>
              <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900">
                <div className="text-2xl font-bold">{weather.main.humidity}%</div>
                <div className="text-xs text-gray-500 dark:text-gray-300 mt-1">Humidity</div>
              </div>
              <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900">
                <div className="text-2xl font-bold">{weather.rain?.["1h"] || 0}mm</div>
                <div className="text-xs text-gray-500 dark:text-gray-300 mt-1">Rainfall (1h)</div>
              </div>
            </div>
            <div className="h-32 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center text-gray-500">
              Weather chart placeholder
            </div>
          </>
        ) : null}
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-300">
        <span>ℹ️</span> Next 3 days expected to increase suitability scores by 1-2 points
      </div>
    </div>
  )
}
