export default function RiskAlerts() {
  const alerts = [
    {
      icon: "☢️",
      title: "High risk cluster in Lagos",
      description: "New cluster detected with 87% outbreak probability",
      time: "15 min ago",
      color: "red",
    },
    {
      icon: "📊",
      title: "Unusual movement pattern",
      description: "Detected erratic movements in Ogun State",
      time: "42 min ago",
      color: "orange",
    },
    {
      icon: "💧",
      title: "Rainfall anomaly detected",
      description: "Increased rainfall in Kano may affect habitats",
      time: "2 hours ago",
      color: "yellow",
    },
    {
      icon: "🏠",
      title: "New habitat identified",
      description: "Potential nesting area in Rivers State",
      time: "5 hours ago",
      color: "blue",
    },
  ]

  const bgColors = {
    red: "bg-red-100 dark:bg-red-900",
    orange: "bg-orange-100 dark:bg-orange-900",
    yellow: "bg-yellow-100 dark:bg-yellow-900",
    blue: "bg-blue-100 dark:bg-blue-900",
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center justify-between">
          <span>⚠️ Risk Alerts</span>
          <span className="text-xs bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-2 py-1 rounded-full">
            3 New
          </span>
        </h3>
      </div>
      <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
        {alerts.map((alert, idx) => (
          <div key={idx} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
            <div className="flex items-start">
              <div
                className={`flex-shrink-0 h-10 w-10 rounded-full ${bgColors[alert.color as keyof typeof bgColors]} flex items-center justify-center text-lg`}
              >
                {alert.icon}
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium">{alert.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{alert.description}</p>
                <p className="text-xs text-gray-400 mt-1">{alert.time}</p>
              </div>
            </div>
          </div>
        ))}
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
  )
}
