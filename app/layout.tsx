import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
// Removed ThemeProvider for a cleaner map-focused layout.
// If you need themes on other pages, you might consider a more complex layout structure
// or apply ThemeProvider conditionally.

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Mastomys Natalensis Real-Time Tracker",
  description: "Cesium Globe for Mastomys Natalensis Tracking",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      {/* 
        Removed inter.className from body to prevent potential style conflicts 
        with a full-screen map. If you need the font, ensure its styles
        don't interfere with Cesium's container.
      */}
      <body className={inter.className}>{children}</body>
    </html>
  )
}
