-- Supabase schema for automated detections
-- Run this in your Supabase SQL editor

CREATE TABLE IF NOT EXISTS detection_patterns (
  id BIGSERIAL PRIMARY KEY,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  detection_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  detection_count INTEGER NOT NULL DEFAULT 0,
  source TEXT,
  environmental_context JSONB,
  risk_assessment JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for realtime queries
CREATE INDEX idx_detection_timestamp ON detection_patterns(detection_timestamp DESC);
CREATE INDEX idx_detection_source ON detection_patterns(source);

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE detection_patterns;

-- RLS policies (adjust for your auth setup)
ALTER TABLE detection_patterns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role"
  ON detection_patterns
  FOR ALL
  TO service_role
  USING (true);

CREATE POLICY "Allow read for authenticated users"
  ON detection_patterns
  FOR SELECT
  TO authenticated
  USING (true);
