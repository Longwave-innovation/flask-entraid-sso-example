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
# OpenIdConnect Provider
# ============================================================================
class OpenIdConnectProvider(AuthProvider):
    """OIDC provider with automatic discovery via .well-known/openid-configuration
    
    Implements OpenID Connect Discovery 1.0 specification:
    https://openid.net/specs/openid-connect-discovery-1_0.html
    """
    
    def __init__(self):
        self._metadata = None
        self._discover_metadata()
    
    def _discover_metadata(self):
        """Fetch OIDC metadata from .well-known/openid-configuration endpoint"""
        if self._metadata:
            return self._metadata
        
        c = current_app.config
        issuer = c.get('OIDC_ISSUER')
        if not issuer:
            raise ValueError("OIDC_ISSUER must be configured for OIDC discovery")
        
        # Normalize issuer URL (remove trailing slash per RFC 8414 section 3)
        issuer = issuer.rstrip('/')
        discovery_url = f"{issuer}/.well-known/openid-configuration"
        
        try:
            logging.info(f"Discovering OIDC metadata from {discovery_url}")
            response = requests.get(discovery_url, timeout=10)
            response.raise_for_status()
            self._metadata = response.json()
            
            # Validate required endpoints per OIDC Discovery spec
            required = ['authorization_endpoint', 'token_endpoint', 'userinfo_endpoint', 'jwks_uri']
            missing = [k for k in required if k not in self._metadata]
            if missing:
                raise ValueError(f"OIDC metadata missing required fields: {missing}")
            
            logging.info("OIDC metadata discovered successfully")
            return self._metadata
        except requests.RequestException as e:
            logging.error(f"Failed to discover OIDC metadata: {e}")
            raise

    def get_auth_url(self):
        c = current_app.config
        # metadata = self._discover_metadata()
        return (
            f"{self._metadata['authorization_endpoint']}?"
            f"client_id={c['CLIENT_ID']}&response_type=code&redirect_uri={c['REDIRECT_URI']}"
            f"&scope={c.get('OIDC_SCOPES', 'openid profile email groups')}&response_mode=query"
        )
    
    def exchange_code_for_token(self, code):
        c = current_app.config
        # metadata = self._discover_metadata()
        data = {
            'grant_type': 'authorization_code',
            'client_id': c['CLIENT_ID'],
            'client_secret': c['CLIENT_SECRET'],
            'code': code,
            'redirect_uri': c['REDIRECT_URI']
        }
        response = requests.post(self._metadata['token_endpoint'], data=data)
        logging.info(f"Token exchange response: {response}")
        return response.json()
    
    def get_user_info(self, access_token):
        # metadata = self._discover_metadata()
        headers = {'Authorization': f"Bearer {access_token}"}
        response = requests.get(self._metadata['userinfo_endpoint'], headers=headers)
        return response.json()
    
    def get_user_groups(self, access_token):
        # Standard OIDC doesn't define a groups endpoint
        # Groups are typically included in ID token claims or userinfo response
        # So we are goind to get user info if groups is in the OIDC_SCOPES
        if "groups" in current_app.config.get('OIDC_SCOPES', ''):
            return self.get_user_info(access_token).get("groups", [])
        return {'value': []}
    
    def get_logout_url(self):
        c = current_app.config
        # metadata = self._discover_metadata()
        # end_session_endpoint is optional per OIDC RP-Initiated Logout spec
        logout_endpoint = self._metadata.get('end_session_endpoint')
        if logout_endpoint:
            return (
                f"{logout_endpoint}?"
                f"post_logout_redirect_uri={c['LOGOUT_URI']}"
                f"&client_id={c['CLIENT_ID']}"
            )
        return c['LOGOUT_URI']
    

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
            f"&scope={c.get('COGNITO_CLAIMS', 'openid profile email')}"
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
    elif provider == 'oidc':
        return OpenIdConnectProvider()
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