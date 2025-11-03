import { type NextRequest, NextResponse } from "next/server"
import { runYOLOInference } from "@/lib/yolo/inference"
import { saveDetection } from "@/lib/db/detection-writer"
import { z } from "zod"

// Increased body size limit for images
export const maxDuration = 60 // 60 seconds timeout
export const dynamic = 'force-dynamic'

const InferenceRequestSchema = z.object({
  imageBase64: z.string().min(1, "Image data required"),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  source: z.string().default("web_upload"),
  confThreshold: z.number().min(0).max(1).default(0.5),
  metadata: z.record(z.any()).optional(),
})

/**
 * POST /api/detections/inference
 * Upload an image and run YOLO inference
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate request
    const validated = InferenceRequestSchema.parse(body)
    
    console.log('[Inference] Starting YOLO inference...')
    
    // Run YOLO inference
    const inferenceResult = await runYOLOInference(
      validated.imageBase64,
      validated.confThreshold
    )
    
    if (inferenceResult.detections.length === 0) {
      return NextResponse.json(
        {
          success: true,
          message: "No detections found",
          result: inferenceResult,
        },
        { status: 200 }
      )
    }
    
    console.log(`[Inference] Found ${inferenceResult.detections.length} detections`)
    
    // Calculate highest confidence
    const maxConfidence = Math.max(...inferenceResult.detections.map(d => d.confidence))
    
    // Save to databases
    const saveResult = await saveDetection({
      image_id: inferenceResult.image_id,
      latitude: validated.latitude,
      longitude: validated.longitude,
      detections: inferenceResult.detections,
      analysis: inferenceResult.analysis,
      source: validated.source,
      confidence: maxConfidence,
      processing_time_ms: inferenceResult.processing_time_ms,
      metadata: validated.metadata,
    })
    
    console.log('[Inference] Save results:', saveResult)
    
    return NextResponse.json(
      {
        success: true,
        detection: {
          image_id: inferenceResult.image_id,
          timestamp: inferenceResult.timestamp,
          detections: inferenceResult.detections,
          analysis: inferenceResult.analysis,
          processing_time_ms: inferenceResult.processing_time_ms,
          saved_to: saveResult,
        },
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('[Inference] Error:', error)
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: "Invalid request format",
          details: error.errors,
        },
        { status: 400 }
      )
    }
    
    return NextResponse.json(
      {
        error: "Inference failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    )
  }
}
