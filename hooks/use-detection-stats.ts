"use client"

import { useMemo } from "react"
import type { Detection } from "./use-realtime-detections"

export interface DetectionStats {
  total: number
  highRisk: number
  avgConfidence: number
  latestTime: string | null
  byRegion: Record<string, number>
  detections24h: number
  consciousnessState: string
}

export function useDetectionStats(detections: Detection[]): DetectionStats {
  return useMemo(() => {
    const now = new Date()
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)

    const stats: DetectionStats = {
      total: detections.length,
      highRisk: 0,
      avgConfidence: 0,
      latestTime: null,
      byRegion: {},
      detections24h: 0,
      consciousnessState: "DORMANT",
    }

    // Sort by timestamp to get the truly latest
    const sorted = [...detections].sort(
      (a, b) => new Date(b.detection_timestamp).getTime() - new Date(a.detection_timestamp).getTime(),
    )

    if (sorted.length > 0) {
      stats.consciousnessState = sorted[0].environmental_context?.consciousness_state || "DORMANT"
    }

    let confidenceSum = 0
    let confidenceCount = 0

    detections.forEach((detection) => {
      // High risk threshold
      const riskScore = detection.risk_assessment?.risk_score || 0
      if (riskScore > 0.7) {
        stats.highRisk++
      }

      // Average confidence
      const confidence = detection.risk_assessment?.confidence || 0
      if (confidence > 0) {
        confidenceSum += confidence
        confidenceCount++
      }

      // Latest timestamp
      if (!stats.latestTime || new Date(detection.detection_timestamp) > new Date(stats.latestTime)) {
        stats.latestTime = detection.detection_timestamp
      }

      // 24h count
      if (new Date(detection.detection_timestamp) > oneDayAgo) {
        stats.detections24h++
      }

      // By region/source
      const region = detection.source || "unknown"
      stats.byRegion[region] = (stats.byRegion[region] || 0) + 1
    })

    if (confidenceCount > 0) {
      stats.avgConfidence = confidenceSum / confidenceCount
    }

    return stats
  }, [detections])
}
