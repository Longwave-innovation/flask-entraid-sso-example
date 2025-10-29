import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(16)
    
    # Entra ID Configuration
    TENANT_ID = os.getenv('TENANT_ID')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    
    # App Configuration
    HOST = os.getenv('HOST', 'http://localhost')
    PORT = int(os.getenv('PORT', 8080))
    CALLBACK_PATH = os.getenv('CALLBACK_PATH', '/login/callback')
    LOGIN_PATH = os.getenv('LOGIN_PATH', '/login')
    
    # Computed URIs
    REDIRECT_URI = f"{HOST}:{PORT}{CALLBACK_PATH}"
    LOGOUT_URI = f"{HOST}:{PORT}/"