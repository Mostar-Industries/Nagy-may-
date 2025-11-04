"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Progress } from "@/components/ui/progress"
import { Activity, TrendingUp, Zap, Trophy, Play, Pause, StopCircle } from "lucide-react"
import { useActiveTraining } from "@/hooks/use-active-training"
import { useTrainingSessions } from "@/hooks/use-training-sessions"
import { TrainingMetricsChart } from "@/components/training-metrics-chart"
import { ModelLeaderboard } from "@/components/model-leaderboard"
import { TrainingSessionDetails } from "@/components/training-session-details"

export default function TrainingPage() {
  const { activeSessions, isLoading: activeLoading } = useActiveTraining()
  const { sessions, isLoading: sessionsLoading, isConnected } = useTrainingSessions()
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running": return "bg-green-500"
      case "completed": return "bg-blue-500"
      case "failed": return "bg-red-500"
      case "cancelled": return "bg-gray-500"
      default: return "bg-yellow-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running": return <Play className="h-4 w-4" />
      case "completed": return <Trophy className="h-4 w-4" />
      case "failed": return <StopCircle className="h-4 w-4" />
      default: return <Pause className="h-4 w-4" />
    }
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return "N/A"
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const formatNumber = (num: number | null, decimals = 4) => {
    if (num === null || num === undefined) return "N/A"
    return num.toFixed(decimals)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Model Training</h1>
          <p className="text-muted-foreground">
            Monitor and manage ML training sessions
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? "default" : "secondary"}>
            <Activity className="mr-1 h-3 w-3" />
            {isConnected ? "Live" : "Disconnected"}
          </Badge>
        </div>
      </div>

      {/* Active Training Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Sessions
            </CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {activeSessions.length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently training
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Sessions
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.length}
            </div>
            <p className="text-xs text-muted-foreground">
              All time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Best mAP50-95
            </CardTitle>
            <Trophy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(
                Math.max(...sessions.map(s => s.final_map50_95 || 0)),
                3
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Top performing model
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Completed
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.filter(s => s.status === "completed").length}
            </div>
            <p className="text-xs text-muted-foreground">
              Successful runs
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="active" className="space-y-4">
        <TabsList>
          <TabsTrigger value="active">Active Training</TabsTrigger>
          <TabsTrigger value="history">Training History</TabsTrigger>
          <TabsTrigger value="leaderboard">Model Leaderboard</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {activeLoading ? (
            <Card>
              <CardContent className="p-6">
                <p className="text-center text-muted-foreground">Loading active sessions...</p>
              </CardContent>
            </Card>
          ) : activeSessions.length === 0 ? (
            <Card>
              <CardContent className="p-6">
                <p className="text-center text-muted-foreground">No active training sessions</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {activeSessions.map((session) => (
                <Card key={session.id} className="cursor-pointer hover:bg-accent/50 transition-colors"
                  onClick={() => setSelectedSessionId(session.id)}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(session.status)}
                        <div>
                          <CardTitle className="text-lg">{session.session_name}</CardTitle>
                          <CardDescription>{session.model_type}</CardDescription>
                        </div>
                      </div>
                      <Badge className={getStatusColor(session.status)}>
                        {session.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Progress */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">
                          Epoch {session.current_epoch || 0} of {session.epochs}
                        </span>
                        <span className="font-medium">
                          {Math.round(((session.current_epoch || 0) / session.epochs) * 100)}%
                        </span>
                      </div>
                      <Progress 
                        value={((session.current_epoch || 0) / session.epochs) * 100} 
                      />
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Loss</p>
                        <p className="text-sm font-medium">{formatNumber(session.avg_loss)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">mAP50</p>
                        <p className="text-sm font-medium">{formatNumber(session.best_map50, 3)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Duration</p>
                        <p className="text-sm font-medium">{formatDuration(session.duration_seconds)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Epochs</p>
                        <p className="text-sm font-medium">{session.completed_epochs}/{session.epochs}</p>
                      </div>
                    </div>

                    {/* Recent Metrics Mini Chart */}
                    {session.recent_metrics && session.recent_metrics.length > 0 && (
                      <div className="mt-4">
                        <p className="text-xs text-muted-foreground mb-2">Recent Epochs</p>
                        <div className="flex items-end gap-1 h-16">
                          {session.recent_metrics.slice(-10).map((metric, idx) => {
                            const height = (metric.map50 || 0) * 100
                            return (
                              <div
                                key={idx}
                                className="flex-1 bg-primary/20 rounded-t hover:bg-primary/40 transition-colors"
                                style={{ height: `${height}%` }}
                                title={`Epoch ${metric.epoch}: mAP50 ${formatNumber(metric.map50, 3)}`}
                              />
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Training History</CardTitle>
              <CardDescription>
                All training sessions and their results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px]">
                <div className="space-y-4">
                  {sessionsLoading ? (
                    <p className="text-center text-muted-foreground">Loading sessions...</p>
                  ) : sessions.length === 0 ? (
                    <p className="text-center text-muted-foreground">No training sessions found</p>
                  ) : (
                    sessions.map((session) => (
                      <Card
                        key={session.id}
                        className="cursor-pointer hover:bg-accent/50 transition-colors"
                        onClick={() => setSelectedSessionId(session.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                {getStatusIcon(session.status)}
                                <h3 className="font-semibold">{session.session_name}</h3>
                                <Badge className={getStatusColor(session.status)}>
                                  {session.status}
                                </Badge>
                              </div>
                              <div className="grid grid-cols-5 gap-4 text-sm">
                                <div>
                                  <p className="text-xs text-muted-foreground">Model</p>
                                  <p className="font-medium">{session.model_type}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">mAP50-95</p>
                                  <p className="font-medium">{formatNumber(session.final_map50_95, 3)}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">Precision</p>
                                  <p className="font-medium">{formatNumber(session.final_precision, 3)}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">Recall</p>
                                  <p className="font-medium">{formatNumber(session.final_recall, 3)}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">Duration</p>
                                  <p className="font-medium">{formatDuration(session.duration_seconds)}</p>
                                </div>
                              </div>
                            </div>
                            <Button variant="ghost" size="sm">
                              View Details
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="leaderboard" className="space-y-4">
          <ModelLeaderboard />
        </TabsContent>
      </Tabs>

      {/* Session Details Modal/Sheet */}
      {selectedSessionId && (
        <TrainingSessionDetails
          sessionId={selectedSessionId}
          onClose={() => setSelectedSessionId(null)}
        />
      )}
    </div>
  )
}
