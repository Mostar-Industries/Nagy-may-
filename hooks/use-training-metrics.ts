"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase/client"

export interface TrainingMetric {
  id: string
  session_id: string
  epoch: number
  box_loss: number | null
  cls_loss: number | null
  dfl_loss: number | null
  total_loss: number | null
  precision: number | null
  recall: number | null
  map50: number | null
  map50_95: number | null
  learning_rate: number | null
  epoch_time_seconds: number | null
  gpu_memory_mb: number | null
  recorded_at: string
}

export function useTrainingMetrics(sessionId: string | null) {
  const [metrics, setMetrics] = useState<TrainingMetric[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const fetchMetrics = async () => {
    if (!sessionId) {
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch(`/api/training/metrics?session_id=${sessionId}`)
      const data = await response.json()

      if (data.success) {
        setMetrics(data.metrics)
      } else {
        setError(data.error)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch metrics")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!sessionId) return

    fetchMetrics()

    // Set up Supabase realtime subscription for metrics
    const supabase = createClient()
    
    const channel = supabase
      .channel(`training_metrics_${sessionId}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "training_metrics",
          filter: `session_id=eq.${sessionId}`,
        },
        (payload) => {
          console.log("Training metric change:", payload)
          
          if (payload.eventType === "INSERT") {
            setMetrics((prev) => {
              // Insert in sorted order by epoch
              const newMetric = payload.new as TrainingMetric
              const updated = [...prev, newMetric]
              return updated.sort((a, b) => a.epoch - b.epoch)
            })
          } else if (payload.eventType === "UPDATE") {
            setMetrics((prev) =>
              prev.map((metric) =>
                metric.id === payload.new.id
                  ? (payload.new as TrainingMetric)
                  : metric
              )
            )
          }
        }
      )
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          setIsConnected(true)
        } else if (status === "CLOSED" || status === "CHANNEL_ERROR") {
          setIsConnected(false)
        }
      })

    return () => {
      supabase.removeChannel(channel)
    }
  }, [sessionId])

  // Calculate derived metrics
  const latestMetric = metrics[metrics.length - 1] || null
  const bestMap50 = metrics.reduce((max, m) => 
    (m.map50 || 0) > max ? (m.map50 || 0) : max, 0
  )
  const bestMap50_95 = metrics.reduce((max, m) => 
    (m.map50_95 || 0) > max ? (m.map50_95 || 0) : max, 0
  )
  const avgLoss = metrics.length > 0
    ? metrics.reduce((sum, m) => sum + (m.total_loss || 0), 0) / metrics.length
    : 0

  return {
    metrics,
    isLoading,
    error,
    isConnected,
    refetch: fetchMetrics,
    latestMetric,
    bestMap50,
    bestMap50_95,
    avgLoss,
  }
}
