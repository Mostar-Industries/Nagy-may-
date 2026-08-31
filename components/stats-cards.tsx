"use client"

import { useRealtimeDetections } from "@/hooks/use-realtime-detections"
import { useDetectionStats } from "@/hooks/use-detection-stats"

export default function StatsCards() {
  const { detections, isLoading: isLoadingDetections } = useRealtimeDetections()
  const stats = useDetectionStats(detections)

  const statCards = [
    {
      label: "Detections Today",
      value: isLoadingDetections ? "..." : stats.detections24h.toString(),
      change: `${stats.total} total detections`,
      icon: "🔍",
      color: "indigo",
    },
    {
      label: "High Risk Areas",
      value: isLoadingDetections ? "..." : stats.highRisk.toString(),
      change: `${((stats.highRisk / Math.max(stats.total, 1)) * 100).toFixed(0)}% of total`,
      icon: "☢️",
      color: "red",
    },
    {
      label: "Consciousness State",
      value: isLoadingDetections ? "..." : stats.consciousnessState,
      change: "Mostar Grid awareness level",
      icon: "⚡",
      color: "purple",
    },
    {
      label: "Latest Detection",
      value: isLoadingDetections ? "..." : stats.latestTime ? new Date(stats.latestTime).toLocaleTimeString() : "N/A",
      change: "Most recent activity",
      icon: "⏰",
      color: "green",
    },
  ]

  const colorClasses = {
    indigo: "bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300",
    red: "bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300",
    green: "bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300",
    purple: "bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-300",
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      {statCards.map((stat, idx) => (
        <div
          key={idx}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg hover:-translate-y-1 transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.label}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
              <p className="text-xs text-green-500 mt-1">{stat.change}</p>
            </div>
            <div
              className={`h-12 w-12 rounded-full ${colorClasses[stat.color as keyof typeof colorClasses]} flex items-center justify-center text-xl`}
            >
              {stat.icon}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
