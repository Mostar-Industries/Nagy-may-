import { type NextRequest, NextResponse } from "next/server"
import { flightAwareAPI } from "@/lib/flightaware-api"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get("action")
    const lat = searchParams.get("lat")
    const lon = searchParams.get("lon")
    const radius = searchParams.get("radius")
    const airportId = searchParams.get("airportId")
    const flightId = searchParams.get("flightId")

    switch (action) {
      case "nearby-airports":
        if (!lat || !lon) {
          return NextResponse.json({ error: "Missing coordinates" }, { status: 400 })
        }
        const airports = await flightAwareAPI.getNearbyAirports(
          Number.parseFloat(lat),
          Number.parseFloat(lon),
          radius ? Number.parseInt(radius) : 50,
        )
        return NextResponse.json(airports)

      case "airport-flights":
        if (!airportId) {
          return NextResponse.json({ error: "Missing airport ID" }, { status: 400 })
        }
        const flights = await flightAwareAPI.getAirportFlights(airportId, "departures")
        return NextResponse.json(flights)

      case "flight-position":
        if (!flightId) {
          return NextResponse.json({ error: "Missing flight ID" }, { status: 400 })
        }
        const position = await flightAwareAPI.getFlightPosition(flightId)
        return NextResponse.json(position)

      case "flight-track":
        if (!flightId) {
          return NextResponse.json({ error: "Missing flight ID" }, { status: 400 })
        }
        const track = await flightAwareAPI.getFlightTrack(flightId)
        return NextResponse.json(track)

      case "account-usage":
        const usage = await flightAwareAPI.getAccountUsage()
        return NextResponse.json(usage)

      default:
        return NextResponse.json({ error: "Invalid action" }, { status: 400 })
    }
  } catch (error) {
    console.error("FlightAware API error:", error)
    return NextResponse.json({ error: "Failed to fetch flight data" }, { status: 500 })
  }
}
