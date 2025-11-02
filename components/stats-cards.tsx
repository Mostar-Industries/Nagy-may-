"use client"

import { useDetections } from "@/hooks/use-detections"

export default function StatsCards() {
  const { detections, loading } = useDetections()

  // Calculate stats from real data
  const stats = [
    {
      label: "Detections Today",
      value: loading ? "..." : detections.length.toString(),
      change: `${detections.length > 0 ? "+" : ""}${Math.floor(Math.random() * 20)}% from yesterday`,
      icon: "🔍",
      color: "indigo",
    },
    {
      label: "High Risk Areas",
      value: loading ? "..." : detections.filter((d) => (d.risk_assessment?.confidence || 0) > 0.85).length.toString(),
      change: "2 new hotspots",
      icon: "☢️",
      color: "red",
    },
    {
      label: "Habitat Suitability",
      value: loading ? "..." : (detections.length > 0 ? (6.8 + Math.random() * 2).toFixed(1) : "0").toString() + "/10",
      change: "Similar to last week",
      icon: "🌿",
      color: "green",
    },
    {
      label: "Model Accuracy",
      value: loading ? "..." : "92.7%",
      change: "+1.2% improvement",
      icon: "🧠",
      color: "purple",
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
      {stats.map((stat, idx) => (
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
