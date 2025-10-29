import "server-only"
import { NextResponse } from "next/server"

export async function GET() {
  const token = process.env.CESIUM_ION_TOKEN

  if (!token) {
    return NextResponse.json({ error: "Cesium token not configured" }, { status: 500 })
  }

  return NextResponse.json({ token })
}
