"use client"

import { useEffect, useState, useCallback } from "react"
import { createClient } from "@/lib/supabase/client"
import type { RealtimeChannel } from "@supabase/supabase-js"

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

export interface UseRealtimeDetectionsReturn {
  detections: Detection[]
  isLoading: boolean
  isConnected: boolean
  error: string | null
  lastUpdate: string | null
}

export function useRealtimeDetections(): UseRealtimeDetectionsReturn {
  const [detections, setDetections] = useState<Detection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<string | null>(null)

  const supabase = createClient()

  useEffect(() => {
    const initializeRealtimeDetections = async () => {
      try {
        // Fetch initial detections from the correct table
        const { data, error: fetchError } = await supabase
          .from("detections")
          .select("*")
          .order("detected_at", { ascending: false })
          .limit(100)

        if (fetchError) {
          setError(fetchError.message)
          setIsLoading(false)
          return
        }

        // Map detections to expected format
        const mappedData = (data || []).map((d: any) => ({
          id: d.id,
          latitude: d.latitude,
          longitude: d.longitude,
          detection_timestamp: d.detected_at,
          detection_count: 1,
          source: d.source || 'system',
          environmental_context: {
            species: d.species,
            species_confidence: d.confidence,
            label: d.label,
            bbox: d.bbox
          },
          risk_assessment: {
            confidence: d.confidence,
            risk_score: 0.5,
            risk_level: d.confidence > 0.8 ? 'HIGH' : d.confidence > 0.6 ? 'MEDIUM' : 'LOW'
          },
          created_at: d.detected_at
        }))

        setDetections(mappedData)
        setIsLoading(false)
        setIsConnected(true)

        // Subscribe to new insertions
        const channel: RealtimeChannel = supabase
          .channel("public:detections")
          .on(
            "postgres_changes",
            {
              event: "INSERT",
              schema: "public",
              table: "detections",
            },
            (payload: any) => {
              const detection = payload.new
              const newDetection = {
                id: detection.id,
                latitude: detection.latitude,
                longitude: detection.longitude,
                detection_timestamp: detection.detected_at,
                detection_count: 1,
                source: detection.source || 'system',
                environmental_context: {
                  species: detection.species,
                  species_confidence: detection.confidence,
                  label: detection.label,
                  bbox: detection.bbox
                },
                risk_assessment: {
                  confidence: detection.confidence,
                  risk_score: 0.5,
                  risk_level: detection.confidence > 0.8 ? 'HIGH' : detection.confidence > 0.6 ? 'MEDIUM' : 'LOW'
                },
                created_at: detection.detected_at
              }
              setDetections((prev) => [newDetection, ...prev])
              setLastUpdate(new Date().toISOString())
              console.log("[Realtime] New detection received:", newDetection)
            },
          )
          .subscribe()

        return () => {
          supabase.removeChannel(channel)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
        setIsLoading(false)
        setIsConnected(false)
      }
    }

    initializeRealtimeDetections()
  }, [supabase])

  const addDetection = useCallback((detection: Detection) => {
    setDetections((prev) => {
      // Avoid duplicates
      const exists = prev.some((d) => d.id === detection.id)
      if (exists) return prev
      return [detection, ...prev].slice(0, 100) // Keep last 100
    })
    setLastUpdate(new Date().toISOString())
  }, [])

  return {
    detections,
    isLoading,
    isConnected,
    error,
    lastUpdate,
  }
}
