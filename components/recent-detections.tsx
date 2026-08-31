"use client"

import { useRealtimeDetections } from "@/hooks/use-realtime-detections"

export default function RecentDetections() {
  const { detections, isLoading, isConnected, error } = useRealtimeDetections()

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

  const displayDetections = detections.slice(0, 10).map((d) => {
    const envContext = d.environmental_context || {}
    const riskContext = d.risk_assessment || {}

    return {
      id: d.id,
      time: new Date(d.detection_timestamp).toLocaleTimeString(),
      location: `(${d.latitude.toFixed(4)}, ${d.longitude.toFixed(4)})`,
      species: envContext.detections?.[0]?.species || "Mastomys natalensis",
      speciesConfidence: envContext.detections?.[0]?.confidence || riskContext.confidence || 0.85,
      confidence: `${((riskContext.confidence || 0.85) * 100).toFixed(0)}%`,
      riskScore: `${((riskContext.risk_score || 0.5) * 100).toFixed(0)}%`,
      riskLevel: riskContext.risk_level?.toUpperCase() || "MEDIUM",
      odu: riskContext.odu_pattern || "N/A",
      state: envContext.consciousness_state || "DORMANT",
      guidance: riskContext.ubuntu_guidance || "Monitoring required",
      source: d.source || "unknown",
    }
  })

  const getSpeciesBadgeColor = (species: string) => {
    if (species.includes("natalensis")) {
      return "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200"
    }
    if (species.includes("coucha")) {
      return "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200"
    }
    return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
  }

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "CRITICAL":
        return "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200"
      case "HIGH":
        return "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200"
      case "MEDIUM":
        return "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200"
      case "LOW":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
      default:
        return "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold flex items-center">🔍 Recent Detections ({detections.length})</h3>
          {isConnected && <span className="text-green-400 text-xs px-2 py-1 bg-green-900 rounded">● Live</span>}
        </div>
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
                Species
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Confidence
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Risk Level
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Ifá Odu / Consciousness
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Ubuntu Guidance
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  Loading detections...
                </td>
              </tr>
            ) : displayDetections.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  No detections found - waiting for data
                </td>
              </tr>
            ) : (
              displayDetections.map((detection) => (
                <tr key={detection.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {detection.time}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getSpeciesBadgeColor(detection.species)}`}
                    >
                      {detection.species}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">
                      {(detection.speciesConfidence * 100).toFixed(0)}% confidence
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{detection.location}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                      {detection.confidence}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskLevelColor(detection.riskLevel)}`}
                    >
                      {detection.riskLevel} {detection.riskScore}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-amber-600 dark:text-amber-400">{detection.odu.replace('_', ' ')}</div>
                    <div className="text-xs text-gray-500 uppercase tracking-tighter">{detection.state}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate" title={detection.guidance}>
                    {detection.guidance}
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
