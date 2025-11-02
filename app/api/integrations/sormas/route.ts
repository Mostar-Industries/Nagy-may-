import { type NextRequest, NextResponse } from "next/server"
import { fetchFromSORMAS, isAPIAvailable } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    if (!isAPIAvailable("SORMAS")) {
      await logAuditEvent(user.id, "READ", "sormas_cases", null, { status: "unavailable" })
      return NextResponse.json({ error: "SORMAS API not configured", data: [], available: false }, { status: 503 })
    }

    // Fetch cases from SORMAS
    const cases = await fetchFromSORMAS("/cases")

    await logAuditEvent(user.id, "READ", "sormas_cases", null)

    return NextResponse.json({ data: cases, available: true })
  } catch (error) {
    console.error("[v0] SORMAS integration error:", error)
    return NextResponse.json({ error: "Failed to fetch SORMAS data", available: false }, { status: 500 })
  }
}
