"use client"

import { useEffect, useRef, useState } from "react"
import Script from "next/script"

const hardcodedDetections = [
  {
    id: "mn-001",
    name: "Mastomys Edo State",
    latitude: 6.335,
    longitude: 5.6037,
    altitude: 200,
    description: "Detection point in Edo State - Lassa fever endemic region.",
    confidence: 0.92,
    type: "confirmed",
  },
  {
    id: "mn-002",
    name: "Mastomys Bauchi State",
    latitude: 10.3158,
    longitude: 9.8442,
    altitude: 609,
    description: "Detection point in Bauchi State - Northern Nigeria surveillance.",
    confidence: 0.88,
    type: "confirmed",
  },
  {
    id: "mn-003",
    name: "Mastomys Ondo State",
    latitude: 7.2526,
    longitude: 5.1931,
    altitude: 164,
    description: "Detection point in Ondo State - Southwest Nigeria monitoring.",
    confidence: 0.85,
    type: "suspected",
  },
  {
    id: "mn-004",
    name: "Mastomys Plateau State",
    latitude: 9.2182,
    longitude: 9.5179,
    altitude: 1200,
    description: "Detection point in Plateau State - Central Nigeria highlands.",
    confidence: 0.9,
    type: "confirmed",
  },
  {
    id: "mn-005",
    name: "Mastomys Taraba State",
    latitude: 7.8706,
    longitude: 10.0753,
    altitude: 318,
    description: "Detection point in Taraba State - Eastern Nigeria border region.",
    confidence: 0.87,
    type: "confirmed",
  },
]

declare global {
  interface Window {
    Cesium: any
  }
}

export default function CesiumMap() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [cesiumLoaded, setCesiumLoaded] = useState(false)

  const initCesium = async () => {
    if (!window.Cesium || !viewerRef.current) return

    try {
      const Cesium = window.Cesium

      const tokenResponse = await fetch("/api/cesium-token")
      if (!tokenResponse.ok) {
        throw new Error("Failed to fetch Cesium token")
      }
      const { token } = await tokenResponse.json()

      Cesium.Ion.defaultAccessToken = token

      const terrainProvider = await Cesium.createWorldTerrainAsync()

      const viewer = new Cesium.Viewer(viewerRef.current, {
        terrainProvider: terrainProvider,
        animation: true,
        timeline: true,
        fullscreenButton: true,
        baseLayerPicker: true,
        geocoder: true,
        homeButton: true,
        infoBox: true,
        navigationHelpButton: true,
      })

      hardcodedDetections.forEach((detection) => {
        const pointColor = detection.type === "confirmed" ? Cesium.Color.ORANGERED : Cesium.Color.YELLOW

        viewer.entities.add({
          id: detection.id,
          name: detection.name,
          position: Cesium.Cartesian3.fromDegrees(detection.longitude, detection.latitude, detection.altitude),
          point: {
            pixelSize: 12,
            color: pointColor,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
          },
          label: {
            text: detection.name,
            font: "14pt sans-serif",
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -15),
            showBackground: true,
            backgroundColor: Cesium.Color.BLACK.withAlpha(0.7),
            backgroundPadding: new Cesium.Cartesian2(8, 4),
            disableDepthTestDistance: Number.POSITIVE_INFINITY,
          },
          description: `
            <div style="font-family: sans-serif; color: #333; padding: 10px;">
              <h3 style="margin-bottom: 5px; color: ${detection.type === "confirmed" ? "#d9534f" : "#f0ad4e"};">${detection.name}</h3>
              <p><strong>ID:</strong> ${detection.id}</p>
              <p><strong>Type:</strong> ${detection.type === "confirmed" ? "✓ Confirmed" : "⚠ Suspected"}</p>
              <p><strong>Confidence:</strong> ${(detection.confidence * 100).toFixed(1)}%</p>
              <p><strong>Coordinates:</strong> (${detection.latitude.toFixed(4)}°N, ${detection.longitude.toFixed(4)}°E)</p>
              <p><strong>Altitude:</strong> ${detection.altitude}m</p>
              <p><strong>Notes:</strong> ${detection.description || "N/A"}</p>
            </div>
          `,
        })
      })

      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(8.6753, 9.082, 2000000),
        orientation: {
          heading: Cesium.Math.toRadians(0.0),
          pitch: Cesium.Math.toRadians(-45.0),
          roll: Cesium.Math.toRadians(0.0),
        },
        duration: 2.0,
      })

      setIsLoading(false)
    } catch (err) {
      console.error("Cesium initialization error:", err)
      setError(err instanceof Error ? err.message : String(err))
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (cesiumLoaded) {
      initCesium()
    }
  }, [cesiumLoaded])

  return (
    <>
      <Script
        src="https://cesium.com/downloads/cesiumjs/releases/1.134/Build/Cesium/Cesium.js"
        strategy="afterInteractive"
        onLoad={() => setCesiumLoaded(true)}
        onError={(e) => {
          console.error("Failed to load Cesium:", e)
          setError("Failed to load Cesium library from CDN")
          setIsLoading(false)
        }}
      />

      <div className="relative w-full h-96 rounded-md overflow-hidden bg-gray-900">
        {isLoading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900 z-10">
            <div className="w-10 h-10 border-4 border-gray-700 border-t-white rounded-full animate-spin" />
            <span className="text-white mt-3 text-sm">Loading map...</span>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900 z-10">
            <p className="text-red-400 text-center px-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md text-sm hover:bg-indigo-700"
            >
              Retry
            </button>
          </div>
        )}

        <div ref={viewerRef} className="w-full h-full" />
      </div>
    </>
  )
}
