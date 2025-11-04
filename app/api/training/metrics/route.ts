import { NextRequest, NextResponse } from "next/server"
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      session_id,
      epoch,
      box_loss,
      cls_loss,
      dfl_loss,
      total_loss,
      precision,
      recall,
      map50,
      map50_95,
      learning_rate,
      epoch_time_seconds,
      gpu_memory_mb,
    } = body

    // Validate required fields
    if (!session_id || epoch === undefined) {
      return NextResponse.json(
        { success: false, error: "Missing required fields: session_id, epoch" },
        { status: 400 }
      )
    }

    const result = await sql`
      INSERT INTO training_metrics (
        session_id,
        epoch,
        box_loss,
        cls_loss,
        dfl_loss,
        total_loss,
        precision,
        recall,
        map50,
        map50_95,
        learning_rate,
        epoch_time_seconds,
        gpu_memory_mb
      ) VALUES (
        ${session_id},
        ${epoch},
        ${box_loss},
        ${cls_loss},
        ${dfl_loss},
        ${total_loss},
        ${precision},
        ${recall},
        ${map50},
        ${map50_95},
        ${learning_rate},
        ${epoch_time_seconds},
        ${gpu_memory_mb}
      )
      ON CONFLICT (session_id, epoch)
      DO UPDATE SET
        box_loss = EXCLUDED.box_loss,
        cls_loss = EXCLUDED.cls_loss,
        dfl_loss = EXCLUDED.dfl_loss,
        total_loss = EXCLUDED.total_loss,
        precision = EXCLUDED.precision,
        recall = EXCLUDED.recall,
        map50 = EXCLUDED.map50,
        map50_95 = EXCLUDED.map50_95,
        learning_rate = EXCLUDED.learning_rate,
        epoch_time_seconds = EXCLUDED.epoch_time_seconds,
        gpu_memory_mb = EXCLUDED.gpu_memory_mb,
        recorded_at = NOW()
      RETURNING *
    `

    return NextResponse.json({
      success: true,
      metric: result[0],
    })
  } catch (error) {
    console.error("Error recording training metric:", error)
    return NextResponse.json(
      { success: false, error: "Failed to record training metric" },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const session_id = searchParams.get("session_id")

    if (!session_id) {
      return NextResponse.json(
        { success: false, error: "session_id parameter required" },
        { status: 400 }
      )
    }

    const metrics = await sql`
      SELECT * FROM training_metrics
      WHERE session_id = ${session_id}
      ORDER BY epoch ASC
    `

    return NextResponse.json({
      success: true,
      metrics,
      count: metrics.length,
    })
  } catch (error) {
    console.error("Error fetching training metrics:", error)
    return NextResponse.json(
      { success: false, error: "Failed to fetch training metrics" },
      { status: 500 }
    )
  }
}
