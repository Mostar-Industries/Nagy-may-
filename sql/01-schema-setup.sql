-- sql/01-schema-setup.sql

-- Notes table with RLS
CREATE TABLE IF NOT EXISTS notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  user_id TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  location GEOGRAPHY(POINT),
  tags TEXT[]
);

-- Paragraphs table with RLS
CREATE TABLE IF NOT EXISTS paragraphs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  sequence_number INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- External data table for API integrations
CREATE TABLE IF NOT EXISTS external_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,
  data JSONB NOT NULL,
  fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed BOOLEAN DEFAULT FALSE,
  region TEXT,
  data_type TEXT
);

-- Sightings table for Mastomys tracking
CREATE TABLE IF NOT EXISTS sightings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location GEOGRAPHY(POINT) NOT NULL,
  reported_by TEXT NOT NULL,
  reported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  confirmed BOOLEAN DEFAULT FALSE,
  risk_score DECIMAL,
  notes TEXT,
  images TEXT[],
  weather_conditions JSONB
);

-- Enable Row-Level Security
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE paragraphs ENABLE ROW LEVEL SECURITY;
ALTER TABLE external_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE sightings ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY notes_user_access ON notes
  USING (user_id = current_setting('app.current_user_id', TRUE));

CREATE POLICY paragraphs_note_access ON paragraphs
  USING (note_id IN (SELECT id FROM notes WHERE user_id = current_setting('app.current_user_id', TRUE)));

CREATE POLICY external_data_access ON external_data
  USING (TRUE);

CREATE POLICY sightings_access ON sightings
  USING (reported_by = current_setting('app.current_user_id', TRUE) OR 
         current_setting('app.user_role', TRUE) = 'admin');

-- Create indexes for performance
CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_paragraphs_note_id ON paragraphs(note_id);
CREATE INDEX idx_sightings_location ON sightings USING GIST(location);
CREATE INDEX idx_external_data_source ON external_data(source, fetched_at);
