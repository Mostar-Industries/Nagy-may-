// lib/services/who-afro-service.ts

import { API_ENDPOINTS, ApiError, ApiResponse } from '@/lib/api-integration';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL || '');

export interface WhoAfroData {
  indicator: string;
  region: string;
  year: number;
  value: number;
}

export async function fetchWhoAfroData(indicator: string, region: string): Promise<ApiResponse<WhoAfroData[]>> {
  const baseUrl = API_ENDPOINTS.WHO_AFRO.base;
  const url = `${baseUrl}${API_ENDPOINTS.WHO_AFRO.data}?indicator=${indicator}&region=${region}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new ApiError(`WHO AFRO API error: ${response.statusText}`, response.status);
    }

    const data = await response.json();

    // Store in database
    await storeWhoAfroData(data, region, indicator);

    return { data };
  } catch (error) {
    console.error('WHO AFRO API error:', error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Failed to fetch WHO AFRO data', 500);
  }
}

async function storeWhoAfroData(data: any, region: string, dataType: string) {
  try {
    await sql`
      INSERT INTO external_data (source, data, region, data_type)
      VALUES ('WHO_AFRO', ${JSON.stringify(data)}, ${region}, ${dataType})
    `;
  } catch (dbError) {
    console.error('Failed to store WHO AFRO data:', dbError);
  }
}
