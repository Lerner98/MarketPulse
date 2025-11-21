"""
Setup CBS database schema using raw psycopg2 connection.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Read schema file
schema_file = Path(__file__).parent / 'models' / 'schema_cbs.sql'

print(f"Reading schema from: {schema_file}")

with open(schema_file, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

print("Executing schema...")

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
# postgresql://user:pass@host:port/dbname
parts = db_url.replace('postgresql://', '').split('@')
user_pass = parts[0].split(':')
host_port_db = parts[1].split('/')
host, port = host_port_db[0].split(':')
dbname = host_port_db[1]

# Connect with raw psycopg2 and execute schema
conn = psycopg2.connect(
    dbname=dbname,
    user=user_pass[0],
    password=user_pass[1],
    host=host,
    port=port
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute(schema_sql)

conn.close()

print("✓ Schema executed successfully!")
