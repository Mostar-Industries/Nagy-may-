import { NextRequest, NextResponse } from "next/server"
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = parseInt(searchParams.get("limit") || "20")

    // Get top performing models from leaderboard
    const leaderboard = await sql`
      SELECT * FROM models_leaderboard
      LIMIT ${limit}
    `

    return NextResponse.json({
      success: true,
      leaderboard,
      count: leaderboard.length,
    })
  } catch (error) {
    console.error("Error fetching models leaderboard:", error)
    return NextResponse.json(
      { success: false, error: "Failed to fetch models leaderboard" },
      { status: 500 }
    )
  }
}
