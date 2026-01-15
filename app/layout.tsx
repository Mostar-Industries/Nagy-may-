import "server-only"
import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { validateEnvironment } from "@/lib/env-validation"

const inter = Inter({ subsets: ["latin"] })

validateEnvironment()

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
      <body className={inter.className}>{children}</body>
    </html>
  )
}
