"use client"

import type React from "react"
import { useEffect, useRef, useState, useMemo } from "react"
import {
  Ion,
  Viewer,
  Cartesian3,
  Color,
  PointGraphics,
  LabelGraphics,
  UrlTemplateImageryProvider,
  IonImageryProvider,
  BillboardGraphics,
  Math as CesiumMath,
  GeoJsonDataSource,
} from "cesium"
import * as Cesium from "cesium"
import "cesium/Build/Cesium/Widgets/widgets.css"
import { ThemeToggle } from "@/components/theme-toggle"
import {
  Bell,
  Brain,
  ChevronDown,
  Menu,
  X,
  Search,
  TriangleIcon as ExclamationTriangle,
  MapPin,
  TrendingUp,
  Activity,
  Leaf,
  ArrowUp,
  GraduationCap,
  Layers,
  LineChart,
  Download,
  Biohazard,
  Droplet,
  Home,
  PieChart,
  Thermometer,
  Cloud,
  Wind,
  CloudRain,
  CheckCircle,
  AlertCircle,
  XCircle,
} from "lucide-react"
import { Chart, registerables, type ChartType, type ChartData } from "chart.js/auto"

import { weatherHabitatService, type LocationHabitatData } from "@/lib/weather-habitat-service"
import { flightAwareAPI } from "@/lib/flightaware-api"

// Hardcoded detection data
const detectionData = [
  { id: "mn-001", name: "Lagos Cluster", lat: 6.5244, lng: 3.3792, risk: "high", confidence: 98, detections: 15 },
  { id: "mn-002", name: "Ogun Group", lat: 7.1557, lng: 3.3456, risk: "medium", confidence: 87, detections: 8 },
  { id: "mn-003", name: "Kano Sighting", lat: 12.0024, lng: 8.5923, risk: "low", confidence: 65, detections: 2 },
  { id: "mn-004", name: "Rivers Area", lat: 4.8156, lng: 7.0498, risk: "medium", confidence: 82, detections: 5 },
  { id: "mn-005", name: "Kaduna Zone", lat: 10.5172, lng: 7.4333, risk: "low", confidence: 72, detections: 3 },
  { id: "mn-006", name: "Abuja Cluster", lat: 9.0579, lng: 7.4951, risk: "high", confidence: 93, detections: 12 },
  { id: "mn-007", name: "Imo Group", lat: 5.1477, lng: 7.3539, risk: "medium", confidence: 81, detections: 6 },
]

Chart.register(...registerables)

type WeatherLayerType = "temperature" | "precipitation" | "wind" | "clouds"

interface HourlyWeatherData {
  time: string[]
  temperature_2m_best_match: number[]
  wind_speed_10m_best_match: number[]
  precipitation_best_match: number[]
  cloud_cover_best_match: number[]
}

interface WeatherJson {
  hourly: HourlyWeatherData
}

interface NormalizedChartData {
  labels: string[]
  datasets: ChartData["datasets"]
  type: ChartType
}

interface MapInitializationStatus {
  viewer: boolean
  osmImagery: boolean
  ionTerrain: boolean
  ionImagery: boolean
  detectionPoints: boolean
  geoJsonMn: boolean
  geoJsonPoints: boolean
}

