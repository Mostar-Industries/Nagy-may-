import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

const ML_SERVICE_URL = process.env.YOLO_API_URL || "http://localhost:5001"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") ?? formData.get("image")

    if (!(file instanceof File)) {
      return NextResponse.json({ error: "Missing image file" }, { status: 400 })
    }

    const latitudeRaw = formData.get("latitude")
    const longitudeRaw = formData.get("longitude")
    const latitude = latitudeRaw ? Number(latitudeRaw) : null
    const longitude = longitudeRaw ? Number(longitudeRaw) : null

    if (latitudeRaw && Number.isNaN(latitude)) {
      return NextResponse.json({ error: "Invalid latitude" }, { status: 400 })
    }

    if (longitudeRaw && Number.isNaN(longitude)) {
      return NextResponse.json({ error: "Invalid longitude" }, { status: 400 })
    }

    const mlFormData = new FormData()
    mlFormData.append("file", file, file.name)

    const confidence = formData.get("confidence")
    if (confidence) {
      mlFormData.append("confidence", confidence.toString())
    }

    const mlResponse = await fetch(`${ML_SERVICE_URL}/detect`, {
      method: "POST",
      body: mlFormData,
    })

    if (!mlResponse.ok) {
      const message = await mlResponse.text()
      return NextResponse.json({ error: message || "ML service error" }, { status: 502 })
    }

    const mlData = await mlResponse.json()

    let stored = false
    let insertError: string | null = null

    if (latitude !== null && longitude !== null) {
      const supabase = await createClient()
      const detections = Array.isArray(mlData?.detections) ? mlData.detections : []
      const detectionCount = mlData?.metadata?.detection_count ?? detections.length
      const avgConfidence =
        detections.length > 0
          ? detections.reduce((sum: number, d: any) => sum + (d?.confidence || 0), 0) / detections.length
          : 0

      const { error } = await supabase
        .from("detection_patterns")
        .insert([
          {
            latitude,
            longitude,
            detection_timestamp: new Date().toISOString(),
            detection_count: detectionCount,
            source: "ml_upload",
            environmental_context: { source: "upload" },
            risk_assessment: {
              risk_score: mlData?.risk_score ?? null,
              risk_level: mlData?.risk_level ?? null,
              confidence: avgConfidence,
              detections,
            },
          },
        ])
        .select()

      if (error) {
        insertError = error.message
      } else {
        stored = true
      }
    }

    return NextResponse.json({
      ...mlData,
      stored,
      insert_error: insertError,
    })
  } catch (error) {
    console.error("[v0] Detect proxy error:", error)
    return NextResponse.json({ error: "Detection failed" }, { status: 500 })
  }
}
