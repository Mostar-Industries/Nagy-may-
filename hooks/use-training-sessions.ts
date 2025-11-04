"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase/client"

export interface TrainingSession {
  id: string
  session_name: string
  model_type: string
  dataset_name: string | null
  epochs: number
  batch_size: number
  learning_rate: number | null
  status: "pending" | "running" | "completed" | "failed" | "cancelled"
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  best_epoch: number | null
  final_map50: number | null
  final_map50_95: number | null
  final_precision: number | null
  final_recall: number | null
  final_loss: number | null
  model_path: string | null
  config: Record<string, any>
  created_at: string
  updated_at: string
}

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

export function useTrainingSessions(status?: string) {
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const fetchSessions = async () => {
    try {
      const url = status 
        ? `/api/training/sessions?status=${status}`
        : '/api/training/sessions'
      
      const response = await fetch(url)
      const data = await response.json()

      if (data.success) {
        setSessions(data.sessions)
      } else {
        setError(data.error)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch sessions")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSessions()

    // Set up Supabase realtime subscription
    const supabase = createClient()
    
    const channel = supabase
      .channel("training_sessions_changes")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "training_sessions",
          filter: status ? `status=eq.${status}` : undefined,
        },
        (payload) => {
          console.log("Training session change:", payload)
          
          if (payload.eventType === "INSERT") {
            setSessions((prev) => [payload.new as TrainingSession, ...prev])
          } else if (payload.eventType === "UPDATE") {
            setSessions((prev) =>
              prev.map((session) =>
                session.id === payload.new.id
                  ? (payload.new as TrainingSession)
                  : session
              )
            )
          } else if (payload.eventType === "DELETE") {
            setSessions((prev) =>
              prev.filter((session) => session.id !== payload.old.id)
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
  }, [status])

  return {
    sessions,
    isLoading,
    error,
    isConnected,
    refetch: fetchSessions,
  }
}
