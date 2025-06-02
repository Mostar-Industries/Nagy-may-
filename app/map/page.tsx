"use client"
import { useEffect, useRef, useState } from "react" // Added useState
import { Ion, Viewer, createWorldTerrainAsync, Cartesian3, Math as CesiumMath } from "cesium"
import "cesium/Build/Cesium/Widgets/widgets.css" // Import Cesium's CSS

export default function MapPage() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const viewerInstanceRef = useRef<Viewer | null>(null)
  const [error, setError] = useState<string | null>(null) // State for error message

  useEffect(() => {
    // Ensure this component only runs on the client
    if (typeof window === "undefined") {
      return
    }

    const cesiumToken = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN
    if (!cesiumToken) {
      const errorMessage =
        "Cesium Ion token is not defined. Please set the NEXT_PUBLIC_CESIUM_ION_TOKEN environment variable in your project settings."
      console.error(errorMessage)
      setError(errorMessage) // Set error state
      return
    }

    Ion.defaultAccessToken = cesiumToken
    setError(null) // Clear any previous error if token is found

    // Ensure viewerRef.current is available before proceeding
    if (!viewerRef.current) {
      // This case should ideally not be hit if error state is handled,
      // but as a safeguard:
      setError("Map container element not found. Cannot initialize Cesium viewer.")
      return
    }

    // Clear any manually set error message from previous attempts if div was directly manipulated
    viewerRef.current.innerHTML = ""

    let viewer: Viewer // Declare viewer here to be accessible in cleanup

    const initializeViewer = async () => {
      try {
        if (viewerRef.current && !viewerInstanceRef.current) {
          const worldTerrain = await createWorldTerrainAsync()
          viewer = new Viewer(viewerRef.current!, {
            terrainProvider: worldTerrain,
            animation: true,
            timeline: true,
            fullscreenButton: true,
            shouldAnimate: true,
          })
          viewerInstanceRef.current = viewer

          viewer.camera.flyTo({
            destination: Cartesian3.fromDegrees(20.0, 0.0, 15000000),
            orientation: {
              heading: CesiumMath.toRadians(0.0),
              pitch: CesiumMath.toRadians(-90.0),
              roll: 0.0,
            },
          })
        }
      } catch (err) {
        console.error("Error initializing Cesium Viewer:", err)
        const initErrorMessage = `Error initializing map: ${err instanceof Error ? err.message : String(err)}`
        setError(initErrorMessage)
      }
    }

    initializeViewer()

    return () => {
      if (viewerInstanceRef.current && !viewerInstanceRef.current.isDestroyed()) {
        viewerInstanceRef.current.destroy()
        viewerInstanceRef.current = null
      }
    }
  }, []) // Empty dependency array ensures this runs once on mount

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
        }}
      >
        <h2 style={{ color: "#e06c75", marginBottom: "20px" }}>Map Initialization Error</h2>
        <p style={{ color: "#abb2bf", fontSize: "1.1em", maxWidth: "600px" }}>{error}</p>
        <p style={{ marginTop: "30px", fontSize: "0.9em", color: "#98c379" }}>
          Please ensure the <code>NEXT_PUBLIC_CESIUM_ION_TOKEN</code> is correctly set in your Vercel project's
          environment variables and that you have a stable internet connection.
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
