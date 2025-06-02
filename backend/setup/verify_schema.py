#!/usr/bin/env python3
"""
Verify MNTRK schema was created correctly in Neon
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def verify_schema():
    """Verify all tables and data exist."""
    print("🔍 Verifying MNTRK schema...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check tables
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_schema = 'mntrk' AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'mntrk'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   ✅ {table['table_name']} ({table['column_count']} columns)")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) as count FROM mntrk.training_data;")
        training_count = cursor.fetchone()['count']
        print(f"📊 Training data records: {training_count}")
        
        # Test a sample query
        cursor.execute("""
            SELECT temperature, humidity, outbreak_risk 
            FROM mntrk.training_data 
            LIMIT 3;
        """)
        
        samples = cursor.fetchall()
        print("🧪 Sample training data:")
        for sample in samples:
            print(f"   🌡️ Temp: {sample['temperature']}°C, Humidity: {sample['humidity']}%, Risk: {sample['outbreak_risk']}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ SCHEMA VERIFICATION SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_schema()
