import { type NextRequest, NextResponse } from "next/server"
import { fetchFromSORMAS } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    // Fetch cases from SORMAS
    const cases = await fetchFromSORMAS("/cases")

    await logAuditEvent(user.id, "READ", "sormas_cases", null)

    return NextResponse.json(cases)
  } catch (error) {
    console.error("[v0] SORMAS integration error:", error)
    return NextResponse.json({ error: "Failed to fetch SORMAS data" }, { status: 500 })
  }
}
