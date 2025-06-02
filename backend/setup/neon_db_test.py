#!/usr/bin/env python3
"""
REAL Neon PostgreSQL connection test
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_neon_connection():
    """Test REAL Neon PostgreSQL connection."""
    print("🗄️ Testing Neon PostgreSQL connection...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Set it with: export DATABASE_URL=postgresql://user:pass@host/dbname")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test query
        cursor.execute("SELECT current_database() as db, current_timestamp as time;")
        result = cursor.fetchone()
        
        print(f"✅ Connected to Neon database: {result['db']}")
        print(f"✅ Server time: {result['time']}")
        
        # Check for mntrk schema
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'mntrk';")
        if cursor.fetchone():
            print("✅ MNTRK schema exists")
        else:
            print("⚠️ MNTRK schema does not exist - will create it")
            
            # Create schema
            cursor.execute("CREATE SCHEMA IF NOT EXISTS mntrk;")
            conn.commit()
            print("✅ MNTRK schema created")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Neon connection test failed: {e}")
        return False

def main():
    """Run Neon database test."""
    print("🛡️ MNTRK Sovereign Grid - Neon Database Connection Test")
    print("=" * 50)
    
    # Run test
    if test_neon_connection():
        print("\n🗄️ NEON DATABASE CONNECTION SUCCESSFUL - SOVEREIGN GRID READY")
        return True
    else:
        print("\n❌ NEON DATABASE CONNECTION FAILED - CHECK CONFIGURATION")
        return False

if __name__ == "__main__":
    main()
