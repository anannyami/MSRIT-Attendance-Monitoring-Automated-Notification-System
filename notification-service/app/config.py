import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# Brevo API (replaces SMTP — works on all cloud platforms, no domain verification needed)
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
ALERT_SENDER  = os.getenv("ALERT_SENDER", "")

# Database
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "msrit_attendance")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# URL-encode password to safely handle special characters like @
_db_password_escaped = quote_plus(DB_PASSWORD)
_db_ssl    = os.getenv("DB_SSL", "")
_ssl_suffix = "?sslmode=require" if _db_ssl else ""
DATABASE_URL = f"postgresql://{DB_USER}:{_db_password_escaped}@{DB_HOST}:{DB_PORT}/{DB_NAME}{_ssl_suffix}"

# Service
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8001))
