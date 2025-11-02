import { type NextRequest, NextResponse } from "next/server"
import { fetchFromCDC, isAPIAvailable } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    if (!isAPIAvailable("CDC")) {
      await logAuditEvent(user.id, "READ", "cdc_outbreaks", null, { status: "unavailable" })
      return NextResponse.json({ error: "CDC API not configured", data: [], available: false }, { status: 503 })
    }

    // Fetch outbreak data from CDC
    const outbreaks = await fetchFromCDC("/outbreaks")

    await logAuditEvent(user.id, "READ", "cdc_outbreaks", null)

    return NextResponse.json({ data: outbreaks, available: true })
  } catch (error) {
    console.error("[v0] CDC integration error:", error)
    return NextResponse.json({ error: "Failed to fetch CDC data", available: false }, { status: 500 })
  }
}
