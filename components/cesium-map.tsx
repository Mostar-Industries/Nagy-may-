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

async function loadNigeriaAdminLayers(viewer: any, Cesium: any) {
  const statesGeoJson = await fetch(
    "https://raw.githubusercontent.com/tanerochris/nigeria-state-and-lgas-geojson/master/states.geojson"
  ).then((res) => res.json())

  const statesDataSource = await Cesium.GeoJsonDataSource.load(statesGeoJson, {
    stroke: Cesium.Color.WHITE,
    strokeWidth: 2,
    fill: Cesium.Color.TRANSPARENT,
    clampToGround: true,
  })

  viewer.dataSources.add(statesDataSource)

  const highRiskStates = ["Edo", "Ondo", "Ebonyi", "Plateau", "Taraba", "Bauchi", "Gombe"]
  const mediumRiskStates = ["Ogun", "Osun", "Ekiti", "Kogi", "Nasarawa", "Kaduna"]

  statesDataSource.entities.values.forEach((entity: any) => {
    const stateName = entity.properties?.admin1Name?.getValue?.()

    if (highRiskStates.includes(stateName)) {
      entity.polygon.material = Cesium.Color.RED.withAlpha(0.2)
      entity.polygon.outlineColor = Cesium.Color.RED
    } else if (mediumRiskStates.includes(stateName)) {
      entity.polygon.material = Cesium.Color.ORANGE.withAlpha(0.15)
      entity.polygon.outlineColor = Cesium.Color.ORANGE
    } else {
      entity.polygon.material = Cesium.Color.GREEN.withAlpha(0.1)
      entity.polygon.outlineColor = Cesium.Color.WHITE
    }

    if (entity.polygon?.hierarchy) {
      const hierarchy = entity.polygon.hierarchy.getValue()
      const positions = hierarchy?.positions
      if (positions?.length) {
        const center = Cesium.BoundingSphere.fromPoints(positions).center

        viewer.entities.add({
          position: center,
          label: {
            text: stateName || "Unknown",
            font: "16px sans-serif",
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 3,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            verticalOrigin: Cesium.VerticalOrigin.CENTER,
            horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
            disableDepthTestDistance: Number.POSITIVE_INFINITY,
          },
        })
      }
    }
  })

  return statesDataSource
}

async function loadLGABoundaries(viewer: any, Cesium: any) {
  const lgaGeoJson = await fetch(
    "https://raw.githubusercontent.com/tanerochris/nigeria-state-and-lgas-geojson/master/lgas.geojson"
  ).then((res) => res.json())

  const lgaDataSource = await Cesium.GeoJsonDataSource.load(lgaGeoJson, {
    stroke: Cesium.Color.GRAY,
    strokeWidth: 1,
    fill: Cesium.Color.TRANSPARENT,
    clampToGround: true,
  })

  viewer.dataSources.add(lgaDataSource)
  return lgaDataSource
}

function addEndemicZones(viewer: any, Cesium: any) {
  const endemicZones = [
    {
      name: "Edo Endemic Zone",
      center: [6.34, 6.63],
      radius: 100000,
      color: Cesium.Color.RED,
      cases: 1247,
    },
    {
      name: "Ondo Endemic Zone",
      center: [5.19, 6.91],
      radius: 85000,
      color: Cesium.Color.ORANGE,
      cases: 892,
    },
    {
      name: "Ebonyi Endemic Zone",
      center: [8.11, 6.26],
      radius: 75000,
      color: Cesium.Color.RED,
      cases: 1034,
    },
    {
      name: "Plateau Endemic Zone",
      center: [8.89, 9.22],
      radius: 90000,
      color: Cesium.Color.ORANGE,
      cases: 673,
    },
    {
      name: "Taraba Endemic Zone",
      center: [10.77, 7.87],
      radius: 80000,
      color: Cesium.Color.ORANGE,
      cases: 521,
    },
    {
      name: "Bauchi Endemic Zone",
      center: [9.84, 10.31],
      radius: 70000,
      color: Cesium.Color.YELLOW,
      cases: 412,
    },
  ]

  endemicZones.forEach((zone) => {
    viewer.entities.add({
      name: zone.name,
      position: Cesium.Cartesian3.fromDegrees(zone.center[0], zone.center[1]),
      ellipse: {
        semiMinorAxis: zone.radius,
        semiMajorAxis: zone.radius,
        material: zone.color.withAlpha(0.25),
        outline: true,
        outlineColor: zone.color,
        outlineWidth: 3,
        height: 0,
      },
      label: {
        text: `${zone.name}\n${zone.cases} cases`,
        font: "14px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -20),
        showBackground: true,
        backgroundColor: zone.color.withAlpha(0.7),
        backgroundPadding: new Cesium.Cartesian2(8, 4),
      },
    })
  })
}

