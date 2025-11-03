-- Create detections table for storing YOLO inference results
-- Run this in your Neon database console

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create detections table
CREATE TABLE IF NOT EXISTS detections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  image_id TEXT NOT NULL,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  bbox JSONB NOT NULL,
  confidence DECIMAL(5, 4) NOT NULL,
  label TEXT NOT NULL,
  species TEXT,
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  source TEXT NOT NULL DEFAULT 'unknown',
  processing_time_ms INTEGER,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_detections_detected_at ON detections(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_detections_image_id ON detections(image_id);
CREATE INDEX IF NOT EXISTS idx_detections_species ON detections(species);
CREATE INDEX IF NOT EXISTS idx_detections_location ON detections(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_detections_confidence ON detections(confidence DESC);

-- Create a view for latest detections
CREATE OR REPLACE VIEW latest_detections AS
SELECT 
  id,
  image_id,
  latitude,
  longitude,
  bbox,
  confidence,
  label,
  species,
  detected_at,
  source,
  processing_time_ms,
  metadata
FROM detections
ORDER BY detected_at DESC
LIMIT 100;

-- Grant appropriate permissions
-- GRANT SELECT, INSERT ON detections TO your_app_user;
-- GRANT SELECT ON latest_detections TO your_app_user;

COMMENT ON TABLE detections IS 'YOLO detection results for Mastomys tracking';
COMMENT ON COLUMN detections.bbox IS 'Bounding box coordinates as JSON: {x, y, width, height}';
COMMENT ON COLUMN detections.confidence IS 'Detection confidence score (0-1)';
COMMENT ON COLUMN detections.species IS 'Detected species name';
