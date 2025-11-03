import { type NextRequest, NextResponse } from "next/server"

async function callAgentAPI(payload: any) {
  // In production, call the actual MNTRK_Agent_API service
  // For now, use mock responses
  const { query, events, action } = payload

  if (action === "summarize" && events) {
    // Generate a summary of detection events
    const eventCount = events.length
    const species = events[0]?.species || "Mastomys natalensis"
    const avgConfidence = (events.reduce((sum: number, e: any) => sum + (e.confidence || 0), 0) / eventCount).toFixed(2)
    const riskLevels = events.map((e: any) => e.risk_level)
    const criticalCount = riskLevels.filter((r: string) => r === "CRITICAL").length
    const highCount = riskLevels.filter((r: string) => r === "HIGH").length

    return {
      response: `Event Summary: Detected ${eventCount} ${species} specimens across multiple locations. Average model confidence: ${avgConfidence}. Risk breakdown: ${criticalCount} CRITICAL, ${highCount} HIGH, ${eventCount - criticalCount - highCount} MEDIUM or lower. Recommend increased surveillance in high-risk zones.`,
    }
  }

  if (query) {
    // Handle general query about detections
    return {
      response: `Based on the detection data: The system has identified ${events?.length || 0} recent Mastomys detections. Species distribution shows primarily M. natalensis with good detection confidence. Environmental factors suggest suitable habitat conditions. Continued monitoring recommended.`,
    }
  }

  return {
    response: "Unable to process request. Please provide query or events for analysis.",
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const result = await callAgentAPI(body)

    return NextResponse.json(result)
  } catch (error) {
    console.error("[v0] Agent query error:", error)
    return NextResponse.json({ error: "Failed to process agent query" }, { status: 500 })
  }
}
