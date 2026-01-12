# =====================================================
# DATABASE CONFIGURATION
# =====================================================
# This file contains all settings for database connection
# Supports both local development and production deployment

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Check if we're in production (Render provides DATABASE_URL)
if os.getenv('DATABASE_URL'):
    # Production: Use environment variable from Render
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Render uses postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Local Development: Use local PostgreSQL
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'hospital_db',
        'user': 'postgres',
        'password': 'smit2609'
    }
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Flask App Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'hospital-management-secret-key-2024')

# Session Settings
SESSION_TYPE = 'filesystem'