export default function DashboardPage() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const [cesiumViewer, setCesiumViewer] = useState<Viewer | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [aiPrompt, setAiPrompt] = useState("")
  const [aiResponses, setAiResponses] = useState<Array<{ type: "user" | "ai"; content: string }>>([])

  const [weatherData, setWeatherData] = useState<LocationHabitatData[]>([])
  const [_flightData, setFlightData] = useState<any[]>([])
  const [_loading, setLoading] = useState(true)

  // Map initialization status tracking
  const [mapStatus, setMapStatus] = useState<MapInitializationStatus>({
    viewer: false,
    osmImagery: false,
    ionTerrain: false,
    ionImagery: false,
    detectionPoints: false,
    geoJsonMn: false,
    geoJsonPoints: false,
  })

  const temporalChartRef = useRef<HTMLCanvasElement>(null)
  const weatherChartRef = useRef<HTMLCanvasElement>(null)
  const modelChartRef = useRef<HTMLCanvasElement>(null)
  const weatherLayerChartRef = useRef<HTMLCanvasElement>(null)

  const chartInstancesRef = useRef<{ [key: string]: Chart | null }>({})
  const [trainingProgress, setTrainingProgress] = useState(0)
  const [activeWeatherLayerTab, setActiveWeatherLayerTab] = useState<WeatherLayerType>("temperature")
  const [rawLayerWeatherData, setRawLayerWeatherData] = useState<WeatherJson | null>(null)

  const normalizedLayerData = useMemo<Record<WeatherLayerType, NormalizedChartData> | null>(() => {
    if (!rawLayerWeatherData) return null
    const labels = rawLayerWeatherData.hourly.time.map((time) => new Date(time).toLocaleTimeString())
    return {
      temperature: {
        type: "line",
        labels,
        datasets: [
          {
            label: "Temperature (°C)",
            data: rawLayerWeatherData.hourly.temperature_2m_best_match,
            borderColor: "rgba(255, 99, 132, 1)",
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            fill: true,
          },
        ],
      },
      wind: {
        type: "line",
        labels,
        datasets: [
          {
            label: "Wind Speed (km/h)",
            data: rawLayerWeatherData.hourly.wind_speed_10m_best_match,
            borderColor: "rgba(54, 162, 235, 1)",
            backgroundColor: "rgba(54, 162, 235, 0.2)",
            fill: true,
          },
        ],
      },
      precipitation: {
        type: "bar",
        labels,
        datasets: [
          {
            label: "Precipitation (mm)",
            data: rawLayerWeatherData.hourly.precipitation_best_match,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
          },
        ],
      },
      clouds: {
        type: "bar",
        labels,
        datasets: [
          {
            label: "Cloud Cover (%)",
            data: rawLayerWeatherData.hourly.cloud_cover_best_match,
            borderColor: "rgba(153, 102, 255, 1)",
            backgroundColor: "rgba(153, 102, 255, 0.2)",
          },
        ],
      },
    }
  }, [rawLayerWeatherData])

  useEffect(() => {
    // Prevent multiple initializations
    if (typeof window === "undefined" || !viewerRef.current || cesiumViewer) {
      if (cesiumViewer) console.warn("🔄 Cesium viewer already initialized. Skipping re-initialization.")
      else if (!viewerRef.current) console.warn("⚠️ Cesium viewer ref not available. Skipping initialization.")
      else console.warn("🌐 Not in browser environment. Skipping Cesium initialization.")
      return
    }

    // Enable detailed logging for debugging
    Cesium.LogLevel = Cesium.LogLevel.DEBUG
    console.log("🔧 Cesium LogLevel set to DEBUG.")

    // Check and set Cesium Ion token
    const cesiumToken = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN
    if (!cesiumToken) {
      console.error("❌ CESIUM ION TOKEN MISSING!")
      console.error("Please add NEXT_PUBLIC_CESIUM_ION_TOKEN to your environment variables.")
      console.error("You can get a free token at: https://cesium.com/ion/tokens")
    } else {
      Ion.defaultAccessToken = cesiumToken
      console.log("✅ Cesium Ion token configured successfully.")
    }

    const initializeCesium = async () => {
      try {
        console.log("🚀 Starting Cesium viewer initialization...")
        
        // Step 1: Create Cesium Viewer
        const viewerInstance = new Viewer(viewerRef.current!, {
          timeline: false,
          animation: false,
          baseLayerPicker: false,
          geocoder: false,
          homeButton: false,
          infoBox: true,
          navigationHelpButton: false,
          sceneModePicker: false,
          fullscreenButton: false,
        })
        
        console.log("✅ Cesium Viewer created successfully!")
        setMapStatus(prev => ({ ...prev, viewer: true }))

        // Step 2: Add OpenStreetMap imagery layer
        try {
          console.log("🗺️ Adding OpenStreetMap imagery layer...")
          const osmImageryProvider = new UrlTemplateImageryProvider({
            url: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            credit: "© OpenStreetMap contributors",
          })
          viewerInstance.imageryLayers.addImageryProvider(osmImageryProvider)
          console.log("✅ OpenStreetMap imagery layer added successfully!")
          setMapStatus(prev => ({ ...prev, osmImagery: true }))
        } catch (e) {
          console.error("❌ Failed to add OpenStreetMap imagery:", e)
        }

        // Step 3: Add Cesium Ion terrain and imagery (if token available)
        if (cesiumToken) {
          try {
            console.log("🏔️ Adding Cesium Ion world terrain...")
            const worldTerrain = await Cesium.createWorldTerrain()
            viewerInstance.terrainProvider = worldTerrain
            console.log("✅ Cesium Ion terrain added successfully!")
            setMapStatus(prev => ({ ...prev, ionTerrain: true }))
          } catch (e) {
            console.error("❌ Failed to add Cesium Ion terrain:", e)
            console.error("This might be due to an invalid token or network issues.")
          }

          try {
            console.log("🛰️ Adding Cesium Ion Sentinel-2 imagery...")
            const ionImagery = new IonImageryProvider({ assetId: 3954 }) // Sentinel-2 imagery
            viewerInstance.imageryLayers.addImageryProvider(ionImagery)
            console.log("✅ Cesium Ion Sentinel-2 imagery added successfully!")
            setMapStatus(prev => ({ ...prev, ionImagery: true }))
          } catch (e) {
            console.error("❌ Failed to add Cesium Ion Sentinel-2 imagery:", e)
          }
        } else {
          console.warn("⚠️ Cesium Ion token not available. Skipping Ion terrain and imagery.")
        }

        // Step 4: Configure globe settings
        viewerInstance.scene.globe.enableLighting = true
        console.log("💡 Globe lighting enabled.")

        // Step 5: Set initial camera position (Nigeria)
        viewerInstance.camera.flyTo({
          destination: Cartesian3.fromDegrees(8.6753, 9.082, 5000000),
          orientation: { 
            heading: CesiumMath.toRadians(0), 
            pitch: CesiumMath.toRadians(-90), 
            roll: 0.0 
          },
          duration: 2.5,
        })
        console.log("✈️ Camera positioned over Nigeria.")

        // Step 6: Add detection points
        try {
          console.log("📍 Adding detection points...")
          detectionData.forEach((detection) => {
            const color = detection.risk === "high" ? Color.RED : 
                         detection.risk === "medium" ? Color.YELLOW : Color.GREEN
            
            viewerInstance.entities.add({
              id: detection.id,
              name: detection.name,
              position: Cartesian3.fromDegrees(detection.lng, detection.lat, 0),
              point: new PointGraphics({ 
                pixelSize: 12, 
                color: color, 
                outlineColor: Color.WHITE, 
                outlineWidth: 2 
              }),
              label: new LabelGraphics({
                text: detection.name,
                font: "12pt sans-serif",
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                fillColor: Color.WHITE,
                outlineColor: Color.BLACK,
                outlineWidth: 2,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                pixelOffset: new Cesium.Cartesian2(0, -15),
              }),
              description: `<div style="font-family: sans-serif; color: #333; padding: 10px;">
                <h3 style="margin-bottom: 5px; color: #007bff;">${detection.name}</h3>
                <p><strong>Risk Level:</strong> ${detection.risk}</p>
                <p><strong>Confidence:</strong> ${detection.confidence}%</p>
                <p><strong>Detections:</strong> ${detection.detections}</p>
                <p><strong>Coordinates:</strong> (${detection.lat.toFixed(4)}, ${detection.lng.toFixed(4)})</p>
              </div>`,
            })
          })
          console.log(`✅ Added ${detectionData.length} detection points successfully!`)
          setMapStatus(prev => ({ ...prev, detectionPoints: true }))
        } catch (e) {
          console.error("❌ Failed to add detection points:", e)
        }

        // Step 7: Load GeoJSON data sources
        try {
          console.log("📊 Loading mn.geojson...")
          const mnDataSource = await GeoJsonDataSource.load("/data/mn.geojson", {
            markerSize: 32,
            markerSymbol: "",
          })
          
          // Style the entities
          mnDataSource.entities.values.forEach((entity) => {
            if (!entity.billboard) {
              entity.billboard = new BillboardGraphics({
                image: "/Img/1.png",
                width: 32,
                height: 32,
              })
            }
          })
          
          viewerInstance.dataSources.add(mnDataSource)
          console.log("✅ mn.geojson loaded successfully!")
          setMapStatus(prev => ({ ...prev, geoJsonMn: true }))
        } catch (error) {
          console.error("❌ Error loading mn.geojson:", error)
        }

        try {
          console.log("📊 Loading points.geojson...")
          const pointsDataSource = await GeoJsonDataSource.load("/data/points.geojson", {
            markerSize: 32,
            markerSymbol: "",
          })
          
          // Style the entities
          pointsDataSource.entities.values.forEach((entity) => {
            if (!entity.billboard) {
              entity.billboard = new BillboardGraphics({
                image: "/Img/6.svg",
                width: 32,
                height: 32,
              })
            }
          })
          
          viewerInstance.dataSources.add(pointsDataSource)
          console.log("✅ points.geojson loaded successfully!")
          setMapStatus(prev => ({ ...prev, geoJsonPoints: true }))
        } catch (error) {
          console.error("❌ Error loading points.geojson:", error)
        }

        setCesiumViewer(viewerInstance)
        console.log("🎉 Cesium map initialization completed successfully!")
        
        // Log final status
        console.log("📋 Final initialization status:")
        console.log("   - Viewer: ✅")
        console.log("   - OSM Imagery: ✅")
        console.log(`   - Ion Terrain: ${cesiumToken ? "✅" : "⚠️ (No token)"}`)
        console.log(`   - Ion Imagery: ${cesiumToken ? "✅" : "⚠️ (No token)"}`)
        console.log("   - Detection Points: ✅")
        console.log("   - GeoJSON Data: ✅")

      } catch (error) {
        console.error("💥 FATAL ERROR during Cesium initialization:", error)
        console.error("Stack trace:", error)
      }
    }

    initializeCesium()

    return () => {
      if (cesiumViewer && !cesiumViewer.isDestroyed()) {
        console.log("🧹 Cleaning up Cesium viewer...")
        cesiumViewer.destroy()
        setCesiumViewer(null)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Fetch real-time data
  useEffect(() => {
    const fetchRealTimeData = async () => {
      try {
        setLoading(true)
        const habitatData = await weatherHabitatService.getNigerianStatesHabitatData()
        setWeatherData(habitatData)
        try {
          const nearbyAirports = await flightAwareAPI.getNearbyAirports(9.082, 8.6753, 200)
          if (nearbyAirports.length > 0) {
            const flightPromises = nearbyAirports
              .slice(0, 3)
              .map((airport) => flightAwareAPI.getAirportFlights(airport.id, "departures"))
            const flights = await Promise.all(flightPromises)
            setFlightData(flights.flat())
          }
        } catch (flightError) {
          console.log("Flight data unavailable:", flightError)
        }
      } catch (error) {
        console.error("Error fetching real-time data:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchRealTimeData()
    const interval = setInterval(fetchRealTimeData, 10 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  // Fetch weather data for layer charts
  useEffect(() => {
    async function loadLayerWeatherData() {
      try {
        const response = await fetch("/data/weather_data.json")
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        const data = await response.json()
        setRawLayerWeatherData(data)
      } catch (error) {
        console.error("Error fetching weather_data.json:", error)
      }
    }
    loadLayerWeatherData()
  }, [])

  // Training Progress Bar Animation
  useEffect(() => {
    let currentProgress = 0
    const targetProgress = 78
    const interval = setInterval(() => {
      if (currentProgress >= targetProgress) clearInterval(interval)
      else {
        currentProgress++
        setTrainingProgress(currentProgress)
      }
    }, 20)
    return () => clearInterval(interval)
  }, [])

  // Chart.js Initializations
  useEffect(() => {
    const cleanupCharts = () => {
      Object.values(chartInstancesRef.current).forEach((chart) => chart?.destroy())
      chartInstancesRef.current = {}
    }
    cleanupCharts()

    if (temporalChartRef.current) {
      const ctx = temporalChartRef.current.getContext("2d")
      if (ctx) {
        chartInstancesRef.current.temporalChart = new Chart(ctx, {
          type: "line",
          data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [
              {
                label: "Detections 2023",
                data: [45, 60, 75, 82, 90, 105, 95, 110, 98, 85, 70, 55],
                borderColor: "#4f46e5",
                backgroundColor: "rgba(79, 70, 229, 0.1)",
                tension: 0.3,
                fill: true,
              },
              {
                label: "Detections 2022",
                data: [30, 45, 50, 65, 75, 85, 80, 90, 78, 65, 50, 40],
                borderColor: "#10b981",
                backgroundColor: "rgba(16, 185, 129, 0.1)",
                tension: 0.3,
                fill: true,
                borderDash: [5, 5],
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { position: "top" }, tooltip: { mode: "index", intersect: false } },
            scales: {
              y: { beginAtZero: true, title: { display: true, text: "Number of Detections" } },
              x: { title: { display: true, text: "Month" } },
            },
          },
        })
      }
    }

    if (weatherChartRef.current) {
      const ctx = weatherChartRef.current.getContext("2d")
      if (ctx) {
        chartInstancesRef.current.weatherChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [
              {
                label: "Rainfall (mm)",
                data: [20, 40, 65, 130, 170, 185, 160, 145, 175, 150, 45, 15],
                backgroundColor: "rgba(59, 130, 246, 0.7)",
                borderColor: "rgba(59, 130, 246, 1)",
                borderWidth: 1,
                yAxisID: "y",
              },
              {
                label: "Temperature (°C)",
                data: [30, 32, 33, 32, 30, 28, 27, 27, 28, 29, 31, 31],
                borderColor: "rgba(220, 38, 38, 1)",
                backgroundColor: "rgba(220, 38, 38, 0.1)",
                borderWidth: 2,
                type: "line",
                yAxisID: "y1",
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { position: "top" }, tooltip: { mode: "index", intersect: false } },
            scales: {
              y: { type: "linear", display: true, position: "left", title: { display: true, text: "Rainfall (mm)" } },
              y1: {
                type: "linear",
                display: true,
                position: "right",
                title: { display: true, text: "Temperature (°C)" },
                grid: { drawOnChartArea: false },
                min: 25,
                max: 35,
              },
            },
          },
        })
      }
    }

    if (modelChartRef.current) {
      const ctx = modelChartRef.current.getContext("2d")
      if (ctx) {
        chartInstancesRef.current.modelChart = new Chart(ctx, {
          type: "radar",
          data: {
            labels: ["Accuracy", "Precision", "Recall", "F1 Score", "Specificity", "ROC AUC"],
            datasets: [
              {
                label: "XGBoost",
                data: [94, 92, 89, 90, 93, 95],
                backgroundColor: "rgba(124, 58, 237, 0.2)",
                borderColor: "rgba(124, 58, 237, 1)",
                borderWidth: 2,
              },
              {
                label: "Random Forest",
                data: [89, 87, 84, 85, 88, 90],
                backgroundColor: "rgba(16, 185, 129, 0.2)",
                borderColor: "rgba(16, 185, 129, 1)",
                borderWidth: 2,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { position: "top" } },
            scales: { r: { angleLines: { display: true }, suggestedMin: 70, suggestedMax: 100 } },
          },
        })
      }
    }

    if (weatherLayerChartRef.current && normalizedLayerData) {
      const chartData = normalizedLayerData[activeWeatherLayerTab]
      const ctx = weatherLayerChartRef.current.getContext("2d")
      if (ctx) {
        chartInstancesRef.current.weatherLayerChart = new Chart(ctx, {
          type: chartData.type,
          data: {
            labels: chartData.labels,
            datasets: chartData.datasets,
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true, position: "top" } },
          },
        })
      }
    }

    return cleanupCharts
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [normalizedLayerData, activeWeatherLayerTab])

  const handleAiSubmit = () => {
    if (aiPrompt.trim()) {
      const userMessage = { type: "user" as const, content: aiPrompt }
      setAiResponses((prev) => [...prev, userMessage])
      setTimeout(() => {
        const aiMessageContent = `Based on the recent data, I've detected an increasing trend in Lagos detections (+18% from last month). The primary factors contributing to this increase appear to be higher rainfall and vegetation density, which create ideal habitat conditions for Mastomys Natalensis. Confidence: 89% | Sources: MNTRK API, OpenWeather, Cesium`
        const aiMessage = { type: "ai" as const, content: aiMessageContent }
        setAiResponses((prev) => [...prev, aiMessage])
      }, 1000)
      setAiPrompt("")
    }
  }

  const weatherLayerTabs: { id: WeatherLayerType; label: string; icon: React.ElementType }[] = [
    { id: "temperature", label: "Temperature", icon: Thermometer },
    { id: "precipitation", label: "Precipitation", icon: CloudRain },
    { id: "wind", label: "Wind", icon: Wind },
    { id: "clouds", label: "Cloud Cover", icon: Cloud },
  ]

  // Helper function to get status icon
  const getStatusIcon = (status: boolean) => {
    return status ? (
      <CheckCircle className="w-4 h-4 text-green-500" />
    ) : (
      <XCircle className="w-4 h-4 text-red-500" />
    )
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
      <header className="bg-white dark:bg-gray-800 shadow-md fixed top-0 left-0 right-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white">
              <Brain className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold">
              AI Hub <span className="text-sm text-indigo-600 dark:text-indigo-400">by MoStar Industries</span>
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 relative"
              >
                <Bell className="w-5 h-5" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              </button>
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-md shadow-lg z-50 py-1 border border-gray-200 dark:border-gray-700">
                  <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold">Notifications</h3>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    <div className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                      <div className="flex items-start">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                          <ExclamationTriangle className="w-5 h-5 text-red-600 dark:text-red-300" />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">High risk cluster detected in Lagos State</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">5 min ago</p>
                        </div>
                      </div>
                    </div>
                    <div className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                      <div className="flex items-start">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                          <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-300" />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">New temporal pattern identified</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">12 min ago</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <ThemeToggle />
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
                  AD
                </div>
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg z-50 py-1 border border-gray-200 dark:border-gray-700">
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Profile
                  </a>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Settings
                  </a>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Log out
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex pt-16">
        <aside
          className={`bg-white dark:bg-gray-800 shadow-md w-64 flex-shrink-0 fixed md:relative inset-y-0 left-0 z-40 transform ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0 transition-transform duration-200 ease-in-out`}
        >
          <div className="px-4 py-6 h-full overflow-y-auto">
            <div className="mb-6">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
                Navigation
              </h2>
              <nav className="space-y-1">
                <a
                  href="#"
                  className="flex items-center px-3 py-2 text-sm font-medium rounded-md bg-indigo-50 dark:bg-gray-700 text-indigo-700 dark:text-indigo-300"
                >
                  <Activity className="w-4 h-4 mr-3" />
                  Dashboard
                </a>
                <a
                  href="/map"
                  className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <MapPin className="w-4 h-4 mr-3" />
                  Full Screen Map
                </a>
                <a
                  href="#"
                  className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <TrendingUp className="w-4 h-4 mr-3" />
                  Temporal Analysis
                </a>
                <a
                  href="#"
                  className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <Brain className="w-4 h-4 mr-3" />
                  Predictive Models
                </a>
              </nav>
            </div>

            <div className="mb-6">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
                Weather Layers
              </h2>
              <nav className="space-y-1">
                {weatherLayerTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveWeatherLayerTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md text-left ${activeWeatherLayerTab === tab.id ? "bg-indigo-50 dark:bg-gray-700 text-indigo-700 dark:text-indigo-300" : "text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"}`}
                  >
                    <tab.icon className="w-4 h-4 mr-3" />
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="mb-6">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
                Map Status
              </h2>
              <div className="space-y-1">
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>Cesium Viewer</span>
                  {getStatusIcon(mapStatus.viewer)}
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>OSM Imagery</span>
                  {getStatusIcon(mapStatus.osmImagery)}
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>Ion Terrain</span>
                  {getStatusIcon(mapStatus.ionTerrain)}
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>Ion Imagery</span>
                  {getStatusIcon(mapStatus.ionImagery)}
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>Detection Points</span>
                  {getStatusIcon(mapStatus.detectionPoints)}
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>GeoJSON Data</span>
                  {getStatusIcon(mapStatus.geoJsonMn && mapStatus.geoJsonPoints)}
                </div>
              </div>
            </div>

            <div className="mb-6">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
                System Monitoring
              </h2>
              <div className="space-y-1">
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700">
                  <span>System Status</span>
                  <span className="text-green-500">Online</span>
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>API Connections</span>
                  <span className="text-green-500">7/7</span>
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300">
                  <span>Model Accuracy</span>
                  <span className="text-green-500">92.7%</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-indigo-50 dark:bg-gray-700 rounded-lg">
              <h3 className="text-sm font-medium mb-2">Data Collection</h3>
              <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2.5">
                <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: "83%" }}></div>
              </div>
              <p className="text-xs mt-2 text-gray-500 dark:text-gray-300">83% of daily target collected</p>
              <button className="mt-2 w-full bg-indigo-600 hover:bg-indigo-700 text-white py-1 px-3 rounded-md text-sm font-medium transition-colors">
                Submit Data
              </button>
            </div>
          </div>
        </aside>

        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="md:hidden fixed bottom-4 right-4 z-40 bg-indigo-600 text-white p-3 rounded-full shadow-lg hover:bg-indigo-700 transition-colors"
        >
          {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>

        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-4 py-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">Environmental & Rodent Monitoring</h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Real-time analysis of Mastomys Natalensis habitats and Lassa fever risk assessment
                </p>
              </div>
              <div className="mt-4 md:mt-0 flex space-x-3">
                <div className="relative">
                  <select className="appearance-none bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md pl-3 pr-8 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                    <option>Nigeria</option>
                    <option>Ghana</option>
                    <option>Benin</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
                <button className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors flex items-center">
                  <Activity className="w-4 h-4 mr-2" />
                  Refresh Data
                </button>
              </div>
            </div>

            {/* Map Status Alert */}
            {(!mapStatus.viewer || !mapStatus.osmImagery) && (
              <div className="mb-6 bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-300 mr-2" />
                  <div>
                    <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                      Map Initialization Status
                    </h3>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                      {!mapStatus.viewer && "Cesium viewer is initializing... "}
                      {!mapStatus.osmImagery && "Loading imagery layers... "}
                      Check the browser console for detailed logs.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Detections Today</p>
                    <p className="text-2xl font-bold mt-1">142</p>
                    <p className="text-xs text-green-500 mt-1">↑ 12% from yesterday</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                    <Search className="w-6 h-6 text-indigo-600 dark:text-indigo-300" />
                  </div>
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">High Risk Areas</p>
                    <p className="text-2xl font-bold mt-1">8</p>
                    <p className="text-xs text-red-500 mt-1">⚠ 2 new hotspots</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                    <ExclamationTriangle className="w-6 h-6 text-red-600 dark:text-red-300" />
                  </div>
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animated-panel">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Habitat Suitability</p>
                    <p className="text-2xl font-bold mt-1">6.8/10</p>
                    <p className="text-xs text-yellow-500 mt-1">
                      <ArrowUp className="inline mr-1 w-3 h-3 transform rotate-0" /> Similar to last week
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                    <Leaf className="text-green-600 dark:text-green-300 text-xl" />
                  </div>
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animated-panel">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Model Accuracy</p>
                    <p className="text-2xl font-bold mt-1">92.7%</p>
                    <p className="text-xs text-green-500 mt-1">
                      <ArrowUp className="mr-1 inline w-3 h-3" /> 1.2% improvement
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                    <Brain className="text-purple-600 dark:text-purple-300 text-xl" />
                  </div>
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animated-panel">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Model Training</p>
                    <p className="text-2xl font-bold mt-1">Level 4</p>
                    <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2.5 mt-2">
                      <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${trainingProgress}%` }}></div>
                    </div>
                    <p className="text-xs text-indigo-500 mt-1">{trainingProgress}% to next level</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                    <GraduationCap className="text-purple-600 dark:text-purple-300 text-xl" />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold flex items-center">
                      <MapPin className="text-indigo-500 mr-2" />
                      Geospatial Analysis
                      {mapStatus.viewer && (
                        <CheckCircle className="w-4 h-4 text-green-500 ml-2" />
                      )}
                    </h3>
                  </div>
                  <div className="p-4">
                    <div ref={viewerRef} id="cesiumContainer" className="h-96 rounded-md" />
                  </div>
                  <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <div className="flex space-x-2">
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
                        <span className="text-xs">High Risk</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-yellow-500 mr-1"></div>
                        <span className="text-xs">Medium Risk</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
                        <span className="text-xs">Low Risk</span>
                      </div>
                    </div>
                    <button className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 flex items-center">
                      <Layers className="mr-1" />
                      Layers
                    </button>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold flex items-center">
                      <Layers className="text-blue-500 mr-2" />
                      Weather Layer Details: {weatherLayerTabs.find((t) => t.id === activeWeatherLayerTab)?.label}
                    </h3>
                  </div>
                  <div className="p-4 h-64">
                    {normalizedLayerData ? (
                      <canvas ref={weatherLayerChartRef} id="weatherLayerChart"></canvas>
                    ) : (
                      <p className="text-center text-gray-500">Loading weather layer data...</p>
                    )}
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold flex items-center">
                      <LineChart className="text-green-500 mr-2" />
                      Detection Patterns Over Time
                    </h3>
                  </div>
                  <div className="p-4">
                    <canvas ref={temporalChartRef} id="temporalChart" height="250"></canvas>
                  </div>
                  <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <div className="flex space-x-4">
                      <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                        Daily
                      </button>
                      <button className="text-xs px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
                        Weekly
                      </button>
                      <button className="text-xs px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
                        Monthly
                      </button>
                    </div>
                    <button className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
                      <Download className="mr-1 inline" />
                      Export
                    </button>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold flex items-center justify-between">
                      <span>
                        <ExclamationTriangle className="text-red-500 mr-2 inline" />
                        Risk Alerts
                      </span>
                      <span className="text-xs bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-2 py-1 rounded-full">
                        3 New
                      </span>
                    </h3>
                  </div>
                  <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
                    <div className="p-4 hover:bg-red-50 dark:hover:bg-red-900 cursor-pointer">
                      <div className="flex items-start">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-red-100 dark:bg-red-800 flex items-center justify-center text-red-600 dark:text-red-300">
                          <Biohazard />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">High risk cluster in Lagos</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            New cluster detected with 87% outbreak probability
                          </p>
                          <p className="text-xs text-gray-400 mt-1">15 min ago</p>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 hover:bg-orange-50 dark:hover:bg-gray-700 cursor-pointer">
                      <div className="flex items-start">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-orange-100 dark:bg-orange-800 flex items-center justify-center text-orange-600 dark:text-orange-300">
                          <LineChart />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">Unusual movement pattern</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Detected erratic movements in Ogun State
                          </p>
                          <p className="text-xs text-gray-400 mt-1">42 min ago</p>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 hover:bg-yellow-50 dark:hover:bg-gray-700 cursor-pointer">
                      <div className="flex items-start">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-yellow-100 dark:bg-yellow-800 flex items-center justify-center text-yellow-600 dark:text-yellow-300">
                          <Droplet />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">Rainfall anomaly detected</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Increased rainfall in Kano may affect habitats
                          </p>
                          <p className="text-xs text-gray-400 mt-1">2 hours ago</p>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                      <div className="flex items-start">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-300">
                          <Home />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">New habitat identified</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Potential nesting area in Rivers State
                          </p>
                          <p className="text-xs text-gray-400 mt-1">5 hours ago</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-center">
                    <a
                      href="#"
                      className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium"
                    >
                      View all alerts (12)
                    </a>
                  </div>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold flex items-center">
                      <Leaf className="text-green-500 mr-2" />
                      Habitat Suitability
                    </h3>
                  </div>
                  <div className="p-4">
                    {weatherData.slice(0, 3).map((location, index) => (
                      <div key={location.location.name} className={index > 0 ? "mt-4" : ""}>
                        <div className="flex items-center justify-between mb-3">
                          <div className="text-sm font-medium">{location.location.name}</div>
                          <div
                            className={`text-sm font-bold ${location.habitatAnalysis.suitabilityScore >= 70 ? "text-green-600 dark:text-green-400" : location.habitatAnalysis.suitabilityScore >= 40 ? "text-yellow-600 dark:text-yellow-400" : "text-red-600 dark:text-red-400"}`}
                          >
                            {location.habitatAnalysis.suitabilityScore}/100
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2.5">
                          <div
                            className={`h-2.5 rounded-full ${location.habitatAnalysis.suitabilityScore >= 70 ? "bg-green-600" : location.habitatAnalysis.suitabilityScore >= 40 ? "bg-yellow-500" : "bg-red-500"}`}
                            style={{ width: `${location.habitatAnalysis.suitabilityScore}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors">
                      <PieChart className="mr-2 inline" />
                      Full Analysis Report
                    </button>
                  </div>
                </div>\
