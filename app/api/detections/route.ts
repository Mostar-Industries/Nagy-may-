import { neon } from "@neondatabase/serverless"
import { type NextRequest, NextResponse } from "next/server"
import { DetectionSchema } from "@/lib/validation"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"
import { z } from "zod" // Added import for z
import { createClient } from "@/lib/supabase/server"

const sql = neon(process.env.DATABASE_URL || "")

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    const supabase = await createClient()

    const { data, error } = await supabase
      .from("detection_patterns")
      .select("*")
      .order("detection_timestamp", { ascending: false })
      .limit(100)

    if (error) {
      console.error("[v0] Supabase error:", error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    await logAuditEvent(user.id, "READ", "detection_patterns", null)

    return NextResponse.json(data)
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

    const supabase = await createClient()

    const { data, error } = await supabase
      .from("detection_patterns")
      .insert([
        {
          latitude: validated.latitude,
          longitude: validated.longitude,
          detection_count: 1,
          source: "user_submission",
          environmental_context: { type: validated.type },
          risk_assessment: { confidence: validated.confidence },
          detection_timestamp: new Date().toISOString(),
        },
      ])
      .select()

    if (error) {
      console.error("[v0] Supabase insert error:", error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    await logAuditEvent(user.id, "CREATE", "detection_patterns", data?.[0]?.id, validated)

    return NextResponse.json(data?.[0], { status: 201 })
  } catch (error) {
    console.error("[v0] POST detections error:", error)

    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: "Invalid input", details: error.errors }, { status: 400 })
    }

    return NextResponse.json({ error: "Failed to create detection" }, { status: 500 })
  }
}
