import { neon } from "@neondatabase/serverless"
import { createClient } from "@/lib/supabase/server"
import type { YOLODetection, DetectionAnalysis } from "@/lib/yolo/inference"

const sql = neon(process.env.DATABASE_URL || "")

export interface DetectionPayload {
  image_id: string
  latitude?: number
  longitude?: number
  detections: YOLODetection[]
  analysis?: DetectionAnalysis
  source: string
  confidence: number
  processing_time_ms: number
  metadata?: Record<string, any>
}

/**
 * Save detection to Neon database with retry logic
 */
export async function saveDetectionToNeon(payload: DetectionPayload): Promise<void> {
  const maxRetries = 3
  let lastError: Error | null = null
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // Insert each detection individually with enhanced fields
      for (const det of payload.detections) {
        await sql`
          INSERT INTO detections (
            image_id,
            latitude,
            longitude,
            bbox,
            confidence,
            label,
            species,
            detected_at,
            source,
            processing_time_ms,
            metadata,
            detection_type,
            gender,
            age_estimate,
            health_status,
            threat_level,
            behavior_tags,
            physical_attributes,
            tracking_status,
            last_seen
          ) VALUES (
            ${payload.image_id},
            ${payload.latitude || null},
            ${payload.longitude || null},
            ${JSON.stringify(det.bbox)},
            ${det.confidence},
            ${det.class_name},
            ${det.species},
            ${new Date().toISOString()},
            ${payload.source},
            ${payload.processing_time_ms},
            ${JSON.stringify(payload.metadata || {})},
            ${payload.analysis?.detection_type || 'single'},
            ${det.gender || 'unknown'},
            ${det.age_estimate || 'unknown'},
            ${det.health_status || 'unknown'},
            ${det.threat_level || 0},
            ${JSON.stringify(det.behavior_tags || [])},
            ${JSON.stringify(det.physical_attributes || {})},
            ${'active'},
            ${new Date().toISOString()}
          )
        `
      }
      
      console.log(`[Neon] Saved ${payload.detections.length} detections`)
      return
    } catch (error) {
      lastError = error as Error
      console.warn(`[Neon] Write attempt ${attempt}/${maxRetries} failed:`, error)
      
      if (attempt < maxRetries) {
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000))
      }
    }
  }
  
  throw new Error(`Neon write failed after ${maxRetries} attempts: ${lastError?.message}`)
}

/**
 * Save detection to Supabase for realtime updates
 */
export async function saveDetectionToSupabase(payload: DetectionPayload): Promise<void> {
  try {
    const supabase = await createClient()
    
    // Calculate highest confidence detection
    const topDetection = payload.detections.reduce((prev, current) => 
      (current.confidence > prev.confidence) ? current : prev
    , payload.detections[0])
    
    const { error } = await supabase
      .from('detections')
      .insert({
        image_id: payload.image_id || `detection_${Date.now()}`,
        latitude: payload.latitude || 0,
        longitude: payload.longitude || 0,
        confidence: topDetection.confidence || 0.5,
        label: topDetection.class_name || 'unknown',
        species: topDetection.species || 'Mastomys natalensis',
        source: payload.source || 'ml_inference',
        bbox: topDetection.bbox || {},
        metadata: payload.metadata || {},
        processing_time_ms: payload.processing_time_ms
      })
    
    if (error) {
      console.warn('[Supabase] Write failed:', error.message)
      throw error
    }
    
    console.log(`[Supabase] Detection saved successfully`)
  } catch (error) {
    console.error('[Supabase] Failed to save detection:', error)
    // Don't throw - Supabase is optional/fallback
  }
}

/**
 * Save detection to both databases with fallback logic
 */
export async function saveDetection(payload: DetectionPayload): Promise<{
  neon: boolean
  supabase: boolean
}> {
  const results = {
    neon: false,
    supabase: false
  }
  
  // Try Neon first (primary)
  try {
    await saveDetectionToNeon(payload)
    results.neon = true
  } catch (error) {
    console.error('[Detection] Neon save failed:', error)
  }
  
  // Always try Supabase (for realtime)
  try {
    await saveDetectionToSupabase(payload)
    results.supabase = true
  } catch (error) {
    console.error('[Detection] Supabase save failed:', error)
  }
  
  if (!results.neon && !results.supabase) {
    throw new Error('Failed to save detection to any database')
  }
  
  return results
}
