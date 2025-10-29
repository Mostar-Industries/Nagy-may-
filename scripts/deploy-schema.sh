#!/bin/bash
# scripts/deploy-schema.sh

echo "Deploying database schema..."

# Run the notes and paragraphs tables migration with RLS
psql $DATABASE_URL -f sql/01-schema-setup.sql

# Verify tables were created
TABLES=$(psql $DATABASE_URL -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
echo "Created tables:"
echo "$TABLES"

# Verify RLS policies
POLICIES=$(psql $DATABASE_URL -t -c "SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';")
echo "Row-Level Security policies:"
echo "$POLICIES"

echo "Schema deployment complete."
