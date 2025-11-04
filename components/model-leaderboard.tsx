"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trophy, Medal, Award } from "lucide-react"

interface LeaderboardEntry {
  id: string
  session_name: string
  model_type: string
  dataset_name: string | null
  final_map50: number
  final_map50_95: number
  final_precision: number
  final_recall: number
  epochs: number
  duration_seconds: number | null
  avg_inference_ms: number | null
  throughput_fps: number | null
  created_at: string
  rank: number
}

export function ModelLeaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await fetch('/api/training/leaderboard')
        const data = await response.json()
        if (data.success) {
          setLeaderboard(data.leaderboard)
        }
      } catch (error) {
        console.error("Error fetching leaderboard:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchLeaderboard()
  }, [])

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />
    if (rank === 3) return <Award className="h-5 w-5 text-amber-600" />
    return null
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return "N/A"
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-muted-foreground">Loading leaderboard...</p>
        </CardContent>
      </Card>
    )
  }

  if (leaderboard.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-muted-foreground">No completed models yet</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Performing Models</CardTitle>
        <CardDescription>
          Models ranked by mAP50-95 performance
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {leaderboard.map((entry) => (
            <div
              key={entry.id}
              className="flex items-center gap-4 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              {/* Rank */}
              <div className="flex items-center justify-center w-12 h-12">
                {getRankIcon(entry.rank) || (
                  <span className="text-2xl font-bold text-muted-foreground">
                    {entry.rank}
                  </span>
                )}
              </div>

              {/* Model Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold">{entry.session_name}</h3>
                  <Badge variant="outline">{entry.model_type}</Badge>
                  {entry.dataset_name && (
                    <Badge variant="secondary">{entry.dataset_name}</Badge>
                  )}
                </div>
                <div className="grid grid-cols-5 gap-4 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">mAP50-95</p>
                    <p className="font-bold text-primary">{(entry.final_map50_95 * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">mAP50</p>
                    <p className="font-medium">{(entry.final_map50 * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Precision</p>
                    <p className="font-medium">{(entry.final_precision * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Recall</p>
                    <p className="font-medium">{(entry.final_recall * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="font-medium">{formatDuration(entry.duration_seconds)}</p>
                  </div>
                </div>
                
                {/* Inference Performance */}
                {entry.avg_inference_ms && (
                  <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                    <span>Inference: {entry.avg_inference_ms.toFixed(1)}ms</span>
                    {entry.throughput_fps && (
                      <span>Throughput: {entry.throughput_fps.toFixed(1)} FPS</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
