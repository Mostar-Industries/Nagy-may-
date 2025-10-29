export default function HabitatSuitability() {
  const habitats = [
    { name: "Lagos State", score: 6.8, percentage: 68, color: "blue" },
    { name: "Ogun State", score: 7.4, percentage: 74, color: "green" },
    { name: "Kano State", score: 5.1, percentage: 51, color: "yellow" },
  ]

  const colorClasses = {
    blue: "bg-blue-600",
    green: "bg-green-600",
    yellow: "bg-yellow-500",
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center">🌿 Habitat Suitability</h3>
      </div>
      <div className="p-4">
        {habitats.map((habitat, idx) => (
          <div key={idx}>
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium">{habitat.name}</div>
              <div className="text-sm font-bold text-blue-600 dark:text-blue-400">{habitat.score}/10</div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full ${colorClasses[habitat.color as keyof typeof colorClasses]}`}
                style={{ width: `${habitat.percentage}%` }}
              />
            </div>
            {idx < habitats.length - 1 && <div className="mt-4" />}
          </div>
        ))}
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors">
          📊 Full Analysis Report
        </button>
      </div>
    </div>
  )
}
