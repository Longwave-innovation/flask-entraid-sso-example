import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(16)
    
    # Auth Provider Selection: 'entraid' or 'cognito'
    AUTH_PROVIDER = os.getenv('AUTH_PROVIDER', 'entraid').lower()
    
    # Common to both providers
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    
    # Entra ID Configuration
    TENANT_ID = os.getenv('TENANT_ID')
    
    # AWS Cognito Configuration
    _cognito_domain = os.getenv('COGNITO_DOMAIN', '')  # e.g., https://your-domain.auth.region.amazoncognito.com
    # Ensure COGNITO_DOMAIN has protocol
    COGNITO_DOMAIN = _cognito_domain if _cognito_domain.startswith(('http://', 'https://')) else f"https://{_cognito_domain}" if _cognito_domain else None
    COGNITO_REGION = os.getenv('COGNITO_REGION', 'eu-south-1')
    
    # App Configuration
    HOST = os.getenv('HOST', 'http://localhost')
    PORT = int(os.getenv('PORT', 8080))
    CALLBACK_PATH = os.getenv('CALLBACK_PATH', '/login/callback')
    LOGIN_PATH = os.getenv('LOGIN_PATH', '/login')
    
    # Computed URIs
    REDIRECT_URI = f"{HOST}:{PORT}{CALLBACK_PATH}"
    LOGOUT_URI = f"{HOST}:{PORT}/"
