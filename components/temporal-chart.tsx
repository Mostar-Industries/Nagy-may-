"use client"

import { useEffect, useRef } from "react"
import { useDetections } from "@/hooks/use-detections"

export default function TemporalChart() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { detections, loading } = useDetections()

  useEffect(() => {
    if (!canvasRef.current || loading) return

    const ctx = canvasRef.current.getContext("2d")
    if (!ctx) return

    const width = canvasRef.current.width
    const height = canvasRef.current.height

    ctx.fillStyle = "#f3f4f6"
    ctx.fillRect(0, 0, width, height)

    const data =
      detections.length > 0
        ? detections.slice(0, 12).map((d) => d.detection_count || 1)
        : [45, 60, 75, 82, 90, 105, 95, 110, 98, 85, 70, 55]

    const maxValue = Math.max(...data, 110)
    const padding = 40

    ctx.strokeStyle = "#4f46e5"
    ctx.lineWidth = 2
    ctx.beginPath()

    data.forEach((value, idx) => {
      const x = padding + (idx / (data.length - 1)) * (width - 2 * padding)
      const y = height - padding - (value / maxValue) * (height - 2 * padding)

      if (idx === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()
  }, [detections, loading])

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center">📈 Detection Patterns Over Time</h3>
      </div>
      <div className="p-4">
        {loading ? (
          <div className="w-full h-64 flex items-center justify-center text-gray-500">Loading chart data...</div>
        ) : (
          <canvas ref={canvasRef} width={600} height={250} className="w-full" />
        )}
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <div className="flex space-x-4">
          <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
            Daily
          </button>
          <button className="text-xs px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">Weekly</button>
          <button className="text-xs px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">Monthly</button>
        </div>
        <button className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
          ⬇️ Export
        </button>
      </div>
    </div>
  )
}
