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

export default function MapPage() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const viewerInstanceRef = useRef<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [cesiumLoaded, setCesiumLoaded] = useState(false)

  const [verticalExaggeration, setVerticalExaggeration] = useState(1.0)
  const [relativeHeight, setRelativeHeight] = useState(0)
  const [showControls, setShowControls] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<string | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

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
        navigationHelpButton: true,
        skyAtmosphere: new Cesium.SkyAtmosphere(),
        geocoder: Cesium.IonGeocodeProviderType.GOOGLE,
      })

      viewer.scene.verticalExaggeration = verticalExaggeration
      viewer.scene.verticalExaggerationRelativeHeight = relativeHeight

      viewer.scene.globe.enableLighting = true
      viewer.clock.currentTime = Cesium.JulianDate.fromIso8601("2024-01-15T12:00:00Z")

      // Add Photorealistic 3D Tiles
      try {
        const googleTileset = await Cesium.createGooglePhotorealistic3DTileset({
          // Only the Google Geocoder can be used with Google Photorealistic 3D Tiles.  Set the `geocode` property of the viewer constructor options to IonGeocodeProviderType.GOOGLE.
          onlyUsingWithGoogleGeocoder: true,
        });
        viewer.scene.primitives.add(googleTileset);
      } catch (error) {
        console.log(`Error loading Photorealistic 3D Tiles tileset.
        ${error}`);
      }

      if (detections.length) {
        detections.forEach((detection) => {
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
      }

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

  const handleDetect = async () => {
    if (!selectedFile) {
      setSubmitError("Select an image to detect.")
      return
    }

    if (!navigator.geolocation) {
      setSubmitError("Geolocation is not available in this browser.")
      return
    }

    setIsSubmitting(true)
    setSubmitError(null)
    setSubmitStatus(null)

    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
        })
      })

      const formData = new FormData()
      formData.append("file", selectedFile, selectedFile.name)
      formData.append("latitude", position.coords.latitude.toString())
      formData.append("longitude", position.coords.longitude.toString())

      const response = await fetch("/api/detect", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || "Detection failed")
      }

      const data = await response.json()
      const detectionCount = data?.metadata?.detection_count ?? data?.detections?.length ?? 0
      const stored = data?.stored === true
      setSubmitStatus(
        stored
          ? `Detection sent. ${detectionCount} detections.`
          : `Detection completed (${detectionCount}). Not stored in database.`,
      )
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Detection failed")
    } finally {
      setIsSubmitting(false)
    }
  }

  useEffect(() => {
    if (cesiumLoaded && !detectionsLoading) {
      initCesium()
    }
  }, [cesiumLoaded, detectionsLoading, detections])

  useEffect(() => {
    if (!viewerRef.current || !viewerInstanceRef.current) return

    const observer = new ResizeObserver(() => {
      viewerInstanceRef.current?.resize()
      viewerInstanceRef.current?.scene?.requestRender()
    })

    observer.observe(viewerRef.current)
    return () => observer.disconnect()
  }, [])

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
          <div className="loadingOverlay">
            <div className="spinner" />
            <span>Loading Mastomys Tracker Map...</span>
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
            <strong>Detections:</strong> {detections.length}
          </p>
          <p style={{ margin: "5px 0", fontSize: "14px" }}>
            <strong>Focus:</strong> Nigeria (Lassa Endemic)
          </p>
          {detections.length > 0 ? (
            <p style={{ margin: "5px 0", fontSize: "12px", color: "#4ade80" }}>Live data active</p>
          ) : (
            <p style={{ margin: "5px 0", fontSize: "12px", color: "#f0ad4e" }}>No detections yet</p>
          )}
          <div style={{ marginTop: "10px", display: "flex", flexDirection: "column", gap: "8px" }}>
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={(event) => {
                const file = event.target.files?.[0] || null
                setSelectedFile(file)
                setSubmitStatus(null)
                setSubmitError(null)
              }}
              style={{ fontSize: "12px" }}
            />
            <button
              onClick={handleDetect}
              disabled={isSubmitting || !selectedFile}
              style={{
                padding: "8px",
                backgroundColor: isSubmitting || !selectedFile ? "#555" : "#4a9eff",
                border: "none",
                borderRadius: "4px",
                color: "white",
                cursor: isSubmitting || !selectedFile ? "not-allowed" : "pointer",
                fontSize: "12px",
              }}
            >
              {isSubmitting ? "Detecting..." : "Run Detection"}
            </button>
            {submitError && <p style={{ margin: 0, fontSize: "12px", color: "#ff6b6b" }}>{submitError}</p>}
            {submitStatus && <p style={{ margin: 0, fontSize: "12px", color: "#4ade80" }}>{submitStatus}</p>}
          </div>
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

        <div
          ref={viewerRef}
          style={{
            position: "absolute",
            top: 0,
            right: 0,
            bottom: 0,
            left: 0,
          }}
        />

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





