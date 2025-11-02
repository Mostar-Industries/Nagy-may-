"use client"

import { useEffect, useState } from "react"

export interface Detection {
  id: number
  latitude: number
  longitude: number
  detection_timestamp: string
  detection_count: number
  source: string
  environmental_context: Record<string, any>
  risk_assessment: Record<string, any>
  created_at: string
}

export function useDetections() {
  const [detections, setDetections] = useState<Detection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDetections = async () => {
      try {
        setLoading(true)
        const response = await fetch("/api/detections")
        if (!response.ok) throw new Error("Failed to fetch detections")
        const data = await response.json()
        setDetections(data)
        setError(null)
      } catch (err) {
        console.error("[v0] Error fetching detections:", err)
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    fetchDetections()
    const interval = setInterval(fetchDetections, 30000)
    return () => clearInterval(interval)
  }, [])

  return { detections, loading, error }
}
