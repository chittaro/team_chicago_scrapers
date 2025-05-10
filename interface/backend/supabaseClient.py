import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file in the backend directory
# Make sure your .env file is in interface/backend/
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL_ENV = os.getenv("BACKEND_SUPABASE_URL")
SUPABASE_SERVICE_KEY_ENV = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL_ENV or not SUPABASE_SERVICE_KEY_ENV:
    raise ValueError("BACKEND_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not set in the environment variables. Check your .env file in the interface/backend/ directory.")

# Initialize the Supabase client for the backend
supabase_backend: Client = create_client(SUPABASE_URL_ENV, SUPABASE_SERVICE_KEY_ENV) 