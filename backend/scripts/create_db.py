import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "123456")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
target_db = os.getenv("POSTGRES_DB", "dau_second_brain")

def create_database():
    print(f"Connecting to PostgreSQL server at {host}:{port} as user '{user}'...")
    try:
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if target database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (target_db,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{target_db}' does not exist. Creating now...")
            cursor.execute(f'CREATE DATABASE "{target_db}";')
            print(f"Database '{target_db}' created successfully!")
        else:
            print(f"Database '{target_db}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        raise e

if __name__ == "__main__":
    create_database()
