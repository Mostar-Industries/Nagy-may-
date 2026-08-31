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
  environmental_context: {
    consciousness_state?: string
    detections?: any[]
    [key: string]: any
  }
  risk_assessment: {
    risk_score?: number
    risk_level?: string
    odu_pattern?: string
    ubuntu_guidance?: string
    reasoning?: string[]
    [key: string]: any
  }
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
        // Fetch initial detections
        const { data, error: fetchError } = await supabase
          .from("detection_patterns")
          .select("*")
          .order("detection_timestamp", { ascending: false })
          .limit(100)

        if (fetchError) {
          setError(fetchError.message)
          setIsLoading(false)
          return
        }

        setDetections(data || [])
        setIsLoading(false)
        setIsConnected(true)

        // Subscribe to new insertions
        const channel: RealtimeChannel = supabase
          .channel("public:detection_patterns")
          .on(
            "postgres_changes",
            {
              event: "INSERT",
              schema: "public",
              table: "detection_patterns",
            },
            (payload: any) => {
              const newDetection = payload.new as Detection
              setDetections((prev) => [newDetection, ...prev])
              setLastUpdate(new Date().toISOString())
              console.log("[v0] New detection received:", newDetection)
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
