"use client"

import { useDetections } from "@/hooks/use-detections"

export default function RecentDetections() {
  const { detections, loading, error } = useDetections()

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold flex items-center">🔍 Recent Detections</h3>
        </div>
        <div className="p-4 text-red-500">Error loading detections: {error}</div>
      </div>
    )
  }

  const displayDetections = detections.slice(0, 10).map((d) => ({
    time: new Date(d.detection_timestamp).toLocaleTimeString(),
    location: `(${d.latitude.toFixed(4)}, ${d.longitude.toFixed(4)})`,
    confidence: `${((d.risk_assessment?.confidence || 0.85) * 100).toFixed(0)}%`,
    temp: `${d.environmental_context?.temperature || "N/A"}°C`,
    humidity: `${d.environmental_context?.humidity || "N/A"}%`,
  }))

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 className="font-semibold flex items-center">🔍 Recent Detections ({detections.length})</h3>
        <button className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 flex items-center">
          🔽 Filter
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Confidence
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Environmental Data
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                  Loading detections...
                </td>
              </tr>
            ) : displayDetections.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                  No detections found
                </td>
              </tr>
            ) : (
              displayDetections.map((detection, idx) => (
                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {detection.time}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{detection.location}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                      {detection.confidence}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    <div>Temp: {detection.temp}</div>
                    <div>Humidity: {detection.humidity}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <a
                      href="#"
                      className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300 mr-3"
                    >
                      View
                    </a>
                    <a href="#" className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300">
                      Flag
                    </a>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
