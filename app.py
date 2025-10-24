from flask import Flask, request, redirect, session, jsonify
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
TENANT_ID = "your-tenant-id"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-super-secret-client-secret"
CALLBACK_PATH = "/login/callback"
LOGIN_PATH = "/login"
PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}{CALLBACK_PATH}"

@app.route(LOGIN_PATH)
def login():
    """Redirect to Entra ID for authentication"""
    auth_url = (
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope=openid profile email&response_mode=query"
    )
    return redirect(auth_url)

@app.route(CALLBACK_PATH)
def callback():
    """Handle Entra ID callback"""
    code = request.args.get('code')
    if not code:
        return "Error: No authorization code received", 400
    
    # Exchange code for token
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    token_data = response.json()
    
    if 'access_token' not in token_data:
        return f"Token error: {token_data}", 400
    
    # Get user info
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    user_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    user_info = user_response.json()
    
    return jsonify(user_info)

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
