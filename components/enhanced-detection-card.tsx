"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { DetectionAnalysis, YOLODetection } from "@/lib/yolo/inference"

interface EnhancedDetectionCardProps {
  detections: YOLODetection[]
  analysis?: DetectionAnalysis
  processingTime: number
}

export function EnhancedDetectionCard({ detections, analysis, processingTime }: EnhancedDetectionCardProps) {
  if (detections.length === 0) {
    return (
      <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950">
        <CardContent className="pt-6">
          <p className="text-center text-yellow-700 dark:text-yellow-300">
            No rodents detected in this image
          </p>
        </CardContent>
      </Card>
    )
  }

  const getThreatColor = (level: number) => {
    if (level >= 8) return "destructive"
    if (level >= 6) return "default"
    if (level >= 3) return "secondary"
    return "outline"
  }

  const getDetectionTypeIcon = (type: string) => {
    switch (type) {
      case 'single': return '🐀'
      case 'pair': return '🐀🐀'
      case 'group': return '🐀🐀🐀'
      case 'colony': return '🐀🐀🐀+'
      default: return '🐀'
    }
  }

  return (
    <div className="space-y-4">
      {/* Analysis Summary */}
      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              {getDetectionTypeIcon(analysis.detection_type)}
              Detection Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <p className="text-sm text-muted-foreground">Type</p>
                <p className="font-semibold capitalize">{analysis.detection_type}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Count</p>
                <p className="font-semibold">{analysis.total_count}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg Confidence</p>
                <p className="font-semibold">{(analysis.avg_confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Max Threat</p>
                <Badge variant={getThreatColor(analysis.max_threat_level)}>
                  {analysis.max_threat_level}/10
                </Badge>
              </div>
            </div>

            {/* Species Breakdown */}
            {Object.keys(analysis.species_breakdown).length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">Species Distribution</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(analysis.species_breakdown).map(([species, count]) => (
                    <Badge key={species} variant="secondary">
                      {species}: {count}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Gender Distribution */}
            {Object.keys(analysis.gender_distribution).length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">Gender Distribution</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(analysis.gender_distribution).map(([gender, count]) => (
                    <Badge key={gender} variant="outline">
                      {gender === 'male' ? '♂' : gender === 'female' ? '♀' : '?'} {gender}: {count}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Colony Metrics */}
            {analysis.colony_metrics && (
              <div className="border-t pt-3">
                <p className="text-sm font-semibold mb-2">Colony Information</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Population:</span>{" "}
                    <span className="font-medium">{analysis.colony_metrics.estimated_population}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Density:</span>{" "}
                    <span className="font-medium">{analysis.colony_metrics.density.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Spatial Spread:</span>{" "}
                    <span className="font-medium">{analysis.colony_metrics.spatial_spread.toFixed(1)}px</span>
                  </div>
                </div>
              </div>
            )}

            <div className="text-xs text-muted-foreground">
              Processing time: {processingTime}ms
            </div>
          </CardContent>
        </Card>
      )}

      {/* Individual Detections */}
      <div className="space-y-3">
        {detections.map((detection, idx) => (
          <Card key={idx} className="relative overflow-hidden">
            {/* Threat level indicator */}
            {detection.threat_level && detection.threat_level >= 6 && (
              <div className={`absolute top-0 left-0 right-0 h-1 ${
                detection.threat_level >= 8 ? 'bg-red-500' : 'bg-orange-500'
              }`} />
            )}
            
            <CardContent className="pt-4">
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{detection.species}</h4>
                    <div className="flex flex-wrap gap-2 mt-1">
                      <Badge variant="outline">{(detection.confidence * 100).toFixed(1)}% confident</Badge>
                      {detection.gender && detection.gender !== 'unknown' && (
                        <Badge variant="secondary">
                          {detection.gender === 'male' ? '♂ Male' : '♀ Female'}
                        </Badge>
                      )}
                      {detection.age_estimate && detection.age_estimate !== 'unknown' && (
                        <Badge variant="secondary" className="capitalize">
                          {detection.age_estimate.replace('_', ' ')}
                        </Badge>
                      )}
                    </div>
                  </div>
                  {detection.threat_level !== undefined && (
                    <Badge variant={getThreatColor(detection.threat_level)} className="ml-2">
                      Threat: {detection.threat_level}/10
                    </Badge>
                  )}
                </div>

                {/* Physical Attributes */}
                {detection.physical_attributes && (
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {detection.physical_attributes.size_category && (
                      <div>
                        <span className="text-muted-foreground">Size:</span>{" "}
                        <span className="font-medium capitalize">
                          {detection.physical_attributes.size_category}
                        </span>
                      </div>
                    )}
                    {detection.physical_attributes.estimated_length_cm && (
                      <div>
                        <span className="text-muted-foreground">Est. Length:</span>{" "}
                        <span className="font-medium">
                          {detection.physical_attributes.estimated_length_cm.toFixed(1)} cm
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Health Status */}
                {detection.health_status && detection.health_status !== 'unknown' && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Health:</span>
                    <Badge 
                      variant={detection.health_status === 'healthy' ? 'default' : 'destructive'}
                      className="capitalize"
                    >
                      {detection.health_status}
                    </Badge>
                  </div>
                )}

                {/* Behavior Tags */}
                {detection.behavior_tags && detection.behavior_tags.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Behaviors:</p>
                    <div className="flex flex-wrap gap-1">
                      {detection.behavior_tags.map((tag, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {tag.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Bounding Box */}
                <div className="text-xs text-muted-foreground">
                  Location: ({detection.bbox.x.toFixed(0)}, {detection.bbox.y.toFixed(0)}) 
                  {' '}Size: {detection.bbox.width.toFixed(0)}×{detection.bbox.height.toFixed(0)}px
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
