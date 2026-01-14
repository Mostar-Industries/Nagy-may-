"use client"

import { useEffect, useRef, useState } from "react"
import Script from "next/script"
import { useRealtimeDetections } from "@/hooks/use-realtime-detections"
import { useDetectionMapData } from "@/hooks/use-detection-map-data"
import { Slider } from "@/components/ui/slider"

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

  const [verticalExaggeration, setVerticalExaggeration] = useState(1.0)
  const [relativeHeight, setRelativeHeight] = useState(0)
  const [showControls, setShowControls] = useState(false)

  const { detections, isLoading: detLoading, isConnected, error: detError } = useRealtimeDetections()
  const mapMarkers = useDetectionMapData(detections)

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
        globe: false,
        animation: true,
        timeline: true,
        fullscreenButton: true,
        baseLayerPicker: false,
        homeButton: true,
        infoBox: true,
        navigationHelpButton: true,
        skyAtmosphere: new Cesium.SkyAtmosphere(),
        geocoder: Cesium.IonGeocodeProviderType.GOOGLE,
      })

      // Sine wave
      const customHeightmapWidth = 32;
      const customHeightmapHeight = 32;
      interface CustomHeightmapCallback {
        (x: number, y: number, level: number): Float32Array;
      }

      interface CustomHeightmapTerrainProviderOptions {
        width: number;
        height: number;
        callback: CustomHeightmapCallback;
      }

      const customHeightmapProvider = new Cesium.CustomHeightmapTerrainProvider({
        width: customHeightmapWidth,
        height: customHeightmapHeight,
        callback: function (x: number, y: number, level: number): Float32Array {
          const width = customHeightmapWidth;
          const height = customHeightmapHeight;
          const buffer = new Float32Array(width * height);

          for (let yy = 0; yy < height; yy++) {
            for (let xx = 0; xx < width; xx++) {
              /* eslint-disable-next-line no-unused-vars */
              const u = (x + xx / (width - 1)) / Math.pow(2, level);
              const v = (y + yy / (height - 1)) / Math.pow(2, level);

              const heightValue = 4000 * (Math.sin(8000 * v) * 0.5 + 0.5);

              const index = yy * width + xx;
              buffer[index] = heightValue;
            }
          }

          return buffer;
        },
      } as CustomHeightmapTerrainProviderOptions);


      viewer.scene.verticalExaggeration = verticalExaggeration
      viewer.scene.verticalExaggerationRelativeHeight = relativeHeight

      viewer.scene.globe.enableLighting = true

      try {
        const tileset = await Cesium.Cesium3DTileset.fromIonAssetId(2275207);
        viewer.scene.primitives.add(tileset);
      } catch (error) {
        console.log(error);
      }


      viewerInstanceRef.current = viewer
      // Center on Africa (longitude: 20, latitude: 0, height: 5,000,000)
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(20, 0, 5000000)
      })

      // Switch to Mercator (2D) view
      viewer.scene.mode = Cesium.SceneMode.SCENE2D
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

    mapMarkers.forEach((marker) => {
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
          <div style="font-family: sans-serif; color: #33333300; padding: 10px;">
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

    if (mapMarkers.length > 0 && entitiesRef.current.size <= mapMarkers.length) {
      viewer.zoomTo(viewer.entities)
    }
  }, [mapMarkers])

  useEffect(() => {
    if (!viewerRef.current || !viewerInstanceRef.current) return

    const observer = new ResizeObserver(() => {
      viewerInstanceRef.current?.resize()
      viewerInstanceRef.current?.scene?.requestRender()
    })

    observer.observe(viewerRef.current)
    return () => observer.disconnect()
  }, [])

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

        <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 text-white px-3 py-2 rounded-md text-xs z-20">
          <div>Detections: {mapMarkers.length}</div>
          <div className={`mt-1 ${isConnected ? "text-green-400" : "text-yellow-400"}`}>
            {isConnected ? "● Live" : "○ Connecting..."}
          </div>
        </div>

        <button
          onClick={() => setShowControls(!showControls)}
          className="absolute top-4 right-4 bg-black bg-opacity-60 text-white px-3 py-2 rounded-md text-xs z-20 hover:bg-opacity-80 transition-all"
          title="Toggle terrain controls"
        >
          🏔️ Terrain
        </button>

        {showControls && (
          <div className="absolute top-16 right-4 bg-black bg-opacity-90 text-white p-4 rounded-md text-xs z-20 w-64 space-y-4">
            <div>
              <label className="block mb-2 font-medium">
                Vertical Exaggeration: {verticalExaggeration.toFixed(1)}x
              </label>
              <Slider
                value={[verticalExaggeration]}
                onValueChange={(value) => setVerticalExaggeration(value[0])}
                min={0}
                max={10}
                step={0.1}
                className="w-full"
              />
              <p className="text-gray-400 mt-1 text-[10px]">
                Multiplier for terrain height (1.0 = normal, 3.0 = 3x height)
              </p>
            </div>

            <div>
              <label className="block mb-2 font-medium">Reference Height: {relativeHeight.toFixed(0)}m</label>
              <Slider
                value={[relativeHeight]}
                onValueChange={(value) => setRelativeHeight(value[0])}
                min={-10000}
                max={10000}
                step={100}
                className="w-full"
              />
              <p className="text-gray-400 mt-1 text-[10px]">Height above/below which exaggeration is applied</p>
            </div>

            <button
              onClick={() => {
                setVerticalExaggeration(1.0)
                setRelativeHeight(0)
              }}
              className="w-full px-3 py-2 bg-indigo-600 hover:bg-indigo-700 rounded text-xs transition-colors"
            >
              Reset to Default
            </button>
          </div>
        )}
      </div>
    </>
  )
}
