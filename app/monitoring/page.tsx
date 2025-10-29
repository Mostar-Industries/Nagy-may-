"use client"

import { useEffect, useState } from "react"
import CesiumMap from "@/components/cesium-map"
import StatsCards from "@/components/stats-cards"
import TemporalChart from "@/components/temporal-chart"
import WeatherChart from "@/components/weather-chart"
import ModelChart from "@/components/model-chart"
import RecentDetections from "@/components/recent-detections"
import RiskAlerts from "@/components/risk-alerts"
import HabitatSuitability from "@/components/habitat-suitability"
import AIAssistant from "@/components/ai-assistant"

export default function MonitoringPage() {
  const [isDark, setIsDark] = useState(false)
  const [showMobileSidebar, setShowMobileSidebar] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") || "light"
    setIsDark(savedTheme === "dark")
    if (savedTheme === "dark") {
      document.documentElement.classList.add("dark")
    }
  }, [])

  const toggleTheme = () => {
    const newDark = !isDark
    setIsDark(newDark)
    localStorage.setItem("theme", newDark ? "dark" : "light")
    if (newDark) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }

  return (
    <div className={`flex h-screen ${isDark ? "dark" : ""}`}>
      {/* Sidebar */}
      <aside
        className={`${showMobileSidebar ? "fixed" : "hidden"} md:block md:relative w-64 bg-white dark:bg-gray-800 shadow-md flex-shrink-0 overflow-y-auto z-40`}
      >
        <div className="px-4 py-6">
          <div className="mb-6">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
              Navigation
            </h2>
            <nav className="space-y-1">
              <a
                href="/monitoring"
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md bg-indigo-50 dark:bg-gray-700 text-indigo-700 dark:text-indigo-300"
              >
                <span className="mr-3">📊</span> Dashboard
              </a>
              <a
                href="/map"
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 mt-1"
              >
                <span className="mr-3">🗺️</span> Map View
              </a>
              <a
                href="#"
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 mt-1"
              >
                <span className="mr-3">📈</span> Temporal Analysis
              </a>
              <a
                href="#"
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 mt-1"
              >
                <span className="mr-3">🤖</span> Predictive Models
              </a>
              <a
                href="#"
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 mt-1"
              >
                <span className="mr-3">📷</span> Image Detection
              </a>
            </nav>
          </div>

          <div className="mb-6">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
              Monitoring
            </h2>
            <div className="space-y-1">
              <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700">
                <span>System Status</span>
                <span className="text-green-500">Online</span>
              </div>
              <div className="flex items-center justify-between px-3 py-2 text-sm rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                <span>Model Accuracy</span>
                <span className="text-green-500">92.7%</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      {showMobileSidebar && (
        <div
          className="fixed inset-0 bg-gray-900 bg-opacity-50 z-30 md:hidden"
          onClick={() => setShowMobileSidebar(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-md sticky top-0 z-20">
          <div className="px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowMobileSidebar(!showMobileSidebar)}
                className="md:hidden p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {showMobileSidebar ? "✕" : "☰"}
              </button>
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
                🧬
              </div>
              <h1 className="text-xl font-bold">
                AI Hub <span className="text-sm text-indigo-600 dark:text-indigo-400">Mastomys Tracker</span>
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 relative text-lg"
                >
                  🔔
                  <div className="absolute top-1 right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                </button>
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-md shadow-lg z-50 py-1 border border-gray-200 dark:border-gray-700">
                    <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                      <h3 className="font-semibold">Notifications</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      <div className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                        <div className="flex items-start">
                          <div className="flex-shrink-0 h-10 w-10 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                            ⚠️
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
                            📊
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

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-lg"
              >
                {isDark ? "☀️" : "🌙"}
              </button>

              {/* User Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
                    AD
                  </div>
                </button>
                {showUserMenu && (
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

        {/* Page Content */}
        <div className="container mx-auto px-4 py-6">
          {/* Dashboard Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Environmental & Rodent Monitoring</h2>
              <p className="text-gray-600 dark:text-gray-300">
                Real-time analysis of Mastomys Natalensis habitats and Lassa fever risk assessment
              </p>
            </div>
            <div className="mt-4 md:mt-0 flex space-x-3">
              <div className="relative">
                <select aria-label="Select country" className="appearance-none bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md pl-3 pr-8 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option>Nigeria</option>
                  <option>Ghana</option>
                  <option>Benin</option>
                </select>
                <span className="absolute right-2 top-2.5 pointer-events-none text-gray-400">▼</span>
              </div>
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors flex items-center">
                🔄 Refresh Data
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          <StatsCards />

          {/* Map Visualization */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-6">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold flex items-center">🗺️ Geospatial Habitat Analysis</h3>
            </div>
            <div className="p-4">
              <CesiumMap />
            </div>
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <div className="flex space-x-2">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-red-500 mr-1" />
                  <span className="text-xs">High Risk</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-yellow-500 mr-1" />
                  <span className="text-xs">Medium Risk</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-1" />
                  <span className="text-xs">Low Risk</span>
                </div>
              </div>
              <button className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 flex items-center">
                📚 Layers
              </button>
            </div>
          </div>

          {/* Main Dashboard Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-6">
              {/* Temporal Analysis */}
              <TemporalChart />

              {/* Weather and Model Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <WeatherChart />
                <ModelChart />
              </div>

              {/* Recent Detections */}
              <RecentDetections />
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              <RiskAlerts />
              <HabitatSuitability />
            </div>
          </div>

          {/* AI Assistant */}
          <AIAssistant />
        </div>
      </main>
    </div>
  )
}
