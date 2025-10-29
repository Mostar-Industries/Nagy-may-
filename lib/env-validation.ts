import "server-only"

const requiredServerEnvVars = ["DATABASE_URL", "POSTGRES_URL", "CESIUM_ION_TOKEN"]

const optionalServerEnvVars = [
  "FLIGHTAWARE_API_KEY",
  "SORMAS_API_KEY",
  "WHO_AFRO_API_KEY",
  "CDC_API_KEY",
  "NPHCDA_API_KEY",
  "OPENWEATHER_API_KEY",
]

// These should only be used if explicitly needed and should be accessed through server-side routes
const optionalPublicEnvVars: string[] = []

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

  // Warn about optional variables
  const notConfigured: string[] = []
  for (const envVar of [...optionalServerEnvVars, ...optionalPublicEnvVars]) {
    if (!process.env[envVar]) {
      notConfigured.push(envVar)
    }
  }

  if (notConfigured.length > 0) {
    console.warn("[v0] Optional environment variables not configured:", notConfigured.join(", "))
  }
}
