#!/usr/bin/env python3
"""
Real Neon PostgreSQL setup and schema creation script
Run this after creating your Neon database
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def setup_neon():
    """Setup Neon database schema and test connection"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Set it with: export DATABASE_URL=postgresql://user:pass@host:5432/dbname")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Connected to Neon PostgreSQL")
        
        # Create schema
        schema_sql = """
        -- Create MNTRK schema
        CREATE SCHEMA IF NOT EXISTS mntrk;
        
        -- Ecological training data table
        CREATE TABLE IF NOT EXISTS mntrk.ecological_training_data (
            id SERIAL PRIMARY KEY,
            temperature FLOAT,
            humidity FLOAT,
            rainfall FLOAT,
            vegetation_index FLOAT,
            soil_moisture FLOAT,
            outbreak_risk INTEGER,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            data_source VARCHAR(100) DEFAULT 'manual',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Detection patterns table
        CREATE TABLE IF NOT EXISTS mntrk.detection_patterns (
            id SERIAL PRIMARY KEY,
            latitude DECIMAL(10, 8) NOT NULL,
            longitude DECIMAL(11, 8) NOT NULL,
            detection_timestamp TIMESTAMPTZ NOT NULL,
            confidence_score DECIMAL(5, 4),
            detection_method VARCHAR(50),
            image_url TEXT,
            environmental_context JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Model training history
        CREATE TABLE IF NOT EXISTS mntrk.model_training_history (
            id SERIAL PRIMARY KEY,
            model_type VARCHAR(50) NOT NULL,
            training_timestamp TIMESTAMPTZ DEFAULT NOW(),
            accuracy DECIMAL(5, 4),
            precision_score DECIMAL(5, 4),
            recall_score DECIMAL(5, 4),
            f1_score DECIMAL(5, 4),
            model_path TEXT,
            training_data_count INTEGER,
            hyperparameters JSONB
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_ecological_timestamp ON mntrk.ecological_training_data(timestamp);
        CREATE INDEX IF NOT EXISTS idx_detection_location ON mntrk.detection_patterns(latitude, longitude);
        CREATE INDEX IF NOT EXISTS idx_model_training_type ON mntrk.model_training_history(model_type);
        """
        
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ MNTRK database schema created successfully")
        
        # Insert test data
        test_data_sql = """
        INSERT INTO mntrk.ecological_training_data 
        (temperature, humidity, rainfall, vegetation_index, soil_moisture, outbreak_risk, latitude, longitude)
        VALUES 
        (25.5, 65.2, 120.0, 0.75, 45.3, 0, -11.2027, 17.8739),
        (28.1, 70.8, 95.5, 0.68, 38.7, 1, -11.2050, 17.8750),
        (26.3, 68.1, 110.2, 0.72, 42.1, 0, -11.2035, 17.8745)
        ON CONFLICT DO NOTHING;
        """
        
        cursor.execute(test_data_sql)
        conn.commit()
        print("✅ Test data inserted")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) as count FROM mntrk.ecological_training_data;")
        result = cursor.fetchone()
        print(f"✅ Database contains {result['count']} training records")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Neon setup failed: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ NEON POSTGRESQL SETUP AND SCHEMA CREATION")
    print("=" * 50)
    
    if setup_neon():
        print("✅ Neon PostgreSQL is ready for MNTRK deployment")
    else:
        print("❌ Neon setup failed - fix issues before proceeding")
        sys.exit(1)
