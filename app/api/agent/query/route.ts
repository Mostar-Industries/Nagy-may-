import { type NextRequest, NextResponse } from "next/server"

async function callAgentAPI(payload: any) {
  // Use API_SERVICE_URL (5002) for RAG queries
  const baseUrl = process.env.API_SERVICE_URL || `http://localhost:5002`
  const endpoint = `${baseUrl}/rag-query`

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || "REMOSTAR API error")
  }

  return response.json()
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const result = await callAgentAPI(body)

    return NextResponse.json(result)
  } catch (error) {
    console.error("[v0] Agent query error:", error)
    return NextResponse.json(
      { error: "Failed to process agent query", details: error instanceof Error ? error.message : String(error) },
      { status: 500 },
    )
  }
}
