from flask import Blueprint, request, redirect, session, render_template, current_app
from app.auth import exchange_code_for_token, get_user_info, get_user_groups, get_auth_url, get_logout_url
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    """Home page with login/logout buttons"""
    user_data = session.get('user_data')
    user_groups = session.get('user_groups')
    auth_provider = current_app.config['AUTH_PROVIDER']
    return render_template('index.html', 
                         user_data=user_data, 
                         user_groups=user_groups,
                         auth_provider=auth_provider)

@bp.route('/login')
def login():
    """Redirect to configured auth provider"""
    current_app.logger.info(f"Login initiated with provider: {current_app.config['AUTH_PROVIDER']}")
    return redirect(get_auth_url())

@bp.route('/login/callback')
def callback():
    """Handle OAuth callback from auth provider"""
    code = request.args.get('code')
    if not code:
        current_app.logger.error('No authorization code received')
        return "Error: No authorization code received", 400
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    
    # current_app.logger.info(f'Token exchange response: {json.dumps(token_data, indent=4)}')
    
    if 'access_token' not in token_data:
        current_app.logger.error(f'Token exchange failed: {token_data}')
        return f"Token error: {token_data}", 400
    
    # Get user info and groups
    user_info = get_user_info(token_data['access_token'])
    user_groups = get_user_groups(token_data['access_token'])
    
    # Log user identifier (different field names per provider)
    user_id = user_info.get('upn') or user_info.get('preferred_username') or user_info.get('email', 'unknown')
    current_app.logger.info(f'User logged in: {user_id} via {current_app.config["AUTH_PROVIDER"]}')
    
    # Store user data in session
    session['user_data'] = user_info
    session['user_groups'] = user_groups
    session['auth_provider'] = current_app.config['AUTH_PROVIDER']
    
    return redirect('/')

@bp.route('/logout')
def logout():
    """Logout user and redirect to auth provider logout"""
    user_data = session.get('user_data', {})
    user = user_data.get('userPrincipalName') or user_data.get('username') or user_data.get('email', 'unknown')
    provider = session.get('auth_provider', current_app.config['AUTH_PROVIDER'])
    current_app.logger.info(f'User logged out: {user} from {provider}')
    session.clear()
    return redirect(get_logout_url())