function addHealthFacilities(viewer: any, Cesium: any) {
  const facilities = [
    { name: "Irrua Specialist Teaching Hospital", coords: [6.261, 6.739], type: "Lassa Treatment Center" },
    { name: "Federal Medical Centre Owo", coords: [5.587, 7.196], type: "Treatment Center" },
    { name: "Alex Ekwueme Federal University Teaching Hospital", coords: [8.113, 6.264], type: "Treatment Center" },
    { name: "Plateau Specialist Hospital", coords: [8.891, 9.923], type: "Treatment Center" },
    { name: "Federal Medical Centre Jalingo", coords: [11.356, 8.89], type: "Treatment Center" },
  ]

  facilities.forEach((facility) => {
    viewer.entities.add({
      name: facility.name,
      position: Cesium.Cartesian3.fromDegrees(facility.coords[0], facility.coords[1]),
      billboard: {
        image:
          "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSIxNCIgZmlsbD0iI0ZGRiIgc3Ryb2tlPSIjRjAwIiBzdHJva2Utd2lkdGg9IjIiLz48cGF0aCBkPSJNMTEgMTZoMTBNMTYgMTF2MTAiIHN0cm9rZT0iI0YwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+PC9zdmc+",
        scale: 1.0,
      },
      label: {
        text: facility.name,
        font: "12px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.RED,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: Cesium.VerticalOrigin.TOP,
        pixelOffset: new Cesium.Cartesian2(0, 20),
      },
    })
  })
}

