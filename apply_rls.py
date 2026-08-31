import os
import psycopg2
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Try loading from both possible env files
load_dotenv('backend/.env')
load_dotenv('.env')

def apply_rls_policy():
    conn_string = os.getenv('SUPABASE_POSTGRES_URL')
    
    if not conn_string:
        print("❌ SUPABASE_POSTGRES_URL not found in .env")
        return

    print("Parsing connection string...")
    # Strip supa parameter which psycopg2 doesn't like
    if "?" in conn_string:
        clean_conn_string = conn_string.split("?")[0]
    else:
        clean_conn_string = conn_string

    print(f"Connecting to Supabase Postgres (Cleaned DSN)...")
    
    try:
        # Use a more explicit connection if possible
        result = urlparse(conn_string)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port

        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode='require'
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("Checking if policy exists...")
        cur.execute("""
            SELECT count(*) FROM pg_policies 
            WHERE tablename = 'detection_patterns' AND policyname = 'Allow read for anon users';
        """)
        exists = cur.fetchone()[0] > 0

        if not exists:
            print("Applying 'Allow read for anon users' policy to 'detection_patterns'...")
            cur.execute("""
                CREATE POLICY "Allow read for anon users"
                ON detection_patterns
                FOR SELECT
                TO anon
                USING (true);
            """)
            print("✅ Policy applied successfully.")
        else:
            print("ℹ️ Policy 'Allow read for anon users' already exists.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error applying policy: {e}")

if __name__ == "__main__":
    apply_rls_policy()
