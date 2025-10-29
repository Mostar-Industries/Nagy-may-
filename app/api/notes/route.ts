import { neon } from "@neondatabase/serverless"
import { type NextRequest, NextResponse } from "next/server"
import { NoteSchema } from "@/lib/validation"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

const sql = neon(process.env.DATABASE_URL || "")

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    const notes = await sql`
      SELECT * FROM notes
      WHERE owner_id = ${user.id} OR shared = true
      ORDER BY updated_at DESC
    `

    await logAuditEvent(user.id, "READ", "notes", null)

    return NextResponse.json(notes)
  } catch (error) {
    console.error("[v0] GET notes error:", error)
    return NextResponse.json({ error: "Failed to fetch notes" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await requireAuth()
    const body = await request.json()

    const validated = NoteSchema.parse(body)

    const result = await sql`
      INSERT INTO notes (owner_id, title, shared)
      VALUES (${user.id}, ${validated.title}, ${validated.shared})
      RETURNING *
    `

    await logAuditEvent(user.id, "CREATE", "notes", result[0].id, validated)

    return NextResponse.json(result[0], { status: 201 })
  } catch (error) {
    console.error("[v0] POST notes error:", error)
    return NextResponse.json({ error: "Failed to create note" }, { status: 500 })
  }
}
