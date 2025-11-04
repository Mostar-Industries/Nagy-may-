"use client"

import { useEffect, useState } from "react"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TrainingMetricsChart } from "@/components/training-metrics-chart"
import { useTrainingMetrics } from "@/hooks/use-training-metrics"

interface TrainingSessionDetailsProps {
  sessionId: string
  onClose: () => void
}

interface SessionData {
  id: string
  session_name: string
  model_type: string
  dataset_name: string | null
  epochs: number
  batch_size: number
  learning_rate: number | null
  status: string
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  final_map50: number | null
  final_map50_95: number | null
  final_precision: number | null
  final_recall: number | null
  final_loss: number | null
  config: Record<string, any>
  created_at: string
}

export function TrainingSessionDetails({ sessionId, onClose }: TrainingSessionDetailsProps) {
  const [session, setSession] = useState<SessionData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { metrics, latestMetric, bestMap50, bestMap50_95 } = useTrainingMetrics(sessionId)

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await fetch(`/api/training/sessions/${sessionId}`)
        const data = await response.json()
        if (data.success) {
          setSession(data.session)
        }
      } catch (error) {
        console.error("Error fetching session:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchSession()
  }, [sessionId])

  if (isLoading || !session) {
    return (
      <Sheet open={true} onOpenChange={onClose}>
        <SheetContent className="sm:max-w-4xl overflow-y-auto">
          <p className="text-center text-muted-foreground">Loading session details...</p>
        </SheetContent>
      </Sheet>
    )
  }

  const formatDate = (date: string | null) => {
    if (!date) return "N/A"
    return new Date(date).toLocaleString()
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return "N/A"
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours}h ${minutes}m ${secs}s`
  }

  return (
    <Sheet open={true} onOpenChange={onClose}>
      <SheetContent className="sm:max-w-4xl overflow-y-auto">
        <SheetHeader>
          <div className="flex items-center justify-between">
            <SheetTitle>{session.session_name}</SheetTitle>
            <Badge>{session.status}</Badge>
          </div>
          <SheetDescription>
            {session.model_type} - Started {formatDate(session.started_at)}
          </SheetDescription>
        </SheetHeader>

        <Tabs defaultValue="overview" className="mt-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Model Type</p>
                <p className="font-medium">{session.model_type}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Dataset</p>
                <p className="font-medium">{session.dataset_name || "N/A"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Epochs</p>
                <p className="font-medium">{session.epochs}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Batch Size</p>
                <p className="font-medium">{session.batch_size}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Learning Rate</p>
                <p className="font-medium">{session.learning_rate || "N/A"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="font-medium">{formatDuration(session.duration_seconds)}</p>
              </div>
            </div>

            <div className="pt-4 border-t">
              <h3 className="font-semibold mb-4">Final Results</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">mAP50</p>
                  <p className="text-2xl font-bold">
                    {session.final_map50 ? (session.final_map50 * 100).toFixed(2) + "%" : "N/A"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">mAP50-95</p>
                  <p className="text-2xl font-bold">
                    {session.final_map50_95 ? (session.final_map50_95 * 100).toFixed(2) + "%" : "N/A"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Precision</p>
                  <p className="text-2xl font-bold">
                    {session.final_precision ? (session.final_precision * 100).toFixed(2) + "%" : "N/A"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Recall</p>
                  <p className="text-2xl font-bold">
                    {session.final_recall ? (session.final_recall * 100).toFixed(2) + "%" : "N/A"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Final Loss</p>
                  <p className="text-2xl font-bold">
                    {session.final_loss ? session.final_loss.toFixed(6) : "N/A"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Best Epoch</p>
                  <p className="text-2xl font-bold">
                    {latestMetric?.epoch || "N/A"}
                  </p>
                </div>
              </div>
            </div>

            {metrics.length > 0 && (
              <div className="pt-4 border-t">
                <h3 className="font-semibold mb-4">Best Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Best mAP50</p>
                    <p className="text-lg font-bold text-primary">
                      {(bestMap50 * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Best mAP50-95</p>
                    <p className="text-lg font-bold text-primary">
                      {(bestMap50_95 * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="metrics" className="mt-4">
            <TrainingMetricsChart sessionId={sessionId} />
          </TabsContent>

          <TabsContent value="config" className="mt-4">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Training Configuration</h3>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(session.config, null, 2)}
                </pre>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Created At</p>
                  <p className="font-medium">{formatDate(session.created_at)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Started At</p>
                  <p className="font-medium">{formatDate(session.started_at)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Completed At</p>
                  <p className="font-medium">{formatDate(session.completed_at)}</p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  )
}
