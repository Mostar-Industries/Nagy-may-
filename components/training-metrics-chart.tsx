"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { useTrainingMetrics } from "@/hooks/use-training-metrics"

interface TrainingMetricsChartProps {
  sessionId: string
}

export function TrainingMetricsChart({ sessionId }: TrainingMetricsChartProps) {
  const { metrics, isLoading } = useTrainingMetrics(sessionId)

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-muted-foreground">Loading metrics...</p>
        </CardContent>
      </Card>
    )
  }

  if (metrics.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-muted-foreground">No metrics data available</p>
        </CardContent>
      </Card>
    )
  }

  const chartData = metrics.map(m => ({
    epoch: m.epoch,
    loss: m.total_loss,
    map50: m.map50,
    map50_95: m.map50_95,
    precision: m.precision,
    recall: m.recall,
  }))

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Training Loss</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="epoch" label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Loss', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="loss" stroke="#8884d8" name="Total Loss" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>mAP Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="epoch" label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'mAP', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="map50" stroke="#82ca9d" name="mAP50" />
              <Line type="monotone" dataKey="map50_95" stroke="#ffc658" name="mAP50-95" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Precision & Recall</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="epoch" label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="precision" stroke="#ff7c7c" name="Precision" />
              <Line type="monotone" dataKey="recall" stroke="#7c7cff" name="Recall" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
