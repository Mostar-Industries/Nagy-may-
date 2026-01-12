import { type NextRequest, NextResponse } from "next/server"

interface RateLimitStore {
  [key: string]: {
    count: number
    resetTime: number
  }
}

const rateLimitStore: RateLimitStore = {}

export interface RateLimitConfig {
  windowMs: number // Time window in milliseconds
  maxRequests: number // Max requests per window
}

const DEFAULT_CONFIG: RateLimitConfig = {
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 60, // 60 requests per minute
}

export function rateLimit(config: RateLimitConfig = DEFAULT_CONFIG) {
  return (identifier: string): { success: boolean; remaining: number; resetTime: number } => {
    const now = Date.now()
    const entry = rateLimitStore[identifier]

    // Clean up expired entries periodically
    if (Math.random() < 0.01) {
      Object.keys(rateLimitStore).forEach((key) => {
        if (rateLimitStore[key].resetTime < now) {
          delete rateLimitStore[key]
        }
      })
    }

    // If no entry or expired, create new
    if (!entry || entry.resetTime < now) {
      rateLimitStore[identifier] = {
        count: 1,
        resetTime: now + config.windowMs,
      }
      return {
        success: true,
        remaining: config.maxRequests - 1,
        resetTime: now + config.windowMs,
      }
    }

    // Check if limit exceeded
    if (entry.count >= config.maxRequests) {
      return {
        success: false,
        remaining: 0,
        resetTime: entry.resetTime,
      }
    }

    // Increment count
    entry.count++
    return {
      success: true,
      remaining: config.maxRequests - entry.count,
      resetTime: entry.resetTime,
    }
  }
}

export function getRateLimitIdentifier(request: NextRequest): string {
  // Try to get IP from various headers (works with proxies/CDNs)
  const forwarded = request.headers.get("x-forwarded-for")
  const realIp = request.headers.get("x-real-ip")
  const ip = forwarded?.split(",")[0] || realIp || "unknown"

  return ip
}

export function createRateLimitResponse(resetTime: number): NextResponse {
  const retryAfter = Math.ceil((resetTime - Date.now()) / 1000)

  return NextResponse.json(
    {
      error: "Rate limit exceeded",
      message: `Too many requests. Please try again in ${retryAfter} seconds.`,
      retryAfter,
    },
    {
      status: 429,
      headers: {
        "Retry-After": retryAfter.toString(),
        "X-RateLimit-Reset": new Date(resetTime).toISOString(),
      },
    },
  )
}
