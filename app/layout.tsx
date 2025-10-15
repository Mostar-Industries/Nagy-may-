import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Mastomys Tracker - Rodent Detection & Monitoring",
  description: "Real-time tracking and monitoring of Mastomys natalensis populations for Lassa fever surveillance",
    generator: 'v0.app'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://cesium.com/downloads/cesiumjs/releases/1.134/Build/Cesium/Widgets/widgets.css"
        />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
