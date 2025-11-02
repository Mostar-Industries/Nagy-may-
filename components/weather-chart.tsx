export default function WeatherChart() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center">☁️ Weather & Climate Impact</h3>
      </div>
      <div className="p-4">
        <div className="grid grid-cols-3 gap-4 text-center mb-4">
          <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900">
            <div className="text-2xl font-bold">28°C</div>
            <div className="text-xs text-gray-500 dark:text-gray-300 mt-1">Temperature</div>
          </div>
          <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900">
            <div className="text-2xl font-bold">76%</div>
            <div className="text-xs text-gray-500 dark:text-gray-300 mt-1">Humidity</div>
          </div>
          <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900">
            <div className="text-2xl font-bold">12mm</div>
            <div className="text-xs text-gray-500 dark:text-gray-300 mt-1">Rainfall</div>
          </div>
        </div>
        <div className="h-32 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center text-gray-500">
          Weather chart placeholder
        </div>
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-300">
        <span>ℹ️</span> Next 3 days expected to increase suitability scores by 1-2 points
      </div>
    </div>
  )
}
