"use client"

import { useState } from "react"
import { useRealtimeDetections } from "@/hooks/use-realtime-detections"

type ChatMessage = {
  role: "user" | "assistant"
  content: string
}

export default function RemostarChatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { detections } = useRealtimeDetections()

  const sendPrompt = async (text: string) => {
    if (!text.trim()) return
    setIsLoading(true)
    setMessages((prev) => [...prev, { role: "user", content: text }])
    setPrompt("")

    try {
      const response = await fetch("/api/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: text,
          context: {
            detections: detections.slice(0, 5),
            remostar: true,
          },
        }),
      })

      const data = await response.json()
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response || "No response from REMOSTAR." },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: REMOSTAR service unavailable." },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-[1100]">
      <div
        className={[
          "w-[360px] max-w-[90vw] rounded-2xl shadow-2xl border border-slate-800/70",
          "bg-slate-950/95 text-slate-100 backdrop-blur",
          "transition-all duration-300 ease-out origin-bottom-right",
          isOpen ? "opacity-100 scale-100 translate-y-0" : "opacity-0 scale-95 translate-y-3 pointer-events-none",
        ].join(" ")}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/70">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.7)]" />
            <div className="text-sm font-semibold tracking-wide">REMOSTAR</div>
          </div>
          <button
            className="text-xs text-slate-300 hover:text-white transition"
            onClick={() => setIsOpen(false)}
            aria-label="Collapse REMOSTAR"
          >
            Collapse
          </button>
        </div>

        <div className="px-4 py-3 max-h-[320px] overflow-y-auto space-y-3">
          {messages.length === 0 && (
            <div className="text-sm text-slate-300">
              Ask about detections, REMOSTAR interpretation, or risk patterns.
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={[
                "rounded-xl px-3 py-2 text-sm leading-relaxed",
                message.role === "user"
                  ? "bg-amber-500/20 text-amber-100 border border-amber-500/30"
                  : "bg-slate-900/70 text-slate-100 border border-slate-700/60",
              ].join(" ")}
            >
              {message.content}
            </div>
          ))}
        </div>

        <div className="px-4 pb-3">
          <div className="flex flex-wrap gap-2 mb-3">
            {[
              "Summarize latest detections",
              "Any high risk hotspots?",
              "Give REMOSTAR interpretation",
            ].map((label) => (
              <button
                key={label}
                onClick={() => sendPrompt(label)}
                className="text-xs px-2 py-1 rounded-full border border-slate-700/70 text-slate-200 hover:border-amber-400/70 hover:text-amber-100 transition"
                disabled={isLoading}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="flex items-end gap-2">
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault()
                  sendPrompt(prompt)
                }
              }}
              className="flex-1 resize-none rounded-xl bg-slate-900/80 border border-slate-700/70 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-400/80"
              rows={2}
              placeholder="Ask REMOSTAR..."
              disabled={isLoading}
            />
            <button
              onClick={() => sendPrompt(prompt)}
              disabled={isLoading}
              className="h-10 px-4 rounded-xl bg-amber-500 text-slate-900 text-sm font-semibold hover:bg-amber-400 transition disabled:opacity-60"
            >
              {isLoading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>

      <button
        className={[
          "mt-3 ml-auto flex items-center gap-2 px-4 py-3 rounded-full shadow-lg",
          "bg-amber-500 text-slate-900 font-semibold",
          "hover:bg-amber-400 transition",
          "animate-copilot-bob",
          isOpen ? "opacity-0 pointer-events-none" : "opacity-100",
        ].join(" ")}
        onClick={() => setIsOpen(true)}
        aria-label="Open REMOSTAR"
      >
        <span className="h-2 w-2 rounded-full bg-slate-900" />
        Copilot
      </button>

      <style jsx>{`
        @keyframes copilot-bob {
          0%,
          100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-4px);
          }
        }
        :global(.animate-copilot-bob) {
          animation: copilot-bob 2.8s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}
