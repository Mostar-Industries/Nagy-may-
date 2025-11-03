"use client"

import { useState } from "react"
import type { Detection } from "./use-realtime-detections"

export interface UseEventSummaryReturn {
  summary: string | null
  isLoading: boolean
  error: string | null
  summarizeEvents: (detections: Detection[]) => Promise<string>
}

export function useEventSummary(): UseEventSummaryReturn {
  const [summary, setSummary] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const summarizeEvents = async (detections: Detection[]): Promise<string> => {
    setIsLoading(true)
    setError(null)

    try {
      // Prepare event data for summarization
      const eventData = detections.map((d) => ({
        timestamp: d.detection_timestamp,
        species: (d.environmental_context as any)?.species || "Mastomys natalensis",
        confidence: (d.risk_assessment as any)?.confidence || 0.85,
        risk_level: (d.risk_assessment as any)?.risk_level || "MEDIUM",
        location: { lat: d.latitude, lng: d.longitude },
      }))

      const response = await fetch("/api/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: "Please summarize these recent rodent detection events",
          events: eventData,
          action: "summarize",
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to get event summary")
      }

      const data = await response.json()
      const summaryText = data.response || data.summary || "No summary available"
      setSummary(summaryText)
      return summaryText
    } catch (err) {
      console.error("[v0] Event summary error:", err)
      const errorMsg = err instanceof Error ? err.message : "Unknown error"
      setError(errorMsg)

      // Return fallback summary
      const fallbackSummary = `Detected ${detections.length} rodent(s) across ${new Set(detections.map((d) => d.source)).size} locations. Average confidence: ${((detections.reduce((sum, d) => sum + ((d.risk_assessment as any)?.confidence || 0.85), 0) / detections.length) * 100).toFixed(0)}%.`
      setSummary(fallbackSummary)
      return fallbackSummary
    } finally {
      setIsLoading(false)
    }
  }

  return { summary, isLoading, error, summarizeEvents }
}
