"use client"

import { useState, useCallback } from "react"
import { Upload, Loader2, CheckCircle2, XCircle, Camera } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import type { YOLODetection, DetectionAnalysis } from "@/lib/yolo/inference"
import { EnhancedDetectionCard } from "./enhanced-detection-card"

interface DetectionResult {
  image_id: string
  timestamp: string
  detections: YOLODetection[]
  analysis?: DetectionAnalysis
  processing_time_ms: number
  saved_to: {
    neon: boolean
    supabase: boolean
  }
}

export function DetectionUploader() {
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState<DetectionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const { toast } = useToast()

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be less than 10MB')
      return
    }

    setIsUploading(true)
    setError(null)
    setResult(null)

    try {
      // Create preview
      const objectUrl = URL.createObjectURL(file)
      setPreviewUrl(objectUrl)

      // Convert to base64
      const base64 = await fileToBase64(file)

      // Get geolocation if available
      const coords = await getGeolocation()

      // Upload for inference
      const response = await fetch('/api/detections/inference', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imageBase64: base64,
          latitude: coords?.latitude,
          longitude: coords?.longitude,
          source: 'web_upload',
          confThreshold: 0.5,
          metadata: {
            filename: file.name,
            size: file.size,
            type: file.type,
          },
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Upload failed')
      }

      const data = await response.json()
      setResult(data.detection)

      // Show success toast
      toast({
        title: "Detection Complete",
        description: `Found ${data.detection.detections.length} detection(s) in ${data.detection.processing_time_ms}ms`,
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setError(errorMessage)
      toast({
        title: "Detection Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }, [toast])

  const handleCameraCapture = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      const video = document.createElement('video')
      video.srcObject = stream
      video.play()

      // Wait for video to be ready
      await new Promise((resolve) => {
        video.onloadedmetadata = resolve
      })

      // Capture frame
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(video, 0, 0)

      // Stop stream
      stream.getTracks().forEach(track => track.stop())

      // Convert to blob and trigger upload
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          const input = document.querySelector('input[type="file"]') as HTMLInputElement
          if (input) {
            input.files = dataTransfer.files
            input.dispatchEvent(new Event('change', { bubbles: true }))
          }
        }
      }, 'image/jpeg', 0.9)
    } catch (err) {
      toast({
        title: "Camera Error",
        description: err instanceof Error ? err.message : 'Failed to access camera',
        variant: "destructive",
      })
    }
  }, [toast])

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Upload Image for Detection</CardTitle>
        <CardDescription>
          Upload an image to detect Mastomys rodents using AI
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Upload Button */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="flex-1"
            disabled={isUploading}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Select Image
              </>
            )}
          </Button>
          
          <Button
            variant="outline"
            onClick={handleCameraCapture}
            disabled={isUploading}
          >
            <Camera className="h-4 w-4" />
          </Button>
        </div>

        <input
          id="file-input"
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileSelect}
          disabled={isUploading}
        />

        {/* Preview */}
        {previewUrl && (
          <div className="border rounded-lg overflow-hidden">
            <img
              src={previewUrl}
              alt="Preview"
              className="w-full h-auto"
            />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 text-red-600 text-sm">
            <XCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-4 w-4" />
              <span className="font-medium">
                Detection Complete ({result.processing_time_ms}ms)
              </span>
            </div>

            <EnhancedDetectionCard
              detections={result.detections}
              analysis={result.analysis}
              processingTime={result.processing_time_ms}
            />

            <div className="text-xs text-muted-foreground text-center">
              Saved to: Neon {result.saved_to.neon ? "✓" : "✗"}, Supabase{" "}
              {result.saved_to.supabase ? "✓" : "✗"}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Helper functions
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

function getGeolocation(): Promise<GeolocationCoordinates | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null)
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => resolve(position.coords),
      () => resolve(null),
      { timeout: 5000 }
    )
  })
}
