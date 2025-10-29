import { headers } from "next/headers"

export async function getCurrentUser() {
  try {
    const headersList = await headers()
    const authHeader = headersList.get("authorization")

    if (!authHeader?.startsWith("Bearer ")) {
      return null
    }

    // In production, verify JWT token here
    // This is a placeholder for Stack Auth integration
    return {
      id: authHeader.substring(7),
      authenticated: true,
    }
  } catch (error) {
    console.error("[v0] Auth error:", error)
    return null
  }
}

export async function requireAuth() {
  const user = await getCurrentUser()
  if (!user) {
    throw new Error("Unauthorized: Authentication required")
  }
  return user
}
