"use client"

import React, { type ReactNode } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[v0] Error caught by boundary:", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card className="m-4 border-destructive">
          <CardHeader>
            <CardTitle>Something went wrong</CardTitle>
            <CardDescription>An error occurred while rendering this component</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{this.state.error?.message || "Unknown error"}</p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded"
            >
              Try again
            </button>
          </CardContent>
        </Card>
      )
    }

    return this.props.children
  }
}
