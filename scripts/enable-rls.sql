-- Enable Row Level Security on detection_patterns table
ALTER TABLE detection_patterns ENABLE ROW LEVEL SECURITY;

-- Policy: Allow authenticated users to read all detections
CREATE POLICY "Users can view all detections"
ON detection_patterns FOR SELECT
TO authenticated
USING (true);

-- Policy: Allow authenticated users to insert their own detections
CREATE POLICY "Users can create detections"
ON detection_patterns FOR INSERT
TO authenticated
WITH CHECK (true);

-- Policy: Allow service role full access
CREATE POLICY "Service role has full access to detections"
ON detection_patterns
TO service_role
USING (true)
WITH CHECK (true);

-- Enable RLS on users_sync table
ALTER TABLE neon_auth.users_sync ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own profile
CREATE POLICY "Users can view own profile"
ON neon_auth.users_sync FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- Policy: Service role full access to users
CREATE POLICY "Service role has full access to users"
ON neon_auth.users_sync
TO service_role
USING (true)
WITH CHECK (true);
