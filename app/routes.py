from flask import Blueprint, request, redirect, session, render_template, current_app
from app.auth import exchange_code_for_token, get_user_info, get_user_groups, get_auth_url, get_logout_url

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    """Home page with login/logout buttons"""
    user_data = session.get('user_data')
    user_groups = session.get('user_groups')
    return render_template('index.html', user_data=user_data, user_groups=user_groups)

@bp.route('/login')
def login():
    """Redirect to Entra ID for authentication"""
    return redirect(get_auth_url())

@bp.route('/login/callback')
def callback():
    """Handle Entra ID callback"""
    code = request.args.get('code')
    if not code:
        current_app.logger.error('No authorization code received')
        return "Error: No authorization code received", 400
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    
    if 'access_token' not in token_data:
        current_app.logger.error(f'Token exchange failed: {token_data}')
        return f"Token error: {token_data}", 400
    
    # Get user info and groups
    user_info = get_user_info(token_data['access_token'])
    user_groups = get_user_groups(token_data['access_token'])
    current_app.logger.info(f'User logged in: {user_info.get("userPrincipalName", "unknown")}')
    
    # Store user data in session
    session['user_data'] = user_info
    session['user_groups'] = user_groups
    
    return redirect('/')

@bp.route('/logout')
def logout():
    """Logout user and redirect to Entra ID logout"""
    user = session.get('user_data', {}).get('userPrincipalName', 'unknown')
    current_app.logger.info(f'User logged out: {user}')
    session.clear()
    return redirect(get_logout_url())