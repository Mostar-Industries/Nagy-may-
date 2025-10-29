export default function ModelChart() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 className="font-semibold flex items-center">🧠 Model Performance</h3>
        <div className="flex space-x-2">
          <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
            XGBoost
          </button>
          <button className="text-xs px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">LSTM</button>
        </div>
      </div>
      <div className="p-4">
        <div className="h-32 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center text-gray-500">
          Model performance chart placeholder
        </div>
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-3 gap-2 text-center">
        <div>
          <div className="text-lg font-bold text-green-500">94%</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Accuracy</div>
        </div>
        <div>
          <div className="text-lg font-bold text-blue-500">92%</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Precision</div>
        </div>
        <div>
          <div className="text-lg font-bold text-purple-500">89%</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">Recall</div>
        </div>
      </div>
    </div>
  )
}
