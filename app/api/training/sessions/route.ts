import { NextRequest, NextResponse } from "next/server"
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const status = searchParams.get("status")
    const limit = parseInt(searchParams.get("limit") || "50")

    let query = `
      SELECT 
        id,
        session_name,
        model_type,
        dataset_name,
        epochs,
        batch_size,
        learning_rate,
        status,
        started_at,
        completed_at,
        duration_seconds,
        best_epoch,
        final_map50,
        final_map50_95,
        final_precision,
        final_recall,
        final_loss,
        model_path,
        config,
        created_at,
        updated_at
      FROM training_sessions
    `

    const params: any[] = []
    if (status) {
      query += ` WHERE status = $1`
      params.push(status)
    }

    query += ` ORDER BY created_at DESC LIMIT $${params.length + 1}`
    params.push(limit)

    const sessions = await sql.query(query, params)

    return NextResponse.json({
      success: true,
      sessions,
      count: sessions.length,
    })
  } catch (error) {
    console.error("Error fetching training sessions:", error)
    return NextResponse.json(
      { success: false, error: "Failed to fetch training sessions" },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      session_name,
      model_type,
      dataset_name,
      dataset_size,
      epochs,
      batch_size,
      learning_rate,
      img_size = 640,
      config = {},
      hardware_info = {},
      created_by,
    } = body

    // Validate required fields
    if (!session_name || !model_type || !epochs || !batch_size) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required fields: session_name, model_type, epochs, batch_size",
        },
        { status: 400 }
      )
    }

    const result = await sql`
      INSERT INTO training_sessions (
        session_name,
        model_type,
        dataset_name,
        dataset_size,
        epochs,
        batch_size,
        learning_rate,
        img_size,
        status,
        config,
        hardware_info,
        created_by
      ) VALUES (
        ${session_name},
        ${model_type},
        ${dataset_name},
        ${dataset_size},
        ${epochs},
        ${batch_size},
        ${learning_rate},
        ${img_size},
        'pending',
        ${JSON.stringify(config)},
        ${JSON.stringify(hardware_info)},
        ${created_by}
      )
      RETURNING *
    `

    return NextResponse.json({
      success: true,
      session: result[0],
    })
  } catch (error) {
    console.error("Error creating training session:", error)
    return NextResponse.json(
      { success: false, error: "Failed to create training session" },
      { status: 500 }
    )
  }
}
