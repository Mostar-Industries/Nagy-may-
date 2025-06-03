"use client"
import { useEffect, useRef, useState } from "react"
import {
  Ion,
  Viewer,
  Cartesian3,
  Color,
  PointGraphics,
  LabelGraphics,
  createWorldTerrainAsync,
  IonImageryProvider,
  SceneMode, // Import SceneMode
  WebMercatorProjection, // Import WebMercatorProjection
} from "cesium"
import * as Cesium from "cesium" // Import all of Cesium for Cesium.Math, Cesium.LabelStyle etc.
import "cesium/Build/Cesium/Widgets/widgets.css"

// Hardcoded seed detection points
const hardcodedDetections = [
  {
    id: "mn-001",
    name: "Mastomys Alpha",
    latitude: -1.2921,
    longitude: 36.8219,
    altitude: 1661, // Altitude is less relevant in 2D but good to keep for data consistency
    description: "Initial detection point Alpha in Nairobi area.",
  },
  {
    id: "mn-002",
    name: "Mastomys Bravo",
    latitude: -1.295,
    longitude: 36.825,
    altitude: 1670,
    description: "Secondary detection point Bravo, near Alpha.",
  },
  {
    id: "mn-003",
    name: "Mastomys Charlie",
    latitude: -1.3,
    longitude: 36.83,
    altitude: 1680,
    description: "Tertiary detection point Charlie, south-east of Bravo.",
  },
]

export default function MapPage() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const [cesiumViewer, setCesiumViewer] = useState<Viewer | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (typeof window === "undefined") return

    if (viewerRef.current && !cesiumViewer) {
      setError(null)

      const cesiumToken = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN
      if (!cesiumToken) {
        const tokenError = "Cesium Ion token is not defined. Please set NEXT_PUBLIC_CESIUM_ION_TOKEN."
        console.error(tokenError)
        setError(tokenError)
        return
      }
      Ion.defaultAccessToken = cesiumToken

      const initialize = async () => {
        try {
          // Terrain is less visually impactful in 2D but can still affect imagery loading if no other base layer is set.
          // It's fine to keep it, or you can remove it for a purely 2D setup.
          const worldTerrain = await createWorldTerrainAsync()

          const viewerInstance = new Viewer(viewerRef.current!, {
            terrainProvider: worldTerrain, // Can be kept or set to undefined for 2D
            sceneMode: SceneMode.SCENE2D, // Set to 2D mode
            mapProjection: new WebMercatorProjection(), // Use Web Mercator projection
            animation: true,
            timeline: true,
            fullscreenButton: true,
            shouldAnimate: true, // Still useful for smooth zooming/panning
            baseLayerPicker: false,
            infoBox: true,
          })

          try {
            const imageryLayer = viewerInstance.imageryLayers.addImageryProvider(
              await IonImageryProvider.fromAssetId(3954), // Sentinel-2 imagery
            )
          } catch (imageryError) {
            console.error("Error adding Sentinel-2 imagery layer:", imageryError)
          }

          hardcodedDetections.forEach((detection) => {
            viewerInstance.entities.add({
              id: detection.id,
              name: detection.name,
              position: Cartesian3.fromDegrees(detection.longitude, detection.latitude, detection.altitude),
              point: new PointGraphics({
                pixelSize: 12,
                color: Color.ORANGERED,
                outlineColor: Color.WHITE,
                outlineWidth: 2,
              }),
              label: new LabelGraphics({
                text: detection.name,
                font: "14pt sans-serif",
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                fillColor: Color.WHITE,
                outlineColor: Color.BLACK,
                outlineWidth: 2,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                pixelOffset: new Cesium.Cartesian2(0, -15),
              }),
              description: `
                <div style="font-family: sans-serif; color: #333; padding: 10px;">
                  <h3 style="margin-bottom: 5px; color: #007bff;">${detection.name}</h3>
                  <p><strong>ID:</strong> ${detection.id}</p>
                  <p><strong>Coordinates:</strong> (${detection.latitude.toFixed(4)}, ${detection.longitude.toFixed(4)})</p>
                  <p><strong>Altitude:</strong> ${detection.altitude}m</p>
                  <p><strong>Notes:</strong> ${detection.description || "N/A"}</p>
                </div>
              `,
            })
          })

          if (viewerInstance.entities.values.length > 0) {
            viewerInstance
              .flyTo(viewerInstance.entities, {
                duration: 2.0,
              })
              .catch(console.error)
          } else {
            viewerInstance.camera.flyTo({
              destination: Cartesian3.fromDegrees(36.8219, -1.2921, 1500000), // Zoom out a bit more for 2D view
              orientation: {
                // Orientation is less relevant in 2D, but can set initial heading
                heading: Cesium.Math.toRadians(0.0),
                pitch: Cesium.Math.toRadians(0.0), // Pitch is effectively 0 in 2D
                roll: Cesium.Math.toRadians(0.0),
              },
            })
          }

          setCesiumViewer(viewerInstance)
        } catch (initError) {
          console.error("Error initializing Cesium Viewer:", initError)
          const initErrorMessage = `Error initializing map: ${initError instanceof Error ? initError.message : String(initError)}`
          setError(initErrorMessage)
        }
      }
      initialize()
    }

    return () => {
      if (cesiumViewer && !cesiumViewer.isDestroyed()) {
        cesiumViewer.destroy()
        setCesiumViewer(null)
      }
    }
  }, [cesiumViewer])

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
          textAlign: "center",
          backgroundColor: "#282c34",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <h2 style={{ color: "#e06c75", marginBottom: "20px" }}>Map Initialization Error</h2>
        <p style={{ color: "#abb2bf", fontSize: "1.1em", maxWidth: "600px" }}>{error}</p>
        <p style={{ marginTop: "30px", fontSize: "0.9em", color: "#98c379" }}>
          Please ensure <code>NEXT_PUBLIC_CESIUM_ION_TOKEN</code> is correctly set.
        </p>
        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: "30px",
            padding: "10px 20px",
            fontSize: "1em",
            color: "white",
            backgroundColor: "#61afef",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <main style={{ width: "100vw", height: "100vh", margin: 0, padding: 0, overflow: "hidden" }}>
      <div ref={viewerRef} style={{ width: "100%", height: "100%" }} />
    </main>
  )
}
