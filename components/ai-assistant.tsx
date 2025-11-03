"use client"

import { useState } from "react"
import { useEventSummary } from "@/hooks/use-event-summary"
import { useRealtimeDetections } from "@/hooks/use-realtime-detections"

export default function AIAssistant() {
  const [prompt, setPrompt] = useState("")
  const [responses, setResponses] = useState<{ user: string; ai: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { detections } = useRealtimeDetections()
  const { summarizeEvents } = useEventSummary()

  const handleAutoSummarize = async () => {
    setIsLoading(true)
    try {
      const recentEvents = detections.slice(0, 5)
      if (recentEvents.length > 0) {
        const summary = await summarizeEvents(recentEvents)
        setResponses((prev) => [
          ...prev,
          {
            user: "Auto-summary: Latest detections",
            ai: summary,
          },
        ])
      }
    } catch (error) {
      console.error("[v0] Auto-summary error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = async () => {
    if (prompt.trim()) {
      setIsLoading(true)
      try {
        // Call Agent API to get AI response
        const response = await fetch("/api/agent/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: prompt,
            context: { detections: detections.slice(0, 5) },
          }),
        })

        const data = await response.json()
        setResponses([
          ...responses,
          {
            user: prompt,
            ai: data.response || "No response from agent",
          },
        ])
        setPrompt("")
      } catch (error) {
        console.error("[v0] Agent query error:", error)
        setResponses([
          ...responses,
          {
            user: prompt,
            ai: "Error: Could not get response from AI agent",
          },
        ])
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-6">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold flex items-center">🤖 AI Assistant - Generate Insights</h3>
          <button
            onClick={handleAutoSummarize}
            disabled={isLoading}
            className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200 hover:bg-indigo-100 disabled:opacity-50"
          >
            {isLoading ? "Summarizing..." : "📊 Auto-Summary"}
          </button>
        </div>
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
                  Hello! I can analyze detections, summarize events, and explain patterns. What would you like to know?
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                    Summarize latest
                  </button>
                  <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                    Species breakdown
                  </button>
                  <button className="text-xs px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                    Risk analysis
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {responses.map((response, idx) => (
          <div key={idx}>
            <div className="mb-4 flex items-start justify-end">
              <div className="flex-shrink-0 text-right">
                <div className="text-sm bg-indigo-100 dark:bg-indigo-900 text-indigo-900 dark:text-indigo-100 rounded-lg p-3 max-w-xs">
                  {response.user}
                </div>
              </div>
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center ml-2">
                👤
              </div>
            </div>
            <div className="mb-4 flex items-start">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300">
                🤖
              </div>
              <div className="ml-3 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg p-3 max-w-2xl">{response.ai}</div>
            </div>
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
            disabled={isLoading}
            className="w-full border border-gray-300 dark:border-gray-600 rounded-md pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
            rows={3}
            placeholder="Ask me anything about detections, species, or predictions..."
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="absolute right-2 bottom-3 bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-md disabled:opacity-50"
          >
            {isLoading ? "..." : "✈️"}
          </button>
        </div>
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
        <span>ℹ️</span> Powered by Gemini with real-time detection context
      </div>
    </div>
  )
}
