// lib/api-integration/index.ts

export const API_ENDPOINTS = {
  SORMAS: {
    base: process.env.NCDC_SORMAS_API_URL || 'https://sormas.org.ng/api',
    cases: '/cases',
    outbreaks: '/outbreaks',
    contacts: '/contacts'
  },
  WHO_AFRO: {
    base: process.env.WHO_AFRO_DATA_URL || 'https://apps.who.int/gho/athena/api/AFRO',
    data: '/data',
    metadata: '/metadata'
  },
  CDC: {
    base: process.env.CDC_DATA_URL || 'https://data.cdc.gov/resource',
    diseases: '/diseases',
    outbreaks: '/outbreaks'
  },
  NPHCDA: {
    base: process.env.NPHCDA_DATA_URL || 'https://nphcda.gov.ng/api',
    facilities: '/facilities',
    vaccinations: '/vaccinations'
  }
};

export interface ApiResponse<T> {
  data: T;
  meta?: {
    page?: number;
    pageSize?: number;
    total?: number;
  };
  error?: string;
}

export class ApiError extends Error {
  statusCode: number;
  
  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.name = 'ApiError';
  }
}
