import "server-only"

const requiredServerEnvVars = ["DATABASE_URL", "POSTGRES_URL", "CESIUM_ION_TOKEN"]

const optionalServerEnvVars = [
  "FLIGHTAWARE_API_KEY",
  "OPENWEATHER_API_KEY",
]

// These should only be used if explicitly needed and should be accessed through server-side routes
const optionalPublicEnvVars: string[] = [
  "NEXT_PUBLIC_SUPABASE_URL",
  "NEXT_PUBLIC_SUPABASE_ANON_KEY",
]

export function validateEnvironment() {
  const missing: string[] = []

  for (const envVar of requiredServerEnvVars) {
    if (!process.env[envVar]) {
      missing.push(envVar)
    }
  }

  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(", ")}`)
  }

  const notConfigured: string[] = []
  for (const envVar of [...optionalServerEnvVars, ...optionalPublicEnvVars]) {
    if (!process.env[envVar]) {
      notConfigured.push(envVar)
    }
  }

  if (notConfigured.length > 0) {
    console.warn("[v0] Optional environment variables not configured:", notConfigured.join(", "))
    console.warn("[v0] App will work with reduced functionality. Configure these for full features.")
  }
}
