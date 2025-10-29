import { neon } from "@neondatabase/serverless"
import { type NextRequest, NextResponse } from "next/server"
import { DetectionSchema } from "@/lib/validation"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"
import { z } from "zod" // Added import for z

const sql = neon(process.env.DATABASE_URL || "")

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    const detections = await sql`
      SELECT * FROM detection_patterns
      ORDER BY detection_timestamp DESC
      LIMIT 100
    `

    await logAuditEvent(user.id, "READ", "detection_patterns", null)

    return NextResponse.json(detections)
  } catch (error) {
    console.error("[v0] GET detections error:", error)
    return NextResponse.json({ error: "Failed to fetch detections" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await requireAuth()
    const body = await request.json()

    const validated = DetectionSchema.parse(body)

    const result = await sql`
      INSERT INTO detection_patterns (
        latitude, longitude, detection_count, source, 
        environmental_context, risk_assessment
      )
      VALUES (
        ${validated.latitude},
        ${validated.longitude},
        1,
        'user_submission',
        ${JSON.stringify({ type: validated.type })},
        ${JSON.stringify({ confidence: validated.confidence })}
      )
      RETURNING *
    `

    await logAuditEvent(user.id, "CREATE", "detection_patterns", result[0].id, validated)

    return NextResponse.json(result[0], { status: 201 })
  } catch (error) {
    console.error("[v0] POST detections error:", error)

    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: "Invalid input", details: error.errors }, { status: 400 })
    }

    return NextResponse.json({ error: "Failed to create detection" }, { status: 500 })
  }
}
