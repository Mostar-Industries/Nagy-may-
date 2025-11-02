"use client"

import { useState } from "react"

export default function AIAssistant() {
  const [prompt, setPrompt] = useState("")
  const [responses, setResponses] = useState<string[]>([])

  const handleSend = () => {
    if (prompt.trim()) {
      setResponses([...responses, prompt])
      setPrompt("")
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-6">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center">🤖 AI Assistant - Generate Insights</h3>
      </div>
      <div className="p-4">
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300">
              🤖
            </div>
            <div className="ml-3">
              <div className="text-sm font-medium mb-1">AI Assistant</div>
              <div className="text-sm bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <p>
                  Hello! I can help analyze trends, predict outbreaks, or explain any patterns in the data. What would
                  you like to know?
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                    Trends in Lagos
                  </button>
                  <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                    Risk factors
                  </button>
                  <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                    Explain prediction
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {responses.map((response, idx) => (
          <div key={idx} className="mb-4 flex items-start">
            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              👤
            </div>
            <div className="ml-3 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg p-3">{response}</div>
          </div>
        ))}

        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            className="w-full border border-gray-300 dark:border-gray-600 rounded-md pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            rows={3}
            placeholder="Ask me anything about the data, habitats, or predictions..."
          />
          <button
            onClick={handleSend}
            className="absolute right-2 bottom-3 bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-md"
          >
            ✈️
          </button>
        </div>
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
        <span>ℹ️</span> Using DeepSeek-R1-Distill-Qwen-7B with LangChain integration
      </div>
    </div>
  )
}
