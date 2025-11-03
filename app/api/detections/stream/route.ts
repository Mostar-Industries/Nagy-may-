import { type NextRequest } from "next/server"
import { createClient } from "@/lib/supabase/server"

export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

/**
 * GET /api/detections/stream
 * Server-Sent Events stream for real-time detection updates
 */
export async function GET(request: NextRequest) {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    async start(controller) {
      console.log('[SSE] Client connected to detection stream')
      
      // Send initial connection message
      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify({ type: 'connected', timestamp: new Date().toISOString() })}\n\n`)
      )
      
      try {
        const supabase = await createClient()
        
        // Subscribe to Supabase realtime changes
        const channel = supabase
          .channel('public:detection_patterns')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'detection_patterns',
            },
            (payload) => {
              const event = {
                type: 'detection',
                data: payload.new,
                timestamp: new Date().toISOString(),
              }
              
              console.log('[SSE] Sending detection event:', event)
              
              try {
                controller.enqueue(
                  encoder.encode(`data: ${JSON.stringify(event)}\n\n`)
                )
              } catch (error) {
                console.error('[SSE] Error sending event:', error)
              }
            }
          )
          .subscribe()
        
        // Keep connection alive with heartbeat
        const heartbeatInterval = setInterval(() => {
          try {
            controller.enqueue(
              encoder.encode(`: heartbeat ${Date.now()}\n\n`)
            )
          } catch (error) {
            console.error('[SSE] Heartbeat error:', error)
            clearInterval(heartbeatInterval)
          }
        }, 30000) // Every 30 seconds
        
        // Cleanup on client disconnect
        request.signal.addEventListener('abort', () => {
          console.log('[SSE] Client disconnected')
          clearInterval(heartbeatInterval)
          supabase.removeChannel(channel)
          controller.close()
        })
      } catch (error) {
        console.error('[SSE] Stream error:', error)
        controller.error(error)
      }
    },
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  })
}
