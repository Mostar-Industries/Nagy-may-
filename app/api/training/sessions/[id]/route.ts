import { NextRequest, NextResponse } from "next/server"
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    // Get session details
    const session = await sql`
      SELECT * FROM training_sessions
      WHERE id = ${id}
    `

    if (session.length === 0) {
      return NextResponse.json(
        { success: false, error: "Training session not found" },
        { status: 404 }
      )
    }

    // Get metrics
    const metrics = await sql`
      SELECT * FROM training_metrics
      WHERE session_id = ${id}
      ORDER BY epoch ASC
    `

    // Get validation results
    const validationResults = await sql`
      SELECT * FROM validation_results
      WHERE session_id = ${id}
      ORDER BY recorded_at DESC
    `

    // Get benchmark if exists
    const benchmarks = await sql`
      SELECT * FROM model_benchmarks
      WHERE session_id = ${id}
      ORDER BY created_at DESC
      LIMIT 1
    `

    return NextResponse.json({
      success: true,
      session: session[0],
      metrics,
      validationResults,
      benchmark: benchmarks[0] || null,
    })
  } catch (error) {
    console.error("Error fetching training session:", error)
    return NextResponse.json(
      { success: false, error: "Failed to fetch training session" },
      { status: 500 }
    )
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const body = await request.json()
    const {
      status,
      started_at,
      completed_at,
      final_map50,
      final_map50_95,
      final_precision,
      final_recall,
      final_loss,
      model_path,
    } = body

    // Build update query dynamically
    const updates: string[] = []
    const values: any[] = []
    let paramIndex = 1

    if (status) {
      updates.push(`status = $${paramIndex++}`)
      values.push(status)
    }
    if (started_at) {
      updates.push(`started_at = $${paramIndex++}`)
      values.push(started_at)
    }
    if (completed_at) {
      updates.push(`completed_at = $${paramIndex++}`)
      values.push(completed_at)
    }
    if (final_map50 !== undefined) {
      updates.push(`final_map50 = $${paramIndex++}`)
      values.push(final_map50)
    }
    if (final_map50_95 !== undefined) {
      updates.push(`final_map50_95 = $${paramIndex++}`)
      values.push(final_map50_95)
    }
    if (final_precision !== undefined) {
      updates.push(`final_precision = $${paramIndex++}`)
      values.push(final_precision)
    }
    if (final_recall !== undefined) {
      updates.push(`final_recall = $${paramIndex++}`)
      values.push(final_recall)
    }
    if (final_loss !== undefined) {
      updates.push(`final_loss = $${paramIndex++}`)
      values.push(final_loss)
    }
    if (model_path) {
      updates.push(`model_path = $${paramIndex++}`)
      values.push(model_path)
    }

    if (updates.length === 0) {
      return NextResponse.json(
        { success: false, error: "No fields to update" },
        { status: 400 }
      )
    }

    values.push(id)
    const query = `
      UPDATE training_sessions 
      SET ${updates.join(", ")}
      WHERE id = $${paramIndex}
      RETURNING *
    `

    // Use raw query method for dynamic SQL
    const result = await sql.query(query, values)

    return NextResponse.json({
      success: true,
      session: result[0],
    })
  } catch (error) {
    console.error("Error updating training session:", error)
    return NextResponse.json(
      { success: false, error: "Failed to update training session" },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    await sql`
      DELETE FROM training_sessions
      WHERE id = ${id}
    `

    return NextResponse.json({
      success: true,
      message: "Training session deleted",
    })
  } catch (error) {
    console.error("Error deleting training session:", error)
    return NextResponse.json(
      { success: false, error: "Failed to delete training session" },
      { status: 500 }
    )
  }
}
