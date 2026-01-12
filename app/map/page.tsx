"use client"
import { useEffect, useRef, useState } from "react"
import Script from "next/script"
import Link from "next/link"
import { useRealtimeDetections } from "@/hooks/use-realtime-detections"

declare global {
  interface Window {
    Cesium: any
  }
}

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

export default function MapPage() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const viewerInstanceRef = useRef<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [cesiumLoaded, setCesiumLoaded] = useState(false)

  const [verticalExaggeration, setVerticalExaggeration] = useState(3.0)
  const [relativeHeight, setRelativeHeight] = useState(0)
  const [showControls, setShowControls] = useState(false)

  const { detections, isLoading: detectionsLoading } = useRealtimeDetections()

  useEffect(() => {
    if (viewerInstanceRef.current) {
      const scene = viewerInstanceRef.current.scene
      scene.verticalExaggeration = verticalExaggeration
      scene.verticalExaggerationRelativeHeight = relativeHeight
    }
  }, [verticalExaggeration, relativeHeight])

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

      const terrainProvider = await Cesium.Terrain.fromWorldTerrain({
        requestWaterMask: true,
        requestVertexNormals: true,
      })

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
        skyAtmosphere: new Cesium.SkyAtmosphere(),
      })

      viewer.scene.verticalExaggeration = verticalExaggeration
      viewer.scene.verticalExaggerationRelativeHeight = relativeHeight

      viewer.scene.globe.enableLighting = true
      viewer.clock.currentTime = Cesium.JulianDate.fromIso8601("2024-01-15T12:00:00Z")

      try {
        const tileset = await Cesium.Cesium3DTileset.fromIonAssetId(2275207)
        viewer.scene.primitives.add(tileset)
        console.log("[v0] Google Photorealistic 3D Tiles loaded successfully")
      } catch (tilesetError) {
        console.log("[v0] 3D Tiles unavailable, continuing with standard terrain:", tilesetError)
      }

      const detectionsToDisplay = detections.length > 0 ? detections : hardcodedDetections

      detectionsToDisplay.forEach((detection) => {
        const riskLevel = detection.risk_assessment?.risk_level || "medium"
        const confidence = detection.risk_assessment?.confidence || 0.5

        let pointColor = Cesium.Color.YELLOW
        if (riskLevel === "high" || riskLevel === "critical") {
          pointColor = Cesium.Color.ORANGERED
        } else if (riskLevel === "low") {
          pointColor = Cesium.Color.GREEN
        }

        const type = riskLevel === "high" || riskLevel === "critical" ? "confirmed" : "suspected"

        viewer.entities.add({
          id: detection.id?.toString() || `detection-${Math.random()}`,
          name: `Detection ${detection.id}`,
          position: Cesium.Cartesian3.fromDegrees(Number(detection.longitude), Number(detection.latitude), 200),
          point: {
            pixelSize: 12,
            color: pointColor,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
          },
          label: {
            text: `Detection ${detection.id}`,
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
              <h3 style="margin-bottom: 5px; color: ${type === "confirmed" ? "#d9534f" : "#f0ad4e"};">Detection ${detection.id}</h3>
              <p><strong>ID:</strong> ${detection.id}</p>
              <p><strong>Type:</strong> ${type === "confirmed" ? "✓ Confirmed" : "⚠ Suspected"}</p>
              <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
              <p><strong>Coordinates:</strong> (${Number(detection.latitude).toFixed(4)}°N, ${Number(detection.longitude).toFixed(4)}°E)</p>
              <p><strong>Source:</strong> ${detection.source || "Unknown"}</p>
              <p><strong>Timestamp:</strong> ${new Date(detection.detection_timestamp).toLocaleString()}</p>
              <p><strong>Risk Level:</strong> ${riskLevel.toUpperCase()}</p>
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

      viewerInstanceRef.current = viewer
      setIsLoading(false)
    } catch (err) {
      console.error("Cesium initialization error:", err)
      setError(err instanceof Error ? err.message : String(err))
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (cesiumLoaded && !detectionsLoading) {
      initCesium()
    }
  }, [cesiumLoaded, detectionsLoading, detections])

  if (error) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          padding: "20px",
          backgroundColor: "#1a1a1a",
          color: "white",
        }}
      >
        <h2 style={{ color: "#ff6b6b", marginBottom: "10px" }}>Map Error</h2>
        <p style={{ marginTop: "10px", maxWidth: "600px", textAlign: "center" }}>{error}</p>
        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: "20px",
            padding: "10px 20px",
            backgroundColor: "#4a9eff",
            border: "none",
            borderRadius: "5px",
            color: "white",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <>
      <Script
        src="https://cesium.com/downloads/cesiumjs/releases/1.134/Build/Cesium/Cesium.js"
        strategy="afterInteractive"
        onLoad={() => {
          setCesiumLoaded(true)
        }}
        onError={(e) => {
          console.error("Failed to load Cesium:", e)
          setError("Failed to load Cesium library from CDN")
          setIsLoading(false)
        }}
      />

      <main
        style={{ width: "100vw", height: "100vh", margin: 0, padding: 0, overflow: "hidden", position: "relative" }}
      >
        {(isLoading || detectionsLoading) && (
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              color: "white",
              backgroundColor: "rgba(0,0,0,0.8)",
              padding: "20px 40px",
              borderRadius: "8px",
              zIndex: 1000,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "15px",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                border: "4px solid rgba(255,255,255,0.3)",
                borderTop: "4px solid white",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }}
            />
            <span>Loading Mastomys Tracker Map...</span>
            <style>
              {`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              `}
            </style>
          </div>
        )}

        <div
          style={{
            position: "absolute",
            top: "10px",
            left: "10px",
            backgroundColor: "rgba(0,0,0,0.8)",
            color: "white",
            padding: "15px",
            borderRadius: "8px",
            zIndex: 1000,
            maxWidth: "300px",
          }}
        >
          <h3 style={{ margin: "0 0 10px 0", fontSize: "16px" }}>🐭 Mastomys Tracker</h3>
          <p style={{ margin: "5px 0", fontSize: "14px" }}>
            <strong>Detections:</strong> {detections.length > 0 ? detections.length : hardcodedDetections.length}
          </p>
          <p style={{ margin: "5px 0", fontSize: "14px" }}>
            <strong>Focus:</strong> Nigeria (Lassa Endemic)
          </p>
          {detections.length > 0 && (
            <p style={{ margin: "5px 0", fontSize: "12px", color: "#4ade80" }}>✓ Live data active</p>
          )}
        </div>

        <div
          style={{
            position: "absolute",
            bottom: "10px",
            left: "10px",
            backgroundColor: "rgba(0,0,0,0.8)",
            color: "white",
            padding: "15px",
            borderRadius: "8px",
            zIndex: 1000,
          }}
        >
          <h4 style={{ margin: "0 0 10px 0", fontSize: "14px" }}>Legend</h4>
          <div style={{ display: "flex", alignItems: "center", marginBottom: "5px" }}>
            <div
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: "#d9534f",
                marginRight: "8px",
              }}
            />
            <span style={{ fontSize: "12px" }}>Confirmed Detection</span>
          </div>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: "#f0ad4e",
                marginRight: "8px",
              }}
            />
            <span style={{ fontSize: "12px" }}>Suspected Detection</span>
          </div>
        </div>

        <Link
          href="/monitoring"
          style={{
            position: "absolute",
            top: "10px",
            right: "10px",
            backgroundColor: "rgba(0,0,0,0.8)",
            color: "white",
            padding: "12px 16px",
            borderRadius: "8px",
            zIndex: 1000,
            textDecoration: "none",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
            fontWeight: "500",
            border: "1px solid rgba(255,255,255,0.2)",
            cursor: "pointer",
            transition: "all 0.3s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(0,0,0,0.95)"
            e.currentTarget.style.borderColor = "rgba(255,255,255,0.4)"
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(0,0,0,0.8)"
            e.currentTarget.style.borderColor = "rgba(255,255,255,0.2)"
          }}
        >
          <span>📊</span>
          <span>Monitoring</span>
        </Link>

        <div ref={viewerRef} style={{ width: "100%", height: "100%" }} />

        <div
          style={{
            position: "absolute",
            top: "80px",
            right: "10px",
            backgroundColor: "rgba(0,0,0,0.8)",
            color: "white",
            padding: "15px",
            borderRadius: "8px",
            zIndex: 1000,
            width: "250px",
          }}
        >
          <button
            onClick={() => setShowControls(!showControls)}
            style={{
              width: "100%",
              padding: "8px",
              backgroundColor: "rgba(255,255,255,0.1)",
              border: "1px solid rgba(255,255,255,0.3)",
              borderRadius: "4px",
              color: "white",
              cursor: "pointer",
              fontSize: "12px",
              marginBottom: showControls ? "15px" : "0",
            }}
          >
            🏔️ {showControls ? "Hide" : "Show"} Terrain Controls
          </button>

          {showControls && (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "8px", fontSize: "12px", fontWeight: "500" }}>
                  Vertical Exaggeration: {verticalExaggeration.toFixed(1)}x
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  step="0.1"
                  value={verticalExaggeration}
                  onChange={(e) => setVerticalExaggeration(Number.parseFloat(e.target.value))}
                  style={{ width: "100%", cursor: "pointer" }}
                />
                <p style={{ fontSize: "10px", color: "#999", marginTop: "4px" }}>
                  Multiplier for terrain height (1.0 = normal)
                </p>
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "8px", fontSize: "12px", fontWeight: "500" }}>
                  Reference Height: {relativeHeight.toFixed(0)}m
                </label>
                <input
                  type="range"
                  min="-10000"
                  max="10000"
                  step="100"
                  value={relativeHeight}
                  onChange={(e) => setRelativeHeight(Number.parseFloat(e.target.value))}
                  style={{ width: "100%", cursor: "pointer" }}
                />
                <p style={{ fontSize: "10px", color: "#999", marginTop: "4px" }}>
                  Height reference point for exaggeration
                </p>
              </div>

              <button
                onClick={() => {
                  setVerticalExaggeration(1.0)
                  setRelativeHeight(0)
                }}
                style={{
                  padding: "8px",
                  backgroundColor: "#4a9eff",
                  border: "none",
                  borderRadius: "4px",
                  color: "white",
                  cursor: "pointer",
                  fontSize: "12px",
                }}
              >
                Reset to Default
              </button>
            </div>
          )}
        </div>
      </main>
    </>
  )
}
