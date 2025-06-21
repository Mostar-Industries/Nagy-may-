import { type NextRequest, NextResponse } from "next/server"
import { weatherHabitatService } from "@/lib/weather-habitat-service"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const lat = searchParams.get("lat")
    const lon = searchParams.get("lon")
    const locations = searchParams.get("locations")

    if (lat && lon) {
      // Get data for specific coordinates
      const data = await weatherHabitatService.getLocationHabitatData(Number.parseFloat(lat), Number.parseFloat(lon))
      return NextResponse.json(data)
    } else if (locations === "nigeria") {
      // Get data for Nigerian states
      const data = await weatherHabitatService.getNigerianStatesHabitatData()
      return NextResponse.json(data)
    } else {
      return NextResponse.json({ error: "Missing required parameters" }, { status: 400 })
    }
  } catch (error) {
    console.error("Weather habitat API error:", error)
    return NextResponse.json({ error: "Failed to fetch weather habitat data" }, { status: 500 })
  }
}
