import { NextRequest, NextResponse } from "next/server"
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function GET(request: NextRequest) {
  try {
    // Get active training sessions with latest metrics
    const activeSessions = await sql`
      SELECT * FROM active_training_sessions
      ORDER BY started_at DESC
    `

    return NextResponse.json({
      success: true,
      activeSessions,
      count: activeSessions.length,
    })
  } catch (error) {
    console.error("Error fetching active training sessions:", error)
    return NextResponse.json(
      { success: false, error: "Failed to fetch active training sessions" },
      { status: 500 }
    )
  }
}
