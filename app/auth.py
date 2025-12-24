import requests
import logging
from flask import current_app
from abc import ABC, abstractmethod

# ============================================================================
# Abstract Base Provider
# ============================================================================
class AuthProvider(ABC):
    @abstractmethod
    def get_auth_url(self):
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, code):
        pass
    
    @abstractmethod
    def get_user_info(self, access_token):
        pass
    
    @abstractmethod
    def get_user_groups(self, access_token):
        pass
    
    @abstractmethod
    def get_logout_url(self):
        pass

# ============================================================================
# Entra ID Provider
# ============================================================================
class EntraIDProvider(AuthProvider):
    def get_auth_url(self):
        c = current_app.config
        return (
            f"https://login.microsoftonline.com/{c['TENANT_ID']}/oauth2/v2.0/authorize?"
            f"client_id={c['CLIENT_ID']}&response_type=code&redirect_uri={c['REDIRECT_URI']}"
            f"&scope=openid profile email User.Read GroupMember.Read.All&response_mode=query"
        )
    
    def exchange_code_for_token(self, code):
        c = current_app.config
        token_url = f"https://login.microsoftonline.com/{c['TENANT_ID']}/oauth2/v2.0/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': c['CLIENT_ID'],
            'client_secret': c['CLIENT_SECRET'],
            'code': code,
            'redirect_uri': c['REDIRECT_URI']
        }
        response = requests.post(token_url, data=data)
        return response.json()
    
    def get_user_info(self, access_token):
        headers = {'Authorization': f"Bearer {access_token}"}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        return response.json()
    
    def get_user_groups(self, access_token):
        headers = {'Authorization': f"Bearer {access_token}"}
        response = requests.get('https://graph.microsoft.com/v1.0/me/memberOf', headers=headers)
        return response.json()
    
    def get_logout_url(self):
        c = current_app.config
        return (
            f"https://login.microsoftonline.com/{c['TENANT_ID']}/oauth2/v2.0/logout?"
            f"post_logout_redirect_uri={c['LOGOUT_URI']}"
        )

# ============================================================================
# AWS Cognito Provider
# ============================================================================
class CognitoProvider(AuthProvider):
    def get_auth_url(self):
        c = current_app.config
        return (
            f"{c['COGNITO_DOMAIN']}/oauth2/authorize?"
            f"client_id={c['CLIENT_ID']}&response_type=code&redirect_uri={c['REDIRECT_URI']}"
            f"&scope=openid profile email"
        )
    
    def exchange_code_for_token(self, code):
        c = current_app.config
        token_url = f"{c['COGNITO_DOMAIN']}/oauth2/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': c['CLIENT_ID'],
            'client_secret': c['CLIENT_SECRET'],
            'code': code,
            'redirect_uri': c['REDIRECT_URI']
        }
        response = requests.post(token_url, data=data)
        return response.json()
    
    def get_user_info(self, access_token):
        c = current_app.config
        headers = {'Authorization': f"Bearer {access_token}"}
        response = requests.get(f"{c['COGNITO_DOMAIN']}/oauth2/userInfo", headers=headers)
        return response.json()
    
    def get_user_groups(self, access_token):
        # Cognito groups are included in ID token claims, not separate endpoint
        # Return empty for now - groups should be extracted from ID token
        return {'value': []}
    
    def get_logout_url(self):
        c = current_app.config
        return (
            f"{c['COGNITO_DOMAIN']}/logout?"
            f"client_id={c['CLIENT_ID']}&logout_uri={c['LOGOUT_URI']}&redirect_uri={c['LOGOUT_URI']}"
        )

# ============================================================================
# Provider Factory
# ============================================================================
def get_provider() -> AuthProvider:
    """Get the configured auth provider"""
    provider = current_app.config['AUTH_PROVIDER']
    if provider == 'cognito':
        return CognitoProvider()
    elif provider == 'entraid':
        return EntraIDProvider()
    else:
        raise ValueError(f"Unknown auth provider: {provider}")

# ============================================================================
# Public API (backwards compatible)
# ============================================================================
def get_auth_url():
    return get_provider().get_auth_url()

def exchange_code_for_token(code):
    return get_provider().exchange_code_for_token(code)

def get_user_info(access_token):
    return get_provider().get_user_info(access_token)

def get_user_groups(access_token):
    return get_provider().get_user_groups(access_token)

def get_logout_url():
    return get_provider().get_logout_url()