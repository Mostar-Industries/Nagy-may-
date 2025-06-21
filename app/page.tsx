import Link from "next/link"
import { Brain, MapPin, Activity, TrendingUp, ArrowRight } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Mastomys Tracker</h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">by MoStar Industries</p>
              </div>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <Link
                href="/dashboard"
                className="text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition-colors"
              >
                AI Hub
              </Link>
              <Link
                href="/map"
                className="text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition-colors"
              >
                Map View
              </Link>
              <Link
                href="/dashboard"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Get Started
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            AI-Powered
            <span className="text-indigo-600 dark:text-indigo-400"> Environmental</span>
            <br />
            Monitoring System
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            Real-time analysis of Mastomys Natalensis habitats and Lassa fever risk assessment using advanced machine
            learning and geospatial intelligence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
            >
              Launch AI Hub
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
            <Link
              href="/map"
              className="border-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 px-8 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
            >
              View Map
              <MapPin className="w-5 h-5 ml-2" />
            </Link>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center mb-4">
              <Brain className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Advanced machine learning models for habitat prediction and risk assessment.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-green-100 dark:bg-green-900 flex items-center justify-center mb-4">
              <MapPin className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Geospatial Intelligence</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Real-time mapping with Cesium 3D globe and satellite imagery integration.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Real-time Monitoring</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Live detection alerts and environmental data streaming from IoT sensors.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Predictive Analytics</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Forecast outbreak risks and habitat changes using temporal analysis.
            </p>
          </div>
        </div>

        {/* Quick Access Section */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Quick Access</h2>
            <p className="text-gray-600 dark:text-gray-300">Jump directly to the tools you need</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link
              href="/dashboard"
              className="group bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-4">
                <Brain className="w-8 h-8" />
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Hub Dashboard</h3>
              <p className="text-indigo-100">
                Complete analytics suite with AI insights, risk alerts, and predictive models.
              </p>
            </Link>

            <Link
              href="/map"
              className="group bg-gradient-to-br from-green-500 to-teal-600 rounded-xl p-6 text-white hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-4">
                <MapPin className="w-8 h-8" />
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Full Screen Map</h3>
              <p className="text-green-100">
                Immersive Cesium 3D globe with detection points and environmental layers.
              </p>
            </Link>

            <div className="group bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl p-6 text-white opacity-75">
              <div className="flex items-center justify-between mb-4">
                <Activity className="w-8 h-8" />
                <span className="text-xs bg-gray-700 px-2 py-1 rounded">Coming Soon</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Mobile App</h3>
              <p className="text-gray-200">Field data collection and real-time alerts on your mobile device.</p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl md:text-4xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">142</div>
            <div className="text-gray-600 dark:text-gray-300">Detections Today</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold text-green-600 dark:text-green-400 mb-2">92.7%</div>
            <div className="text-gray-600 dark:text-gray-300">Model Accuracy</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold text-purple-600 dark:text-purple-400 mb-2">8</div>
            <div className="text-gray-600 dark:text-gray-300">High Risk Areas</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">24/7</div>
            <div className="text-gray-600 dark:text-gray-300">Monitoring</div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                  <Brain className="w-5 h-5" />
                </div>
                <span className="text-xl font-bold">Mastomys Tracker</span>
              </div>
              <p className="text-gray-400">Advanced AI-powered environmental monitoring for Lassa fever prevention.</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <div className="space-y-2">
                <Link href="/dashboard" className="block text-gray-400 hover:text-white transition-colors">
                  AI Hub Dashboard
                </Link>
                <Link href="/map" className="block text-gray-400 hover:text-white transition-colors">
                  Map View
                </Link>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <p className="text-gray-400">
                MoStar Industries
                <br />
                Environmental AI Division
                <br />
                support@mostar.ai
              </p>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 MoStar Industries. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
