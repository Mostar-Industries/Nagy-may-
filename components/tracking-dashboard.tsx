"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { RefreshCw, AlertTriangle, Activity, Users, Eye } from "lucide-react"
import { useEnhancedTracking } from "@/hooks/use-enhanced-tracking"

export function TrackingDashboard() {
  const { detections, colonies, stats, isLoading, isConnected, lastUpdate, refreshData } = useEnhancedTracking()

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading tracking data...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Real-time Tracking System</CardTitle>
              <CardDescription>
                Enhanced detection monitoring with detailed classification
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={isConnected ? "default" : "destructive"}>
                <Activity className="h-3 w-3 mr-1" />
                {isConnected ? "Connected" : "Disconnected"}
              </Badge>
              <Button size="sm" variant="outline" onClick={refreshData}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        {lastUpdate && (
          <CardContent className="text-xs text-muted-foreground">
            Last update: {new Date(lastUpdate).toLocaleTimeString()}
          </CardContent>
        )}
      </Card>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Detections */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Detections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDetections}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats.activeTracking} actively tracked
            </p>
          </CardContent>
        </Card>

        {/* Active Colonies */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Active Colonies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.coloniesActive}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {colonies.length} total colonies
            </p>
          </CardContent>
        </Card>

        {/* Threat Levels */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-1">
              <AlertTriangle className="h-4 w-4" />
              Threat Levels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-red-600">Critical:</span>
                <span className="font-semibold">{stats.threatLevels.critical}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-orange-600">High:</span>
                <span className="font-semibold">{stats.threatLevels.high}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-yellow-600">Medium:</span>
                <span className="font-semibold">{stats.threatLevels.medium}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detection Types */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Detection Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {Object.entries(stats.detectionTypes).map(([type, count]) => (
                <div key={type} className="flex justify-between text-sm">
                  <span className="capitalize">{type}:</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Species Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Species Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats.speciesBreakdown).map(([species, count]) => (
              <Badge key={species} variant="secondary" className="text-sm">
                {species}: {count}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Gender Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Gender Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(stats.genderDistribution).map(([gender, count]) => (
              <div key={gender} className="text-center">
                <div className="text-2xl mb-1">
                  {gender === 'male' ? '♂' : gender === 'female' ? '♀' : '?'}
                </div>
                <div className="text-lg font-semibold">{count}</div>
                <div className="text-xs text-muted-foreground capitalize">{gender}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Detections */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Recent Detections
          </CardTitle>
        </CardHeader>
        <CardContent>
          {detections.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">No active detections</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {detections.slice(0, 10).map((detection) => (
                <div
                  key={detection.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{detection.species}</span>
                      <Badge variant="outline" className="text-xs">
                        {detection.detection_type}
                      </Badge>
                      {detection.gender !== 'unknown' && (
                        <Badge variant="secondary" className="text-xs">
                          {detection.gender === 'male' ? '♂' : '♀'} {detection.gender}
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(detection.detected_at).toLocaleString()} • 
                      Confidence: {(detection.confidence * 100).toFixed(1)}% •
                      Age: {detection.age_estimate} •
                      Health: {detection.health_status}
                    </div>
                    {detection.colony_name && (
                      <div className="text-xs text-muted-foreground mt-1">
                        <Users className="h-3 w-3 inline mr-1" />
                        Colony: {detection.colony_name}
                      </div>
                    )}
                  </div>
                  <Badge variant={
                    detection.threat_level >= 8 ? "destructive" :
                    detection.threat_level >= 6 ? "default" :
                    detection.threat_level >= 3 ? "secondary" :
                    "outline"
                  }>
                    {detection.threat_level}/10
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Active Colonies */}
      {colonies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Users className="h-5 w-5" />
              Active Colonies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {colonies.map((colony) => (
                <div
                  key={colony.id}
                  className="border rounded-lg p-3 hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold">{colony.colony_name || 'Unnamed Colony'}</h4>
                      <p className="text-sm text-muted-foreground">{colony.species}</p>
                    </div>
                    <Badge variant={
                      colony.threat_level >= 8 ? "destructive" :
                      colony.threat_level >= 6 ? "default" :
                      "secondary"
                    }>
                      {colony.threat_level}/10
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Population:</span>{" "}
                      <span className="font-medium">{colony.estimated_population}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Status:</span>{" "}
                      <Badge variant="outline" className="text-xs ml-1">
                        {colony.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Last activity: {new Date(colony.last_activity).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
