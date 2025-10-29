# Flask Entra ID SSO Example <!-- omit in toc -->

- [What This Example Does](#what-this-example-does)
- [Requirements](#requirements)
- [Download Python](#download-python)
- [Setup Instructions](#setup-instructions)
  - [1. Create and Activate Virtual Environment](#1-create-and-activate-virtual-environment)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Entra ID Application](#3-configure-entra-id-application)
  - [4. Update Environment Configuration](#4-update-environment-configuration)
  - [5. Run the Application](#5-run-the-application)
- [Usage](#usage)
- [Getting User Info](#getting-user-info)
  - [User Profile Data (`/me` endpoint)](#user-profile-data-me-endpoint)
  - [Group Memberships (`/me/memberOf` endpoint)](#group-memberships-mememberof-endpoint)
  - [Authentication Flow](#authentication-flow)
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
pip install -r requirements.txt
```

**Linux/macOS:**

```bash
pip install -r requirements.txt
```

### 3. Configure Entra ID Application

1. Go to [Azure Portal](https://portal.azure.com) > Entra ID > App registrations
2. Create a new application registration
3. Add redirect URI: `http://localhost:8080/login/callback` (or adjust based on your HOST and POST settings)
4. Note down:
   - Tenant ID
   - Client ID
5. Create a Client Secret, from "Overview" -> "Add a certificate or secret" -> "New client secret". Beware of choosing an appropriate expiration period
6. Ensure that the following Microsoft Graph API permissions are set:
   - `User.Read` - enable the read of the user attributes
7. From "Enterprise Apps" find your app and in "Properties" mark "Yes" on "Require assignment", this ensure that users that aren't assigned to the app cannot login through it
8. In the same view click on "Users & Groups" and then add users or group to this app
9. Done

### 4. Update Environment Configuration

1. **Copy the environment template:**

   ```cmd
   copy .env.example .env
   ```

2. **Edit the `.env` file with your actual values:**

   ```env
   SECRET_KEY=your-secret-key-here
   TENANT_ID=your-actual-tenant-id
   CLIENT_ID=your-actual-client-id
   CLIENT_SECRET=your-actual-client-secret
   HOST=http://localhost
   PORT=8080
   CALLBACK_PATH=/login/callback
   LOGIN_PATH=/login
   ```

**Environment Variables:**

- `SECRET_KEY`: Flask session secret (auto-generated if not set)
- `TENANT_ID`: Your Entra ID tenant ID from Azure Portal
- `CLIENT_ID`: Your application's client ID from app registration
- `CLIENT_SECRET`: Your application's client secret
- `HOST`: Hostname for the application (default: `http://localhost`)
- `PORT`: Port number for the Flask server (default: 8080)
- `CALLBACK_PATH`: OAuth callback endpoint path (default: /login/callback)
- `LOGIN_PATH`: Login endpoint path (default: /login)

**Note:** The `.env` file is automatically loaded when the application starts. Never commit this file to version control as it contains sensitive information.

### 5. Run the Application

**Windows:**

```cmd
python run.py
```

**Linux/macOS:**

```bash
python3 run.py
```

## Usage

1. **Start the application:**

   ```cmd
   python run.py
   ```

2. **Open your browser** and navigate to `http://localhost:8080` (or your configured HOST:PORT)

3. **Login Process:**
   - Click the "Login with Microsoft" button
   - You'll be redirected to Microsoft's login page
   - Enter your credentials and complete any required MFA
   - After successful authentication, you'll be redirected back to the app

4. **View Information:**
   - **User Information**: Displays your profile data (name, email, etc.)
   - **Group Memberships**: Shows all groups you're a member of
   - **Copy Feature**: Click on any information box to copy the JSON data to your clipboard

5. **Logout:**
   - Click the "Logout" button to sign out
   - This will clear your session and redirect to Microsoft's logout page

## Getting User Info

The application retrieves user information through Microsoft Graph API calls:

> All api call can be seen in details in the [auth.py](/app/auth.py) file.

### User Profile Data (`/me` endpoint)

**API Call:** `GET https://graph.microsoft.com/v1.0/me`

**Required Permissions:**

- `User.Read` - Allows reading the signed-in user's profile

**Data Retrieved:**

- User principal name (email)
- Display name
- Job title
- Department
- Office location
- Phone numbers
- And other profile attributes

### Group Memberships (`/me/memberOf` endpoint)

**API Call:** `GET https://graph.microsoft.com/v1.0/me/memberOf`

**Required Permissions:**

- `GroupMember.Read.All` - Allows reading group memberships

**Data Retrieved:**

- Security groups
- Distribution groups
- Microsoft 365 groups
- Administrative units
- Directory roles

### Authentication Flow

1. **OAuth2 Authorization Code Flow:**
   - User is redirected to Entra ID with scopes: `openid profile email User.Read GroupMember.Read.All`
   - After authentication, an authorization code is returned
   - The code is exchanged for an access token
   - The access token is used to make Graph API calls

2. **Token Usage:**
   - Access token is included in the `Authorization: Bearer {token}` header
   - Both `/me` and `/me/memberOf` calls use the same token
   - Token permissions are determined by the scopes requested during authentication

**Note:** Ensure your Entra ID application has the required API permissions (`User.Read` and `GroupMember.Read.All`) configured and admin consent granted.

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
