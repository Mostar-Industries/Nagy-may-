import { type NextRequest, NextResponse } from "next/server"
import { fetchFromCDC } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    // Fetch outbreak data from CDC
    const outbreaks = await fetchFromCDC("/outbreaks")

    await logAuditEvent(user.id, "READ", "cdc_outbreaks", null)

    return NextResponse.json(outbreaks)
  } catch (error) {
    console.error("[v0] CDC integration error:", error)
    return NextResponse.json({ error: "Failed to fetch CDC data" }, { status: 500 })
  }
}