function addNigeriaUnityLayers(viewer: any, Cesium: any) {
  const nigerianStates = [
    { name: "Abia", coords: [7.5, 5.4], boundary: [[7.0, 4.8], [8.1, 4.8], [8.1, 6.0], [7.0, 6.0], [7.0, 4.8]] },
    { name: "Adamawa", coords: [12.5, 9.3], boundary: [[11.0, 7.0], [14.0, 7.0], [14.0, 11.0], [11.0, 11.0], [11.0, 7.0]] },
    { name: "Akwa Ibom", coords: [7.9, 5.0], boundary: [[7.3, 4.3], [8.5, 4.3], [8.5, 5.7], [7.3, 5.7], [7.3, 4.3]] },
    { name: "Anambra", coords: [6.9, 6.2], boundary: [[6.4, 5.6], [7.4, 5.6], [7.4, 6.8], [6.4, 6.8], [6.4, 5.6]] },
    { name: "Bauchi", coords: [9.8, 10.3], boundary: [[8.8, 9.0], [11.0, 9.0], [11.0, 12.0], [8.8, 12.0], [8.8, 9.0]] },
    { name: "Bayelsa", coords: [6.1, 4.7], boundary: [[5.5, 4.0], [6.7, 4.0], [6.7, 5.4], [5.5, 5.4], [5.5, 4.0]] },
    { name: "Benue", coords: [8.8, 7.3], boundary: [[7.3, 6.2], [10.0, 6.2], [10.0, 8.5], [7.3, 8.5], [7.3, 6.2]] },
    { name: "Borno", coords: [13.1, 11.8], boundary: [[11.0, 10.0], [14.6, 10.0], [14.6, 13.9], [11.0, 13.9], [11.0, 10.0]] },
    { name: "Cross River", coords: [8.3, 5.4], boundary: [[7.7, 4.3], [9.4, 4.3], [9.4, 6.9], [7.7, 6.9], [7.7, 4.3]] },
    { name: "Delta", coords: [5.7, 5.4], boundary: [[5.0, 4.8], [6.4, 4.8], [6.4, 6.0], [5.0, 6.0], [5.0, 4.8]] },
    { name: "Ebonyi", coords: [8.1, 6.3], boundary: [[7.7, 5.7], [8.5, 5.7], [8.5, 6.9], [7.7, 6.9], [7.7, 5.7]] },
    { name: "Edo", coords: [6.3, 6.5], boundary: [[5.6, 5.8], [7.0, 5.8], [7.0, 7.2], [5.6, 7.2], [5.6, 5.8]] },
    { name: "Ekiti", coords: [5.2, 7.7], boundary: [[4.8, 7.3], [5.6, 7.3], [5.6, 8.1], [4.8, 8.1], [4.8, 7.3]] },
    { name: "Enugu", coords: [7.5, 6.5], boundary: [[7.1, 6.0], [7.9, 6.0], [7.9, 7.0], [7.1, 7.0], [7.1, 6.0]] },
    { name: "FCT", coords: [7.4, 9.1], boundary: [[6.9, 8.5], [7.9, 8.5], [7.9, 9.7], [6.9, 9.7], [6.9, 8.5]] },
    { name: "Gombe", coords: [11.2, 10.3], boundary: [[10.0, 9.0], [12.4, 9.0], [12.4, 11.6], [10.0, 11.6], [10.0, 9.0]] },
    { name: "Imo", coords: [7.0, 5.5], boundary: [[6.6, 5.0], [7.4, 5.0], [7.4, 6.0], [6.6, 6.0], [6.6, 5.0]] },
    { name: "Jigawa", coords: [9.3, 12.2], boundary: [[8.0, 11.0], [10.6, 11.0], [10.6, 13.4], [8.0, 13.4], [8.0, 11.0]] },
    { name: "Kaduna", coords: [7.4, 10.5], boundary: [[6.1, 9.0], [8.7, 9.0], [8.7, 12.0], [6.1, 12.0], [6.1, 9.0]] },
    { name: "Kano", coords: [8.5, 12.0], boundary: [[7.5, 11.0], [9.5, 11.0], [9.5, 13.0], [7.5, 13.0], [7.5, 11.0]] },
    { name: "Katsina", coords: [7.6, 12.9], boundary: [[6.8, 12.0], [8.4, 12.0], [8.4, 13.8], [6.8, 13.8], [6.8, 12.0]] },
    { name: "Kebbi", coords: [4.2, 12.4], boundary: [[3.0, 11.0], [5.4, 11.0], [5.4, 13.8], [3.0, 13.8], [3.0, 11.0]] },
    { name: "Kogi", coords: [6.7, 7.8], boundary: [[5.9, 6.5], [7.5, 6.5], [7.5, 9.1], [5.9, 9.1], [5.9, 6.5]] },
    { name: "Kwara", coords: [4.6, 8.5], boundary: [[2.8, 7.7], [6.4, 7.7], [6.4, 9.3], [2.8, 9.3], [2.8, 7.7]] },
    { name: "Lagos", coords: [3.4, 6.5], boundary: [[2.7, 6.2], [3.7, 6.2], [3.7, 6.7], [2.7, 6.7], [2.7, 6.2]] },
    { name: "Nasarawa", coords: [8.5, 8.5], boundary: [[7.7, 7.7], [9.3, 7.7], [9.3, 9.3], [7.7, 9.3], [7.7, 7.7]] },
    { name: "Niger", coords: [6.6, 9.6], boundary: [[3.0, 8.2], [10.2, 8.2], [10.2, 11.0], [3.0, 11.0], [3.0, 8.2]] },
    { name: "Ogun", coords: [3.6, 7.2], boundary: [[2.7, 6.2], [4.6, 6.2], [4.6, 8.0], [2.7, 8.0], [2.7, 6.2]] },
    { name: "Ondo", coords: [5.2, 6.9], boundary: [[4.5, 5.8], [6.0, 5.8], [6.0, 8.0], [4.5, 8.0], [4.5, 5.8]] },
    { name: "Osun", coords: [4.5, 7.5], boundary: [[4.0, 7.0], [5.0, 7.0], [5.0, 8.0], [4.0, 8.0], [4.0, 7.0]] },
    { name: "Oyo", coords: [4.0, 8.0], boundary: [[2.9, 7.3], [5.1, 7.3], [5.1, 9.1], [2.9, 9.1], [2.9, 7.3]] },
    { name: "Plateau", coords: [9.2, 9.2], boundary: [[8.2, 8.2], [10.2, 8.2], [10.2, 10.2], [8.2, 10.2], [8.2, 8.2]] },
    { name: "Rivers", coords: [6.8, 4.8], boundary: [[6.0, 4.3], [7.6, 4.3], [7.6, 5.8], [6.0, 5.8], [6.0, 4.3]] },
    { name: "Sokoto", coords: [5.2, 13.1], boundary: [[4.0, 12.0], [6.4, 12.0], [6.4, 14.0], [4.0, 14.0], [4.0, 12.0]] },
    { name: "Taraba", coords: [9.8, 7.9], boundary: [[9.0, 6.5], [11.3, 6.5], [11.3, 9.3], [9.0, 9.3], [9.0, 6.5]] },
    { name: "Yobe", coords: [11.9, 12.3], boundary: [[10.9, 11.0], [13.2, 11.0], [13.2, 13.6], [10.9, 13.6], [10.9, 11.0]] },
    { name: "Zamfara", coords: [6.2, 12.2], boundary: [[5.0, 11.0], [7.4, 11.0], [7.4, 13.4], [5.0, 13.4], [5.0, 11.0]] },
  ]

  const geopoliticalZones = [
    { name: "North Central", color: Cesium.Color.ORANGE, states: ["FCT", "Benue", "Kogi", "Kwara", "Nasarawa", "Niger", "Plateau"] },
    { name: "North East", color: Cesium.Color.RED, states: ["Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"] },
    { name: "North West", color: Cesium.Color.PURPLE, states: ["Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"] },
    { name: "South East", color: Cesium.Color.GREEN, states: ["Abia", "Anambra", "Ebonyi", "Enugu", "Imo"] },
    { name: "South South", color: Cesium.Color.CYAN, states: ["Akwa Ibom", "Bayelsa", "Cross River", "Delta", "Edo", "Rivers"] },
    { name: "South West", color: Cesium.Color.YELLOW, states: ["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"] },
  ]

  const zoneColorByState = new Map<string, any>()
  geopoliticalZones.forEach((zone) => {
    zone.states.forEach((state) => zoneColorByState.set(state, zone.color))
  })

  nigerianStates.forEach((state) => {
    const zoneColor = zoneColorByState.get(state.name) || Cesium.Color.BLUE
    viewer.entities.add({
      polygon: {
        hierarchy: Cesium.Cartesian3.fromDegreesArray(state.boundary.flat()),
        material: zoneColor.withAlpha(0.1),
        outline: true,
        outlineColor: zoneColor.withAlpha(0.8),
        outlineWidth: 1,
      },
    })

    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(state.coords[0], state.coords[1]),
      label: {
        text: state.name,
        font: "12px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 1,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        pixelOffset: new Cesium.Cartesian2(0, -20),
      },
    })
  })

  const majorCities = [
    { name: "Lagos", coords: [3.39, 6.45], pop: "15M" },
    { name: "Kano", coords: [8.52, 12.0], pop: "4M" },
    { name: "Ibadan", coords: [3.9, 7.38], pop: "3.6M" },
    { name: "Abuja", coords: [7.49, 9.06], pop: "3.3M" },
    { name: "Port Harcourt", coords: [7.01, 4.75], pop: "3.2M" },
    { name: "Benin City", coords: [5.63, 6.34], pop: "1.8M" },
    { name: "Maiduguri", coords: [13.16, 11.85], pop: "1.2M" },
    { name: "Zaria", coords: [7.7, 11.09], pop: "975K" },
    { name: "Aba", coords: [7.37, 5.11], pop: "897K" },
    { name: "Jos", coords: [8.86, 9.93], pop: "816K" },
  ]

  majorCities.forEach((city) => {
    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(city.coords[0], city.coords[1]),
      point: {
        pixelSize: 8,
        color: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
      },
      label: {
        text: `${city.name}\n(${city.pop})`,
        font: "10px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 1,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        pixelOffset: new Cesium.Cartesian2(0, -25),
      },
    })
  })

  const lassaEndemicZones = [
    { name: "Edo Endemic Zone", center: [6.3, 6.5], radius: 120000, risk: "Very High" },
    { name: "Ondo Endemic Zone", center: [5.2, 6.9], radius: 100000, risk: "High" },
    { name: "Ebonyi Endemic Zone", center: [8.1, 6.3], radius: 80000, risk: "High" },
    { name: "Plateau Endemic Zone", center: [9.2, 9.2], radius: 90000, risk: "Medium" },
    { name: "Taraba Endemic Zone", center: [9.8, 7.9], radius: 70000, risk: "Medium" },
  ]

  lassaEndemicZones.forEach((zone) => {
    const color =
      zone.risk === "Very High" ? Cesium.Color.DARKRED : zone.risk === "High" ? Cesium.Color.RED : Cesium.Color.ORANGE

    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(zone.center[0], zone.center[1]),
      ellipse: {
        semiMinorAxis: zone.radius,
        semiMajorAxis: zone.radius,
        material: color.withAlpha(0.3),
        outline: true,
        outlineColor: color,
      },
      label: {
        text: `${zone.name}\n${zone.risk} Risk`,
        font: "11px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: color,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      },
    })
  })

  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(8.0, 9.5, 2000000),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(-60),
      roll: 0,
    },
  })
}

async function initializeNigeriaLayers(viewer: any, Cesium: any) {
  console.log("Loading Nigeria Administrative Layers...")
  await loadNigeriaAdminLayers(viewer, Cesium)
  await loadLGABoundaries(viewer, Cesium)
  addEndemicZones(viewer, Cesium)
  addHealthFacilities(viewer, Cesium)
  addNigeriaUnityLayers(viewer, Cesium)
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

      try {
        await initializeNigeriaLayers(viewer, Cesium)
      } catch (error) {
        console.log("Nigeria layers failed to load:", error)
      }


      viewerInstanceRef.current = viewer
      // Center on Nigeria for the administrative layers
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(8.0, 9.5, 2000000),
        orientation: {
          heading: 0,
          pitch: Cesium.Math.toRadians(-60),
          roll: 0,
        },
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
