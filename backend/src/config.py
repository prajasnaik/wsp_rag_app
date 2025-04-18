import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuration class for the application
class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # ChromaDB settings
    CHROMA_PERSIST_DIRECTORY = os.environ.get('CHROMA_PERSIST_DIRECTORY') or os.path.join(BASE_DIR, '..', 'data', 'chroma')
    
    # Google API settings for Gemini
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # CORS settings - allow frontend to access API
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')