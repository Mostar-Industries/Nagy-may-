// lib/services/data-sync.ts
import { neon } from "@neondatabase/serverless";
import { fetchSormasCases } from './sormas-service';
import { fetchWhoAfroData } from './who-afro-service';
// Import other services when they are implemented
// import { fetchCdcData } from './cdc-service';
// import { fetchNphcdaData } from './nphcda-service';

const sql = neon(process.env.DATABASE_URL || "");

export async function syncExternalData() {
  try {
    // Fetch data from various sources
    const sormasData = await fetchSormasCases({ limit: '100' });
    const whoData = await fetchWhoAfroData('lassa_fever', 'nigeria');
    // Fetch other data
    
    // Processing and storing is handled within each service now.
    // You could add additional cross-service logic here if needed.
    
    // Log successful sync
    console.log('Data synchronization completed successfully');
    return { success: true };
  } catch (error) {
    console.error('Data sync failed:', error);
    return { success: false, error };
  }
}
