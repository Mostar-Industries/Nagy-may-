"use client"

import { useMemo } from "react"
import type { Detection } from "./use-realtime-detections"

export interface MapMarker {
  id: number
  latitude: number
  longitude: number
  title: string
  riskLevel: "low" | "medium" | "high" | "critical"
  confidence: number
  timestamp: string
  source: string
  color: string
}

export function useDetectionMapData(detections: Detection[]): MapMarker[] {
  return useMemo(() => {
    return detections.map((detection) => {
      const riskScore = detection.risk_assessment?.risk_score || 0
      const confidence = detection.risk_assessment?.confidence || 0

      // Determine risk level
      let riskLevel: "low" | "medium" | "high" | "critical"
      let color: string

      if (riskScore > 0.85) {
        riskLevel = "critical"
        color = "#dc2626" // Red
      } else if (riskScore > 0.7) {
        riskLevel = "high"
        color = "#ea580c" // Orange
      } else if (riskScore > 0.5) {
        riskLevel = "medium"
        color = "#eab308" // Yellow
      } else {
        riskLevel = "low"
        color = "#22c55e" // Green
      }

      return {
        id: detection.id,
        latitude: Number(detection.latitude),
        longitude: Number(detection.longitude),
        title: `Detection: ${detection.source}`,
        riskLevel,
        confidence,
        timestamp: detection.detection_timestamp,
        source: detection.source,
        color,
      }
    })
  }, [detections])
}
