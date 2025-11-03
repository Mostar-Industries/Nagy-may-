"use client"

import { useEffect, useRef, useState } from "react"
import Script from "next/script"
import { useRealtimeDetections } from "@/hooks/use-realtime-detections"
import { useDetectionMapData } from "@/hooks/use-detection-map-data"

declare global {
  interface Window {
    Cesium: any
  }
}

export default function CesiumMap() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const viewerInstanceRef = useRef<any>(null)
  const entitiesRef = useRef<Map<number, any>>(new Map())

  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [cesiumLoaded, setCesiumLoaded] = useState(false)

  const { detections, isLoading: detLoading, isConnected, error: detError } = useRealtimeDetections()
  const mapMarkers = useDetectionMapData(detections)

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

      // Center map on Nigeria with zoomed out view
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(8.6753, 9.0820, 2500000), // Lng, Lat, Altitude (2.5M meters for country view)
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-90), // Looking straight down
          roll: 0.0
        }
      })

      viewerInstanceRef.current = viewer
      setIsLoading(false)
    } catch (err) {
      console.error("Cesium initialization error:", err)
      setError(err instanceof Error ? err.message : String(err))
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!cesiumLoaded) {
      initCesium()
      return
    }
  }, [cesiumLoaded])

  useEffect(() => {
    if (!viewerInstanceRef.current || mapMarkers.length === 0) return

    const Cesium = window.Cesium
    const viewer = viewerInstanceRef.current

    // Add new markers or update existing ones
    mapMarkers.forEach((marker) => {
      // Skip if already on map
      if (entitiesRef.current.has(marker.id)) {
        return
      }

      const pointColor = Cesium.Color.fromCssColorString(marker.color)

      const entity = viewer.entities.add({
        id: marker.id.toString(),
        name: marker.title,
        position: Cesium.Cartesian3.fromDegrees(marker.longitude, marker.latitude, 100),
        point: {
          pixelSize: 12,
          color: pointColor,
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2,
        },
        label: {
          text: marker.title,
          font: "12pt sans-serif",
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          fillColor: Cesium.Color.WHITE,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 1,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          pixelOffset: new Cesium.Cartesian2(0, -15),
          showBackground: true,
          backgroundColor: Cesium.Color.BLACK.withAlpha(0.7),
          backgroundPadding: new Cesium.Cartesian2(8, 4),
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
        description: `
          <div style="font-family: sans-serif; color: #333; padding: 10px;">
            <h3 style="margin-bottom: 5px; color: ${marker.color};">${marker.title}</h3>
            <p><strong>Risk Level:</strong> ${marker.riskLevel.toUpperCase()}</p>
            <p><strong>Confidence:</strong> ${(marker.confidence * 100).toFixed(1)}%</p>
            <p><strong>Location:</strong> (${marker.latitude.toFixed(4)}°N, ${marker.longitude.toFixed(4)}°E)</p>
            <p><strong>Time:</strong> ${new Date(marker.timestamp).toLocaleString()}</p>
            <p><strong>Source:</strong> ${marker.source}</p>
          </div>
        `,
      })

      entitiesRef.current.set(marker.id, entity)
      console.log("[v0] Added marker to map:", marker.id)
    })

    // Fit all markers in view if data just loaded
    if (mapMarkers.length > 0 && entitiesRef.current.size <= mapMarkers.length) {
      viewer.zoomTo(viewer.entities)
    }
  }, [mapMarkers])

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
        {(isLoading || detLoading) && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900 z-10">
            <div className="w-10 h-10 border-4 border-gray-700 border-t-white rounded-full animate-spin" />
            <span className="text-white mt-3 text-sm">Loading map...</span>
            {isConnected && <span className="text-green-400 text-xs mt-1">Realtime connected</span>}
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

        {detError && (
          <div className="absolute top-4 right-4 bg-yellow-900 text-yellow-100 px-4 py-2 rounded-md text-sm z-20">
            Data sync warning: {detError}
          </div>
        )}

        <div ref={viewerRef} className="w-full h-full" />

        {/* Status indicator */}
        <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 text-white px-3 py-2 rounded-md text-xs z-20">
          <div>Detections: {mapMarkers.length}</div>
          <div className={`mt-1 ${isConnected ? "text-green-400" : "text-yellow-400"}`}>
            {isConnected ? "● Live" : "○ Connecting..."}
          </div>
        </div>
      </div>
    </>
  )
}
