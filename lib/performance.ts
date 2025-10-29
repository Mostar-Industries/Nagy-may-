export function reportWebVitals(metric: any) {
  if (typeof window !== "undefined") {
    // Send to analytics service
    console.log("[v0] Web Vital:", {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
    })

    // Example: Send to external service
    if (window.location.hostname !== "localhost") {
      // fetch('/api/analytics', {
      //   method: 'POST',
      //   body: JSON.stringify(metric),
      // })
    }
  }
}

export function measurePerformance(label: string) {
  const start = performance.now()
  return () => {
    const end = performance.now()
    console.log(`[v0] ${label}: ${(end - start).toFixed(2)}ms`)
  }
}
