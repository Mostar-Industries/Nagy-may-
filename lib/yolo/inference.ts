import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'
import { randomUUID } from 'crypto'

export interface YOLODetection {
  id: number
  bbox: {
    x: number
    y: number
    width: number
    height: number
  }
  confidence: number
  class: number
  class_name: string
  species: string
  species_confidence?: number
  processing_time_ms?: number
  // Enhanced attributes
  gender?: string
  age_estimate?: string
  health_status?: string
  threat_level?: number
  behavior_tags?: string[]
  physical_attributes?: {
    size_category: string
    body_length_px: number
    body_height_px: number
    estimated_length_cm: number
    color_profile: any
  }
}

export interface DetectionAnalysis {
  detection_type: 'none' | 'single' | 'pair' | 'group' | 'colony'
  total_count: number
  species_breakdown: Record<string, number>
  gender_distribution: Record<string, number>
  age_distribution: Record<string, number>
  clustering?: {
    cluster_center: { x: number; y: number }
    avg_distance_from_center: number
    max_distance: number
    cluster_density: number
  }
  colony_metrics?: {
    estimated_population: number
    density: number
    spatial_spread: number
    composition: {
      species: Record<string, number>
      gender: Record<string, number>
      age: Record<string, number>
    }
  }
  avg_confidence: number
  max_threat_level: number
}

export interface InferenceResult {
  detections: YOLODetection[]
  analysis?: DetectionAnalysis
  image_id: string
  timestamp: string
  processing_time_ms: number
  image_metadata?: {
    width: number
    height: number
    mode: string
  }
}

/**
 * Run YOLO inference on an image using the Python ML service
 */
export async function runYOLOInference(
  imageBase64: string,
  confThreshold: number = 0.5,
  enhanced: boolean = true
): Promise<InferenceResult> {
  const startTime = Date.now()
  
  try {
    // Decode base64 image
    const base64Data = imageBase64.replace(/^data:image\/\w+;base64,/, '')
    const imageBuffer = Buffer.from(base64Data, 'base64')
    
    // Save to temp file
    const imageId = randomUUID()
    const tempDir = path.join(process.cwd(), 'temp', 'uploads')
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true })
    }
    
    const tempImagePath = path.join(tempDir, `${imageId}.jpg`)
    fs.writeFileSync(tempImagePath, imageBuffer as any)
    
    // Call Python inference service
    const pythonScriptPath = path.join(
      process.cwd(),
      'backend',
      'ml_service',
      'inference_api.py'
    )
    
    const result = await callPythonInference(pythonScriptPath, tempImagePath, confThreshold, enhanced)
    
    // Clean up temp file
    try {
      fs.unlinkSync(tempImagePath)
    } catch (err) {
      console.warn('[YOLO] Failed to delete temp file:', err)
    }
    
    const processingTime = Date.now() - startTime
    
    return {
      detections: result.detections || [],
      analysis: result.analysis,
      image_id: imageId,
      timestamp: new Date().toISOString(),
      processing_time_ms: processingTime,
      image_metadata: result.image_metadata,
    }
  } catch (error) {
    console.error('[YOLO] Inference error:', error)
    throw new Error(`YOLO inference failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

/**
 * Call Python inference script via child process
 */
function callPythonInference(
  scriptPath: string,
  imagePath: string,
  confThreshold: number,
  enhanced: boolean
): Promise<{ detections: YOLODetection[]; analysis?: DetectionAnalysis; image_metadata?: any }> {
  return new Promise((resolve, reject) => {
    const args = [
      scriptPath,
      '--image', imagePath,
      '--conf', confThreshold.toString(),
      '--output', 'json'
    ]
    
    if (enhanced) {
      args.push('--enhanced')
    }
    
    const pythonProcess = spawn('python', args)
    
    let stdout = ''
    let stderr = ''
    
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })
    
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`))
        return
      }
      
      try {
        const result = JSON.parse(stdout)
        resolve(result)
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${error}`))
      }
    })
    
    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to spawn Python process: ${error.message}`))
    })
  })
}

/**
 * Alternative: Direct TypeScript inference using ONNX
 * (Optional if you want to avoid Python dependency)
 */
export async function runONNXInference(
  imageBase64: string,
  modelPath: string = 'models/mastomys.onnx'
): Promise<InferenceResult> {
  // TODO: Implement ONNX runtime inference if needed
  // This would use @microsoft/onnxruntime-node
  throw new Error('ONNX inference not yet implemented. Use Python inference.')
}
