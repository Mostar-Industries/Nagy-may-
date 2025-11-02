import { type NextRequest, NextResponse } from "next/server"
import { fetchFromNPHCDA, isAPIAvailable } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    if (!isAPIAvailable("NPHCDA")) {
      await logAuditEvent(user.id, "READ", "nphcda_facilities", null, { status: "unavailable" })
      return NextResponse.json({ error: "NPHCDA API not configured", data: [], available: false }, { status: 503 })
    }

    // Fetch facility data from NPHCDA
    const facilities = await fetchFromNPHCDA("/facilities")

    await logAuditEvent(user.id, "READ", "nphcda_facilities", null)

    return NextResponse.json({ data: facilities, available: true })
  } catch (error) {
    console.error("[v0] NPHCDA integration error:", error)
    return NextResponse.json({ error: "Failed to fetch NPHCDA data", available: false }, { status: 500 })
  }
}
