# Flask Entra ID SSO Example <!-- omit in toc -->

- [What This Example Does](#what-this-example-does)
- [Requirements](#requirements)
- [Download Python](#download-python)
- [Setup Instructions](#setup-instructions)
  - [1. Create and Activate Virtual Environment](#1-create-and-activate-virtual-environment)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Entra ID Application](#3-configure-entra-id-application)
  - [4. Update Configuration](#4-update-configuration)
  - [5. Run the Application](#5-run-the-application)
- [Usage](#usage)
- [Deactivate Virtual Environment](#deactivate-virtual-environment)
- [Troubleshooting](#troubleshooting)
- [DISCLAIMER](#disclaimer)

A minimal Flask web application that demonstrates Single Sign-On (SSO) authentication using Microsoft Entra ID (formerly Azure AD). The application handles the OAuth2 authorization code flow and displays user information after successful authentication.

## What This Example Does

This Flask application:

- Redirects users to Microsoft Entra ID for authentication
- Handles the OAuth2 callback at `/login/callback`
- Exchanges the authorization code for an access token
- Retrieves user profile information from Microsoft Graph API
- Displays the user information as JSON

## Requirements

- **Python 3.7 or higher** (recommended: Python 3.9+)
- Microsoft Entra ID application registration
- Internet connection for authentication

## Download Python

- **Windows**: Download from [python.org](https://www.python.org/downloads/windows/)
- **Linux**: Usually pre-installed, or install via package manager:

  ```bash
  # Ubuntu/Debian
  sudo apt update && sudo apt install python3 python3-pip python3-venv
  
  # CentOS/RHEL/Fedora
  sudo yum install python3 python3-pip
  ```

## Setup Instructions

### 1. Create and Activate Virtual Environment

**Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

**Windows:**

```cmd
pip install flask requests
```

**Linux/macOS:**

```bash
pip install flask requests
```

### 3. Configure Entra ID Application

1. Go to [Azure Portal](https://portal.azure.com) > Entra ID > App registrations
2. Create a new application registration
3. Add redirect URI: `http://localhost:8080/login/callback` (or adjust based on your PORT setting)
4. Note down:
   - Tenant ID
   - Client ID
   - Client Secret (create one in "Certificates & secrets")

### 4. Update Configuration

Edit `app.py` and update the configuration constants at the top of the file:

```python
# Configuration - Edit these values
TENANT_ID = "your-actual-tenant-id"
CLIENT_ID = "your-actual-client-id"
CLIENT_SECRET = "your-actual-client-secret"
CALLBACK_PATH = "/login/callback"  # Change callback path if needed
LOGIN_PATH = "/login"                      # Change login path if needed
PORT = 8080                                # Change port if needed
```

**Configuration Options:**

- `TENANT_ID`: Your Entra ID tenant ID
- `CLIENT_ID`: Your application's client ID
- `CLIENT_SECRET`: Your application's client secret
- `CALLBACK_PATH`: The callback endpoint path (default: `/login/callback`)
- `LOGIN_PATH`: The login endpoint path (default: `/login`)
- `PORT`: The port the Flask server runs on (default: `8080`)

### 5. Run the Application

**Windows:**

```cmd
python app.py
```

**Linux/macOS:**

```bash
python3 app.py
```

## Usage

1. Start the Flask server (it will run on `http://localhost:8080` by default)
2. Open your browser and go to `http://localhost:8080/login` (or your configured LOGIN_PATH)
3. You'll be redirected to Microsoft login page
4. After successful authentication, you'll see your user information as JSON

**Note:** The URLs will change based on your PORT and path configurations in the constants.

## Deactivate Virtual Environment

**Windows & Linux:**

```bash
deactivate
```

## Troubleshooting

- Ensure your Entra ID app has the correct redirect URI configured
- Check that all configuration values are correctly set
- Verify your internet connection for authentication requests
- Make sure the virtual environment is activated before running the app

---

## DISCLAIMER

> README was generated with Amazon Q so not every command might work perfectly
