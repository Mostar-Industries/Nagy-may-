"use client"

import { useModelMetrics } from "@/hooks/use-model-metrics"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, LineChart, Line } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

export default function ModelChart() {
  const { metrics, isLoading, error } = useModelMetrics()

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold flex items-center">🧠 Model Performance</h3>
        </div>
        <div className="p-4 h-64 flex items-center justify-center text-gray-500">Loading metrics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold flex items-center">🧠 Model Performance</h3>
        </div>
        <div className="p-4 text-red-500">{error}</div>
      </div>
    )
  }

  const confidenceData = [
    { species: "M. natalensis", confidence: metrics?.species_accuracy?.natalensis || 94 },
    { species: "M. coucha", confidence: metrics?.species_accuracy?.coucha || 87 },
    { species: "Other rodent", confidence: metrics?.species_accuracy?.other || 92 },
  ]

  const performanceData = [
    { model: "YOLOv8n", inference_ms: metrics?.inference_time_ms?.avg || 45, memory_mb: 180 },
    { model: "YOLOv8s", inference_ms: 72, memory_mb: 340 },
    { model: "YOLOv8m", inference_ms: 145, memory_mb: 720 },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 className="font-semibold flex items-center">🧠 Model Performance</h3>
        <div className="flex space-x-2">
          <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
            Real-time
          </button>
          <button className="text-xs px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">Stats</button>
        </div>
      </div>

      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-semibold mb-3">Species Detection Accuracy</h4>
        <ChartContainer
          config={{
            confidence: {
              label: "Accuracy %",
              color: "hsl(var(--chart-1))",
            },
          }}
          className="h-64"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={confidenceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="species" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="confidence" fill="var(--color-confidence)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>

      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-semibold mb-3">Model Inference Time (ms)</h4>
        <ChartContainer
          config={{
            inference_ms: {
              label: "Time (ms)",
              color: "hsl(var(--chart-2))",
            },
          }}
          className="h-40"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line type="monotone" dataKey="inference_ms" stroke="var(--color-inference_ms)" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-4 gap-2 text-center">
        <div>
          <div className="text-lg font-bold text-green-500">{metrics?.overall_accuracy || 94}%</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Overall Accuracy</div>
        </div>
        <div>
          <div className="text-lg font-bold text-blue-500">{metrics?.precision || 92}%</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Precision</div>
        </div>
        <div>
          <div className="text-lg font-bold text-purple-500">{metrics?.recall || 89}%</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Recall</div>
        </div>
        <div>
          <div className="text-lg font-bold text-orange-500">{metrics?.inference_time_ms?.avg?.toFixed(0) || 45}ms</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Avg Inference</div>
        </div>
      </div>
    </div>
  )
}
