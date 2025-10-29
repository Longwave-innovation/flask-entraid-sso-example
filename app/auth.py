import requests
from flask import current_app

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = f"https://login.microsoftonline.com/{current_app.config['TENANT_ID']}/oauth2/v2.0/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': current_app.config['CLIENT_ID'],
        'client_secret': current_app.config['CLIENT_SECRET'],
        'code': code,
        'redirect_uri': current_app.config['REDIRECT_URI']
    }
    
    response = requests.post(token_url, data=data)
    return response.json()

def get_user_info(access_token):
    """Get user information from Microsoft Graph"""
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    return response.json()

def get_user_groups(access_token):
    """Get user's group memberships from Microsoft Graph"""
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.get('https://graph.microsoft.com/v1.0/me/memberOf', headers=headers)
    return response.json()

def get_auth_url():
    """Generate Entra ID authorization URL"""
    c = current_app.config
    return (
        f"https://login.microsoftonline.com/{c['TENANT_ID']}/oauth2/v2.0/authorize?"
        f"client_id={c['CLIENT_ID']}&response_type=code&redirect_uri={c['REDIRECT_URI']}"
        f"&scope=openid profile email User.Read GroupMember.Read.All&response_mode=query"
    )

def get_logout_url():
    """Generate Entra ID logout URL"""
    return (
        f"https://login.microsoftonline.com/{current_app.config['TENANT_ID']}/oauth2/v2.0/logout?"
        f"post_logout_redirect_uri={current_app.config['LOGOUT_URI']}"
    )