"use client"

import { useEffect, useState, useCallback } from "react"
import { createClient } from "@/lib/supabase/client"
import type { RealtimeChannel } from "@supabase/supabase-js"

export interface EnhancedDetection {
  id: string
  image_id: string
  latitude: number
  longitude: number
  species: string
  detection_type: 'single' | 'pair' | 'group' | 'colony'
  gender: string
  age_estimate: string
  health_status: string
  threat_level: number
  confidence: number
  behavior_tags: string[]
  physical_attributes: any
  tracking_status: string
  detected_at: string
  last_seen: string
  colony_id?: string
  colony_name?: string
}

export interface ColonyInfo {
  id: string
  colony_name: string
  species: string
  estimated_population: number
  threat_level: number
  status: string
  last_activity: string
  location_center: any
}

export interface TrackingStats {
  totalDetections: number
  activeTracking: number
  coloniesActive: number
  speciesBreakdown: Record<string, number>
  genderDistribution: Record<string, number>
  threatLevels: {
    critical: number
    high: number
    medium: number
    low: number
  }
  detectionTypes: Record<string, number>
}

export interface UseEnhancedTrackingReturn {
  detections: EnhancedDetection[]
  colonies: ColonyInfo[]
  stats: TrackingStats
  isLoading: boolean
  isConnected: boolean
  error: string | null
  lastUpdate: string | null
  refreshData: () => Promise<void>
}

export function useEnhancedTracking(): UseEnhancedTrackingReturn {
  const [detections, setDetections] = useState<EnhancedDetection[]>([])
  const [colonies, setColonies] = useState<ColonyInfo[]>([])
  const [stats, setStats] = useState<TrackingStats>({
    totalDetections: 0,
    activeTracking: 0,
    coloniesActive: 0,
    speciesBreakdown: {},
    genderDistribution: {},
    threatLevels: { critical: 0, high: 0, medium: 0, low: 0 },
    detectionTypes: {}
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<string | null>(null)

  const supabase = createClient()

  const calculateStats = useCallback((dets: EnhancedDetection[]) => {
    const speciesBreakdown: Record<string, number> = {}
    const genderDistribution: Record<string, number> = {}
    const detectionTypes: Record<string, number> = {}
    const threatLevels = { critical: 0, high: 0, medium: 0, low: 0 }

    dets.forEach(det => {
      // Species
      speciesBreakdown[det.species] = (speciesBreakdown[det.species] || 0) + 1

      // Gender
      genderDistribution[det.gender] = (genderDistribution[det.gender] || 0) + 1

      // Detection types
      detectionTypes[det.detection_type] = (detectionTypes[det.detection_type] || 0) + 1

      // Threat levels
      if (det.threat_level >= 8) threatLevels.critical++
      else if (det.threat_level >= 6) threatLevels.high++
      else if (det.threat_level >= 3) threatLevels.medium++
      else threatLevels.low++
    })

    return {
      totalDetections: dets.length,
      activeTracking: dets.filter(d => d.tracking_status === 'active').length,
      coloniesActive: new Set(dets.map(d => d.colony_id).filter(Boolean)).size,
      speciesBreakdown,
      genderDistribution,
      threatLevels,
      detectionTypes
    }
  }, [])

  const refreshData = useCallback(async () => {
    try {
      // Fetch active detections with colony info
      const { data: detectionsData, error: detError } = await supabase
        .from("detections")
        .select(`
          *,
          colonies:colony_id (
            id,
            colony_name,
            estimated_population,
            threat_level,
            status
          )
        `)
        .eq("tracking_status", "active")
        .order("detected_at", { ascending: false })
        .limit(200)

      if (detError) throw detError

      const formattedDetections = detectionsData?.map((d: any) => ({
        id: d.id,
        image_id: d.image_id,
        latitude: d.latitude,
        longitude: d.longitude,
        species: d.species,
        detection_type: d.detection_type,
        gender: d.gender,
        age_estimate: d.age_estimate,
        health_status: d.health_status,
        threat_level: d.threat_level,
        confidence: d.confidence,
        behavior_tags: d.behavior_tags || [],
        physical_attributes: d.physical_attributes,
        tracking_status: d.tracking_status,
        detected_at: d.detected_at,
        last_seen: d.last_seen,
        colony_id: d.colony_id,
        colony_name: d.colonies?.colony_name
      })) || []

      setDetections(formattedDetections)
      setStats(calculateStats(formattedDetections))

      // Fetch active colonies
      const { data: coloniesData, error: colError } = await supabase
        .from("colonies")
        .select("*")
        .eq("status", "active")
        .order("last_activity", { ascending: false })

      if (colError) throw colError
      setColonies(coloniesData || [])

      setLastUpdate(new Date().toISOString())
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
      console.error("[Enhanced Tracking] Refresh error:", err)
    }
  }, [supabase, calculateStats])

  useEffect(() => {
    const initializeTracking = async () => {
      try {
        await refreshData()
        setIsLoading(false)
        setIsConnected(true)

        // Subscribe to real-time detection updates
        const detectionChannel: RealtimeChannel = supabase
          .channel("enhanced:detections")
          .on(
            "postgres_changes",
            {
              event: "INSERT",
              schema: "public",
              table: "detections",
            },
            (payload: any) => {
              console.log("[Enhanced Tracking] New detection:", payload)
              const newDetection = {
                id: payload.new.id,
                image_id: payload.new.image_id,
                latitude: payload.new.latitude,
                longitude: payload.new.longitude,
                species: payload.new.species,
                detection_type: payload.new.detection_type,
                gender: payload.new.gender,
                age_estimate: payload.new.age_estimate,
                health_status: payload.new.health_status,
                threat_level: payload.new.threat_level,
                confidence: payload.new.confidence,
                behavior_tags: payload.new.behavior_tags || [],
                physical_attributes: payload.new.physical_attributes,
                tracking_status: payload.new.tracking_status,
                detected_at: payload.new.detected_at,
                last_seen: payload.new.last_seen,
                colony_id: payload.new.colony_id
              }

              setDetections(prev => {
                const updated = [newDetection, ...prev]
                setStats(calculateStats(updated))
                return updated
              })
              setLastUpdate(new Date().toISOString())
            }
          )
          .on(
            "postgres_changes",
            {
              event: "UPDATE",
              schema: "public",
              table: "detections",
            },
            (payload: any) => {
              setDetections(prev =>
                prev.map(d => (d.id === payload.new.id ? { ...d, ...payload.new } : d))
              )
              setLastUpdate(new Date().toISOString())
            }
          )
          .subscribe()

        // Subscribe to colony updates
        const colonyChannel: RealtimeChannel = supabase
          .channel("enhanced:colonies")
          .on(
            "postgres_changes",
            {
              event: "*",
              schema: "public",
              table: "colonies",
            },
            () => {
              refreshData()
            }
          )
          .subscribe()

        return () => {
          supabase.removeChannel(detectionChannel)
          supabase.removeChannel(colonyChannel)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
        setIsLoading(false)
        setIsConnected(false)
      }
    }

    initializeTracking()
  }, [supabase, refreshData, calculateStats])

  return {
    detections,
    colonies,
    stats,
    isLoading,
    isConnected,
    error,
    lastUpdate,
    refreshData
  }
}
