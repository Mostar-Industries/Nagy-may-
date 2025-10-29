import { type NextRequest, NextResponse } from "next/server"
import { fetchFromNPHCDA } from "@/lib/api-integration"
import { requireAuth } from "@/lib/auth"
import { logAuditEvent } from "@/lib/audit"

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth()

    // Fetch facility data from NPHCDA
    const facilities = await fetchFromNPHCDA("/facilities")

    await logAuditEvent(user.id, "READ", "nphcda_facilities", null)

    return NextResponse.json(facilities)
  } catch (error) {
    console.error("[v0] NPHCDA integration error:", error)
    return NextResponse.json({ error: "Failed to fetch NPHCDA data" }, { status: 500 })
  }
}
