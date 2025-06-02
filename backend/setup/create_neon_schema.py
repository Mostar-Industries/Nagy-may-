#!/usr/bin/env python3
"""
Create REAL Neon PostgreSQL schema for MNTRK Sovereign Grid
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

schema_sql = """
CREATE TABLE IF NOT EXISTS ecological_training_data (
    id SERIAL PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    rainfall FLOAT,
    vegetation_index FLOAT,
    soil_moisture FLOAT,
    outbreak_risk INT,
    timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_registry (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50),
    model_type VARCHAR(50),
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    loss FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);
"""

def create_schema():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Neon schema successfully created.")
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_mntrk_schema():
    """Create complete MNTRK database schema in Neon PostgreSQL."""
    print("🗄️ Creating MNTRK Sovereign Grid schema in Neon...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create schema
        print("📁 Creating mntrk schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS mntrk;")
        
        # Create detection_patterns table
        print("🔎 Creating detection_patterns table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mntrk.detection_patterns (
                id SERIAL PRIMARY KEY,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                detection_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                confidence_score DECIMAL(5, 4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
                detection_method VARCHAR(50) NOT NULL,
                image_url TEXT,
                environmental_context JSONB,
                risk_level VARCHAR(20) DEFAULT 'low',
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create habitat_analyses table
        print("🌿 Creating habitat_analyses table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mntrk.habitat_analyses (
                id SERIAL PRIMARY KEY,
                region_name VARCHAR(255),
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                suitability_score DECIMAL(5, 4) CHECK (suitability_score >= 0 AND suitability_score <= 1),
                analysis_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                satellite_image_url TEXT,
                environmental_data JSONB,
                risk_factors TEXT[],
                analysis_parameters JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create training_data table
        print("🧠 Creating training_data table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mntrk.training_data (
                id SERIAL PRIMARY KEY,
                temperature DECIMAL(5, 2),
                humidity DECIMAL(5, 2),
                rainfall DECIMAL(7, 2),
                vegetation_index DECIMAL(5, 4),
                soil_moisture DECIMAL(5, 2),
                elevation DECIMAL(8, 2),
                outbreak_risk INTEGER CHECK (outbreak_risk >= 0 AND outbreak_risk <= 1),
                data_source VARCHAR(100),
                collection_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create model_registry table
        print("📊 Creating model_registry table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mntrk.model_registry (
                id SERIAL PRIMARY KEY,
                model_id VARCHAR(100) UNIQUE NOT NULL,
                model_type VARCHAR(50) NOT NULL,
                model_version VARCHAR(20) DEFAULT '1.0',
                accuracy DECIMAL(5, 4),
                precision_score DECIMAL(5, 4),
                recall_score DECIMAL(5, 4),
                f1_score DECIMAL(5, 4),
                training_data_count INTEGER,
                hyperparameters JSONB,
                storage_path TEXT,
                training_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create environmental_data table
        print("🌍 Creating environmental_data table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mntrk.environmental_data (
                id SERIAL PRIMARY KEY,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                measurement_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                temperature DECIMAL(5, 2),
                rainfall DECIMAL(7, 2),
                humidity DECIMAL(5, 2),
                vegetation_index DECIMAL(5, 4),
                soil_moisture DECIMAL(5, 2),
                elevation DECIMAL(8, 2),
                data_source VARCHAR(100),
                raw_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create outbreak_alerts table
        print("⚠️ Creating outbreak_alerts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mntrk.outbreak_alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(50) NOT NULL,
                severity_level INTEGER CHECK (severity_level >= 1 AND severity_level <= 5),
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                radius_km DECIMAL(8, 2),
                description TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                alert_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                resolved_timestamp TIMESTAMP WITH TIME ZONE,
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create indexes for performance
        print("🚀 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_detection_patterns_location ON mntrk.detection_patterns(latitude, longitude);",
            "CREATE INDEX IF NOT EXISTS idx_detection_patterns_timestamp ON mntrk.detection_patterns(detection_timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_habitat_analyses_location ON mntrk.habitat_analyses(latitude, longitude);",
            "CREATE INDEX IF NOT EXISTS idx_training_data_date ON mntrk.training_data(collection_date);",
            "CREATE INDEX IF NOT EXISTS idx_environmental_data_location ON mntrk.environmental_data(latitude, longitude);",
            "CREATE INDEX IF NOT EXISTS idx_environmental_data_timestamp ON mntrk.environmental_data(measurement_timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_outbreak_alerts_location ON mntrk.outbreak_alerts(latitude, longitude);",
            "CREATE INDEX IF NOT EXISTS idx_outbreak_alerts_status ON mntrk.outbreak_alerts(status);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Insert sample data
        print("📝 Inserting sample data...")
        cursor.execute("""
            INSERT INTO mntrk.training_data (temperature, humidity, rainfall, vegetation_index, soil_moisture, outbreak_risk, data_source)
            VALUES 
                (28.5, 75.2, 1200, 0.65, 45.3, 1, 'field_survey'),
                (30.1, 68.7, 800, 0.45, 32.1, 0, 'satellite_data'),
                (26.8, 82.3, 1500, 0.78, 52.7, 1, 'weather_station'),
                (29.2, 71.5, 950, 0.58, 38.9, 0, 'field_survey'),
                (31.0, 65.2, 600, 0.35, 28.4, 0, 'satellite_data')
            ON CONFLICT DO NOTHING;
        """)
        
        # Commit all changes
        conn.commit()
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'mntrk'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Created {len(tables)} tables in mntrk schema:")
        for table in tables:
            print(f"   📋 {table[0]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🛡️ MNTRK SOVEREIGN GRID SCHEMA CREATED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False

def main():
    """Run schema creation."""
    print("🛡️ MNTRK Sovereign Grid - Neon Schema Creation")
    print("=" * 50)
    
    if create_mntrk_schema():
        print("\n🗄️ NEON DATABASE SCHEMA READY - SOVEREIGN GRID OPERATIONAL")
        return True
    else:
        print("\n❌ SCHEMA CREATION FAILED - CHECK CONFIGURATION")
        return False

    create_schema()

if __name__ == "__main__":
    main()
