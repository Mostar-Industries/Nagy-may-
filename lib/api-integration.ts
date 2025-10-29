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

export async function fetchFromSORMAS(endpoint: string, options?: RequestInit) {
  const url = `${API_ENDPOINTS.SORMAS.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${process.env.SORMAS_API_KEY}`,
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
  const url = `${API_ENDPOINTS.WHO_AFRO.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${process.env.WHO_AFRO_API_KEY}`,
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
  const url = `${API_ENDPOINTS.CDC.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${process.env.CDC_API_KEY}`,
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
  const url = `${API_ENDPOINTS.NPHCDA.base}${endpoint}`
  const headers = {
    Authorization: `Bearer ${process.env.NPHCDA_API_KEY}`,
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
