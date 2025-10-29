import { type NextRequest, NextResponse } from "next/server"
import { fetchFromWHOAFRO } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    // Fetch data from WHO AFRO
    const data = await fetchFromWHOAFRO("/data")

    await logAuditEvent(user.id, "READ", "who_data", null)

    return NextResponse.json(data)
  } catch (error) {
    console.error("[v0] WHO AFRO integration error:", error)
    return NextResponse.json({ error: "Failed to fetch WHO AFRO data" }, { status: 500 })
  }
}
