-- Enhanced detection schema with deep details
-- Run this to upgrade your detection system

-- Drop existing views
DROP VIEW IF EXISTS latest_detections;

-- Add new columns to detections table
ALTER TABLE detections 
  ADD COLUMN IF NOT EXISTS detection_type VARCHAR(50) DEFAULT 'single',
  ADD COLUMN IF NOT EXISTS colony_id UUID,
  ADD COLUMN IF NOT EXISTS colony_size INTEGER,
  ADD COLUMN IF NOT EXISTS gender VARCHAR(20),
  ADD COLUMN IF NOT EXISTS age_estimate VARCHAR(30),
  ADD COLUMN IF NOT EXISTS health_status VARCHAR(50),
  ADD COLUMN IF NOT EXISTS behavior_tags TEXT[],
  ADD COLUMN IF NOT EXISTS environment_type VARCHAR(100),
  ADD COLUMN IF NOT EXISTS threat_level INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS tracking_status VARCHAR(30) DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP WITH TIME ZONE,
  ADD COLUMN IF NOT EXISTS movement_pattern JSONB,
  ADD COLUMN IF NOT EXISTS physical_attributes JSONB,
  ADD COLUMN IF NOT EXISTS habitat_data JSONB;

-- Create colonies table for group tracking
CREATE TABLE IF NOT EXISTS colonies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  colony_name VARCHAR(255),
  location_center GEOGRAPHY(POINT),
  radius_meters INTEGER,
  estimated_population INTEGER,
  species VARCHAR(100),
  dominant_gender VARCHAR(20),
  establishment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status VARCHAR(50) DEFAULT 'active',
  threat_level INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create detection_events for detailed tracking history
CREATE TABLE IF NOT EXISTS detection_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  detection_id UUID REFERENCES detections(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  event_data JSONB,
  severity VARCHAR(20) DEFAULT 'info',
  notes TEXT,
  created_by VARCHAR(100)
);

-- Create tracking_sessions for continuous monitoring
CREATE TABLE IF NOT EXISTS tracking_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_name VARCHAR(255),
  start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  end_time TIMESTAMP WITH TIME ZONE,
  location_bounds JSONB,
  total_detections INTEGER DEFAULT 0,
  species_breakdown JSONB,
  status VARCHAR(50) DEFAULT 'active',
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Enhanced indexes
CREATE INDEX IF NOT EXISTS idx_detections_type ON detections(detection_type);
CREATE INDEX IF NOT EXISTS idx_detections_colony ON detections(colony_id);
CREATE INDEX IF NOT EXISTS idx_detections_gender ON detections(gender);
CREATE INDEX IF NOT EXISTS idx_detections_threat ON detections(threat_level DESC);
CREATE INDEX IF NOT EXISTS idx_detections_tracking_status ON detections(tracking_status);
CREATE INDEX IF NOT EXISTS idx_colonies_species ON colonies(species);
CREATE INDEX IF NOT EXISTS idx_colonies_status ON colonies(status);
CREATE INDEX IF NOT EXISTS idx_detection_events_type ON detection_events(event_type);
CREATE INDEX IF NOT EXISTS idx_detection_events_timestamp ON detection_events(event_timestamp DESC);

-- Create materialized view for real-time analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS detection_analytics AS
SELECT 
  DATE_TRUNC('hour', detected_at) as time_bucket,
  species,
  detection_type,
  gender,
  COUNT(*) as detection_count,
  AVG(confidence) as avg_confidence,
  AVG(threat_level) as avg_threat,
  ARRAY_AGG(DISTINCT environment_type) as environments,
  COUNT(DISTINCT colony_id) as unique_colonies
FROM detections
WHERE detected_at > NOW() - INTERVAL '7 days'
GROUP BY time_bucket, species, detection_type, gender
ORDER BY time_bucket DESC;

CREATE INDEX IF NOT EXISTS idx_analytics_time ON detection_analytics(time_bucket DESC);

-- Create view for active tracking
CREATE OR REPLACE VIEW active_tracking AS
SELECT 
  d.id,
  d.image_id,
  d.species,
  d.detection_type,
  d.gender,
  d.age_estimate,
  d.colony_id,
  c.colony_name,
  d.confidence,
  d.threat_level,
  d.latitude,
  d.longitude,
  d.detected_at,
  d.last_seen,
  d.behavior_tags,
  d.tracking_status,
  d.physical_attributes,
  d.habitat_data
FROM detections d
LEFT JOIN colonies c ON d.colony_id = c.id
WHERE d.tracking_status = 'active'
ORDER BY d.detected_at DESC;

-- Create view for colony statistics
CREATE OR REPLACE VIEW colony_statistics AS
SELECT 
  c.id as colony_id,
  c.colony_name,
  c.species,
  c.estimated_population,
  c.threat_level,
  c.status,
  COUNT(d.id) as total_detections,
  COUNT(DISTINCT d.gender) as gender_diversity,
  AVG(d.confidence) as avg_confidence,
  MAX(d.detected_at) as last_detection,
  ARRAY_AGG(DISTINCT d.detection_type) as detection_types
FROM colonies c
LEFT JOIN detections d ON d.colony_id = c.id
GROUP BY c.id, c.colony_name, c.species, c.estimated_population, c.threat_level, c.status;

-- Function to automatically update colony last_activity
CREATE OR REPLACE FUNCTION update_colony_activity()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.colony_id IS NOT NULL THEN
    UPDATE colonies 
    SET last_activity = NEW.detected_at,
        updated_at = NOW()
    WHERE id = NEW.colony_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_colony_activity
  AFTER INSERT OR UPDATE ON detections
  FOR EACH ROW
  EXECUTE FUNCTION update_colony_activity();

-- Function to auto-assign detections to nearby colonies
CREATE OR REPLACE FUNCTION auto_assign_colony()
RETURNS TRIGGER AS $$
DECLARE
  nearby_colony UUID;
BEGIN
  IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
    SELECT id INTO nearby_colony
    FROM colonies
    WHERE status = 'active'
      AND species = NEW.species
      AND ST_DWithin(
        location_center::geography,
        ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography,
        radius_meters
      )
    ORDER BY ST_Distance(
      location_center::geography,
      ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography
    )
    LIMIT 1;
    
    IF nearby_colony IS NOT NULL THEN
      NEW.colony_id = nearby_colony;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_assign_colony
  BEFORE INSERT ON detections
  FOR EACH ROW
  EXECUTE FUNCTION auto_assign_colony();

-- Create function to refresh analytics
CREATE OR REPLACE FUNCTION refresh_detection_analytics()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY detection_analytics;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON COLUMN detections.detection_type IS 'Type: single, pair, group, colony, nest';
COMMENT ON COLUMN detections.gender IS 'Gender: male, female, unknown';
COMMENT ON COLUMN detections.age_estimate IS 'Age: juvenile, young_adult, adult, elderly';
COMMENT ON COLUMN detections.health_status IS 'Health: healthy, sick, injured, deceased';
COMMENT ON COLUMN detections.threat_level IS 'Threat level: 0-10 scale';
COMMENT ON TABLE colonies IS 'Tracked rodent colonies with population estimates';
COMMENT ON TABLE detection_events IS 'Event log for all detection-related activities';

-- Grant permissions (uncomment and adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON detections TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON colonies TO your_app_user;
-- GRANT SELECT, INSERT ON detection_events TO your_app_user;
-- GRANT SELECT ON active_tracking TO your_app_user;
-- GRANT SELECT ON colony_statistics TO your_app_user;
