export const API_ENDPOINTS = {
  SORMAS: {
    base: process.env.SORMAS_API_URL || "https://sormas.org/api",
    cases: "/cases",
    contacts: "/contacts",
    events: "/events",
  },
  WHO_AFRO: {
    base: process.env.WHO_AFRO_API_URL || "https://dataportal.afro.who.int/api",
    data: "/data",
    indicators: "/indicators",
  },
  CDC: {
    base: process.env.CDC_API_URL || "https://api.cdc.gov",
    outbreaks: "/outbreaks",
    events: "/events",
  },
  NPHCDA: {
    base: process.env.NPHCDA_API_URL || "https://api.nphcda.gov.ng",
    facilities: "/facilities",
    reports: "/reports",
  },
}

export function isAPIAvailable(apiName: "SORMAS" | "WHO_AFRO" | "CDC" | "NPHCDA"): boolean {
  const keyMap = {
    SORMAS: "SORMAS_API_KEY",
    WHO_AFRO: "WHO_AFRO_API_KEY",
    CDC: "CDC_API_KEY",
    NPHCDA: "NPHCDA_API_KEY",
  }
  return !!process.env[keyMap[apiName]]
}

function getAPIKey(apiName: "SORMAS" | "WHO_AFRO" | "CDC" | "NPHCDA"): string | null {
  const keyMap = {
    SORMAS: "SORMAS_API_KEY",
    WHO_AFRO: "WHO_AFRO_API_KEY",
    CDC: "CDC_API_KEY",
    NPHCDA: "NPHCDA_API_KEY",
  }
  return process.env[keyMap[apiName]] || null
}

export async function fetchFromSORMAS(endpoint: string, options?: RequestInit) {
  const key = getAPIKey("SORMAS")
  if (!key) {
    console.warn("[v0] SORMAS API key not configured")
    return { error: "SORMAS API not configured", data: [] }
  }

  const url = `${API_ENDPOINTS.SORMAS.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
    ...options?.headers,
  }

  try {
    const response = await fetch(url, { ...options, headers })
    if (!response.ok) throw new Error(`SORMAS API error: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    console.error("[v0] SORMAS API error:", error)
    throw error
  }
}

export async function fetchFromWHOAFRO(endpoint: string, options?: RequestInit) {
  const key = getAPIKey("WHO_AFRO")
  if (!key) {
    console.warn("[v0] WHO AFRO API key not configured")
    return { error: "WHO AFRO API not configured", data: [] }
  }

  const url = `${API_ENDPOINTS.WHO_AFRO.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
    ...options?.headers,
  }

  try {
    const response = await fetch(url, { ...options, headers })
    if (!response.ok) throw new Error(`WHO AFRO API error: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    console.error("[v0] WHO AFRO API error:", error)
    throw error
  }
}

export async function fetchFromCDC(endpoint: string, options?: RequestInit) {
  const key = getAPIKey("CDC")
  if (!key) {
    console.warn("[v0] CDC API key not configured")
    return { error: "CDC API not configured", data: [] }
  }

  const url = `${API_ENDPOINTS.CDC.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
    ...options?.headers,
  }

  try {
    const response = await fetch(url, { ...options, headers })
    if (!response.ok) throw new Error(`CDC API error: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    console.error("[v0] CDC API error:", error)
    throw error
  }
}

export async function fetchFromNPHCDA(endpoint: string, options?: RequestInit) {
  const key = getAPIKey("NPHCDA")
  if (!key) {
    console.warn("[v0] NPHCDA API key not configured")
    return { error: "NPHCDA API not configured", data: [] }
  }

  const url = `${API_ENDPOINTS.NPHCDA.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
    ...options?.headers,
  }

  try {
    const response = await fetch(url, { ...options, headers })
    if (!response.ok) throw new Error(`NPHCDA API error: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    console.error("[v0] NPHCDA API error:", error)
    throw error
  }
}
