import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


DOT_ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")

# Load environment variables from .env file
load_dotenv(dotenv_path=DOT_ENV_PATH)

# Base directory of the application

# Configuration class for the application
class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # ChromaDB settings
    CHROMA_PERSIST_DIRECTORY = os.environ.get('CHROMA_PERSIST_DIRECTORY') or os.path.join(BASE_DIR, '..', 'data', 'chroma')
    
    # Google API settings for Gemini
    GOOGLE_API_KEY = os.environ.get('GOOGLE_GENAI_API_KEY')

    MODEL = os.environ.get("GOOGLE_GENAI_MODEL")

    SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT")
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # CORS settings - allow frontend to access API
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')