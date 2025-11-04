"use client"

import { useEffect, useState } from "react"

export interface ActiveTrainingSession {
  id: string
  session_name: string
  model_type: string
  status: string
  epochs: number
  started_at: string | null
  duration_seconds: number | null
  final_map50: number | null
  final_map50_95: number | null
  completed_epochs: number
  current_epoch: number | null
  avg_loss: number | null
  best_map50: number | null
  recent_metrics: Array<{
    epoch: number
    loss: number
    map50: number
    precision: number
    recall: number
  }>
}

export function useActiveTraining() {
  const [activeSessions, setActiveSessions] = useState<ActiveTrainingSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchActiveSessions = async () => {
    try {
      const response = await fetch('/api/training/active')
      const data = await response.json()

      if (data.success) {
        setActiveSessions(data.activeSessions)
      } else {
        setError(data.error)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch active sessions")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchActiveSessions()

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchActiveSessions, 5000)

    return () => clearInterval(interval)
  }, [])

  return {
    activeSessions,
    isLoading,
    error,
    refetch: fetchActiveSessions,
  }
}
