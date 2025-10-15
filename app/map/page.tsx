"use client"
import { useEffect, useRef } from "react"
import { Ion, Viewer, createWorldTerrainAsync, Cartesian3, Math as CesiumMath } from "cesium"
import "cesium/Build/Cesium/Widgets/widgets.css" // Import Cesium's CSS

export default function MapPage() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const viewerInstanceRef = useRef<Viewer | null>(null) // To store viewer instance for cleanup

  useEffect(() => {
    // Ensure this component only runs on the client
    if (typeof window === "undefined" || !viewerRef.current) {
      return
    }

    const cesiumToken = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN
    if (!cesiumToken) {
      console.error("Cesium Ion token is not defined. Please set NEXT_PUBLIC_CESIUM_ION_TOKEN.")
      // Optionally, display a message to the user in the UI
      if (viewerRef.current) {
        viewerRef.current.innerHTML =
          '<p style="color: red; text-align: center; padding-top: 20px;">Error: Cesium Ion token is not configured. Map cannot be loaded.</p>'
      }
      return
    }
    Ion.defaultAccessToken = cesiumToken

    let viewer: Viewer

    const initializeViewer = async () => {
      try {
        if (viewerRef.current && !viewerInstanceRef.current) {
          const worldTerrain = await createWorldTerrainAsync()
          viewer = new Viewer(viewerRef.current!, {
            terrainProvider: worldTerrain,
            animation: true, // Show animation controls
            timeline: true, // Show timeline
            fullscreenButton: true, // Show fullscreen button
            shouldAnimate: true, // Start animation by default
            // Other common options you might want:
            // baseLayerPicker: true,      // Allow changing base imagery
            // geocoder: true,             // Show geocoder search
            // homeButton: true,           // Show home button
            // sceneModePicker: true,      // Allow 2D/3D/Columbus view
            // navigationHelpButton: true, // Show navigation help
          })
          viewerInstanceRef.current = viewer // Store instance

          // Example: Fly to a specific location (e.g., somewhere in Africa for Mastomys Natalensis)
          viewer.camera.flyTo({
            destination: Cartesian3.fromDegrees(20.0, 0.0, 15000000), // Lon, Lat, Height (meters)
            orientation: {
              heading: CesiumMath.toRadians(0.0),
              pitch: CesiumMath.toRadians(-90.0),
              roll: 0.0,
            },
          })
        }
      } catch (error) {
        console.error("Error initializing Cesium Viewer:", error)
        if (viewerRef.current) {
          viewerRef.current.innerHTML = `<p style="color: red; text-align: center; padding-top: 20px;">Error initializing map: ${error instanceof Error ? error.message : String(error)}</p>`
        }
      }
    }

    initializeViewer()

    return () => {
      // Cleanup: destroy the viewer instance if it exists
      if (viewerInstanceRef.current && !viewerInstanceRef.current.isDestroyed()) {
        viewerInstanceRef.current.destroy()
        viewerInstanceRef.current = null
      }
    }
  }, []) // Empty dependency array ensures this runs once on mount and cleans up on unmount

  return (
    <main style={{ width: "100vw", height: "100vh", margin: 0, padding: 0, overflow: "hidden" }}>
      <div ref={viewerRef} style={{ width: "100%", height: "100%" }} />
    </main>
  )
}
