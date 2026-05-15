import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
# Load environment variables from .env at project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

def get_engine():
    """Create a SQLAlchemy engine connected to the analytics PostgreSQL database."""
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    dbname = os.getenv('DB_NAME', 'analytics')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'password')
    connection_string = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    return create_engine(connection_string)

def get_connection():
    """Get a raw psycopg2 connection for direct SQL execution."""
    import psycopg2
    return psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    dbname=os.getenv('DB_NAME', 'analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'password')
    )