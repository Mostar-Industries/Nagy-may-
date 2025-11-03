export interface RTSPStream {
  id: string
  name: string
  url: string
  enabled: boolean
  location: {
    lat: number
    lon: number
    name: string
  }
  region: string
  type: "wildlife" | "urban" | "lab" | "custom"
  icon?: string
}

export const DEFAULT_STREAMS: RTSPStream[] = [
  {
    id: "wildlife_kenya",
    name: "Wildlife Kenya Live",
    url: "rtsp://stream.example.com/wildlife_kenya",
    enabled: true,
    location: {
      lat: -1.286389,
      lon: 36.817223,
      name: "Kenya - East Africa",
    },
    region: "Kenya",
    type: "wildlife",
  },
  {
    id: "lagos_traffic",
    name: "Lagos Traffic Camera",
    url: "rtsp://stream.example.com/lagos_traffic",
    enabled: true,
    location: {
      lat: 6.5244,
      lon: 3.3792,
      name: "Lagos, Nigeria",
    },
    region: "Nigeria",
    type: "urban",
  },
  {
    id: "ibadan_lab",
    name: "Ibadan Botany Lab Feed",
    url: "rtsp://stream.example.com/ibadan_lab",
    enabled: true,
    location: {
      lat: 7.3775,
      lon: 3.947,
      name: "Ibadan, Nigeria",
    },
    region: "Nigeria",
    type: "lab",
  },
]

export function getStreams(): RTSPStream[] {
  if (typeof window === "undefined") return DEFAULT_STREAMS

  try {
    const stored = localStorage.getItem("rtsp_streams")
    if (stored) {
      const parsed = JSON.parse(stored) as RTSPStream[]
      return [...DEFAULT_STREAMS, ...parsed]
    }
  } catch (e) {
    console.error("[v0] Failed to load streams from localStorage:", e)
  }

  return DEFAULT_STREAMS
}

export function saveStream(stream: RTSPStream): void {
  if (typeof window === "undefined") return

  try {
    const streams = getStreams().filter((s) => !DEFAULT_STREAMS.find((d) => d.id === s.id))
    const updated = [...streams, stream]
    localStorage.setItem("rtsp_streams", JSON.stringify(updated))
  } catch (e) {
    console.error("[v0] Failed to save stream:", e)
  }
}

export function deleteStream(id: string): void {
  if (typeof window === "undefined") return

  try {
    const streams = getStreams().filter((s) => s.id !== id)
    localStorage.setItem("rtsp_streams", JSON.stringify(streams))
  } catch (e) {
    console.error("[v0] Failed to delete stream:", e)
  }
}

export function updateStreamStatus(id: string, enabled: boolean): void {
  if (typeof window === "undefined") return

  try {
    const streams = getStreams()
    const updated = streams.map((s) => (s.id === id ? { ...s, enabled } : s))
    localStorage.setItem("rtsp_streams", JSON.stringify(updated))
  } catch (e) {
    console.error("[v0] Failed to update stream status:", e)
  }
}
