# Database Scripts

## Enable Row Level Security (RLS)

To enable RLS on your Supabase tables, run the SQL script:

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `enable-rls.sql`
4. Click "Run"

This will:
- Enable RLS on `detection_patterns` table
- Create policies for authenticated users to read/create detections
- Enable RLS on `users_sync` table
- Create policies for users to view their own profiles
- Grant service role full access for backend operations

## RLS Policies Created

### detection_patterns
- **Read**: All authenticated users can view all detections
- **Insert**: All authenticated users can create detections
- **Service Role**: Full access for backend operations

### neon_auth.users_sync
- **Read**: Users can only view their own profile
- **Service Role**: Full access for authentication operations

## Testing RLS

After enabling RLS, test the policies:

```sql
-- Test as authenticated user (should work)
SELECT * FROM detection_patterns;

-- Test as anon (should fail)
SET ROLE anon;
SELECT * FROM detection_patterns;
RESET ROLE;
