"use client"

import { useState } from "react"

interface Message {
  text: string;
  isUser: boolean;
}

export default function AIAssistant() {
  const [prompt, setPrompt] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSend = async () => {
    if (!prompt.trim()) return

    const newMessages: Message[] = [...messages, { text: prompt, isUser: true }]
    setMessages(newMessages)
    setPrompt("")
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch("/api/ai-assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to get response from AI assistant")
      }

      const data = await response.json()
      setMessages([...newMessages, { text: data.response, isUser: false }])
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unknown error occurred"
      setError(message)
      setMessages([...newMessages, { text: `Error: ${message}`, isUser: false }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-6">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold flex items-center">🤖 AI Assistant - Generate Insights</h3>
      </div>
      <div className="p-4">
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4 h-64 overflow-y-auto">
          <div className="flex items-start mb-4">
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
              </div>
            </div>
          </div>

          {messages.map((message, idx) => (
            <div key={idx} className={`mb-4 flex items-start ${message.isUser ? "justify-end" : ""}`}>
              {!message.isUser && (
                <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300">
                  🤖
                </div>
              )}
              <div
                className={`ml-3 text-sm rounded-lg p-3 ${message.isUser ? "bg-blue-100 dark:bg-blue-900" : "bg-gray-50 dark:bg-gray-700"}`}>
                {message.text}
              </div>
              {message.isUser && (
                <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center ml-3">
                  👤
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="mb-4 flex items-start">
               <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300">
                  🤖
                </div>
              <div className="ml-3 text-sm bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                Thinking...
              </div>
            </div>
          )}
          {error && (
             <div className="mb-4 flex items-start">
               <div className="flex-shrink-0 h-10 w-10 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center text-red-600 dark:text-red-300">
                  🤖
                </div>
              <div className="ml-3 text-sm bg-red-50 dark:bg-red-700 rounded-lg p-3 text-red-700 dark:text-red-200">
                {error}
              </div>
            </div>
          )}
        </div>

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
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className="absolute right-2 bottom-3 bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-md disabled:bg-gray-400"
            disabled={isLoading}
          >
            {isLoading ? "..." : "✈️"}
          </button>
        </div>
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
        <span>ℹ️</span> Using Mistral-7B-Instruct-v0.2 with Hugging Face Inference API
      </div>
    </div>
  )
}
