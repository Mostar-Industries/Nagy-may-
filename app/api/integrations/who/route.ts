import { type NextRequest, NextResponse } from "next/server"
import { fetchFromWHOAFRO, isAPIAvailable } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    if (!isAPIAvailable("WHO_AFRO")) {
      await logAuditEvent(user.id, "READ", "who_data", null, { status: "unavailable" })
      return NextResponse.json({ error: "WHO AFRO API not configured", data: [], available: false }, { status: 503 })
    }

    // Fetch data from WHO AFRO
    const data = await fetchFromWHOAFRO("/data")

    await logAuditEvent(user.id, "READ", "who_data", null)

    return NextResponse.json({ data, available: true })
  } catch (error) {
    console.error("[v0] WHO AFRO integration error:", error)
    return NextResponse.json({ error: "Failed to fetch WHO AFRO data", available: false }, { status: 500 })
  }
}
