// lib/services/sormas-service.ts

import { API_ENDPOINTS, ApiError, ApiResponse } from '@/lib/api-integration';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL || '');

export interface SormasCase {
  uuid: string;
  disease: string;
  reportDate: string;
  region: string;
  district: string;
  age: number;
  sex: string;
  outcome: string;
  classification: string;
}

export async function fetchSormasCases(params: Record<string, string> = {}): Promise<ApiResponse<SormasCase[]>> {
  try {
    const baseUrl = API_ENDPOINTS.SORMAS.base;
    const endpoint = API_ENDPOINTS.SORMAS.cases;
    const url = new URL(`${baseUrl}${endpoint}`);
    
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
    
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${process.env.SORMAS_API_KEY || ''}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new ApiError(`SORMAS API error: ${response.statusText}`, response.status);
    }
    
    const data = await response.json();
    
    // Store in database
    await storeSormasData(data);
    
    return {
      data: data,
      meta: {
        total: data.length
      }
    };
  } catch (error) {
    console.error('SORMAS API error:', error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Failed to fetch SORMAS data', 500);
  }
}

async function storeSormasData(data: any) {
  try {
    await sql`
      INSERT INTO external_data (source, data, region, data_type)
      VALUES ('SORMAS', ${JSON.stringify(data)}, 'Nigeria', 'cases')
    `;
  } catch (dbError) {
    console.error('Failed to store SORMAS data:', dbError);
  }
}
