import { neon } from "@neondatabase/serverless"
import { type NextRequest, NextResponse } from "next/server"
import { DetectionSchema } from "@/lib/validation"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"
import { z } from "zod" // Added import for z
import { createClient } from "@/lib/supabase/server"
import { rateLimit, getRateLimitIdentifier, createRateLimitResponse } from "@/lib/rate-limiter"

const sql = neon(process.env.DATABASE_URL || "")

const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 100, // 100 requests per minute per IP
})

export async function GET(request: NextRequest) {
  const identifier = getRateLimitIdentifier(request)
  const rateLimitResult = limiter(identifier)

  if (!rateLimitResult.success) {
    return createRateLimitResponse(rateLimitResult.resetTime)
  }

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

    const response = NextResponse.json(data)
    response.headers.set("X-RateLimit-Remaining", rateLimitResult.remaining.toString())
    response.headers.set("X-RateLimit-Reset", new Date(rateLimitResult.resetTime).toISOString())
    return response
  } catch (error) {
    console.error("[v0] GET detections error:", error)
    return NextResponse.json({ error: "Failed to fetch detections" }, { status: 500 })
  }
}

const postLimiter = rateLimit({
  windowMs: 60 * 1000,
  maxRequests: 20, // 20 POST requests per minute
})

export async function POST(request: NextRequest) {
  const identifier = getRateLimitIdentifier(request)
  const rateLimitResult = postLimiter(identifier)

  if (!rateLimitResult.success) {
    return createRateLimitResponse(rateLimitResult.resetTime)
  }

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
