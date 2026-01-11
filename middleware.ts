import { type NextRequest, NextResponse } from "next/server"

const protectedRoutes = ["/monitoring", "/api/detections", "/api/notes"]

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Check if route requires authentication
  const isProtected = protectedRoutes.some((route) => pathname.startsWith(route))

  if (isProtected) {
    const authHeader = request.headers.get("authorization")

    if (!authHeader) {
      // Redirect to login or return 401
      if (pathname.startsWith("/api")) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
      }
      return NextResponse.redirect(new URL("/login", request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/monitoring/:path*", "/api/:path*"],
}
