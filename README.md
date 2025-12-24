# Flask SSO Example <!-- omit in toc -->

- [What This Example Does](#what-this-example-does)
- [Requirements](#requirements)
- [Download Python](#download-python)
- [Setup Instructions](#setup-instructions)
  - [Common Setup (Steps 1-2)](#common-setup-steps-1-2)
    - [1. Create and Activate Virtual Environment](#1-create-and-activate-virtual-environment)
    - [2. Install Dependencies](#2-install-dependencies)
  - [Option 1: Direct Entra ID Authentication](#option-1-direct-entra-id-authentication)
    - [3. Configure Entra ID Application](#3-configure-entra-id-application)
    - [4. Update Environment Configuration](#4-update-environment-configuration)
    - [5. Run the Application](#5-run-the-application)
  - [Option 2: AWS Cognito with Entra ID as IdP](#option-2-aws-cognito-with-entra-id-as-idp)
    - [3. Configure Entra ID Application for Cognito](#3-configure-entra-id-application-for-cognito)
    - [4. Configure AWS Cognito User Pool](#4-configure-aws-cognito-user-pool)
    - [5. Update Environment Configuration](#5-update-environment-configuration)
    - [6. Run the Application](#6-run-the-application)
- [Usage](#usage)
- [Getting User Info](#getting-user-info)
  - [Direct Entra ID](#direct-entra-id)
  - [AWS Cognito](#aws-cognito)
- [Deactivate Virtual Environment](#deactivate-virtual-environment)
- [Docker](#docker)
  - [Build and Run with Docker](#build-and-run-with-docker)
  - [Docker Compose](#docker-compose)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [DISCLAIMER](#disclaimer)

A minimal Flask web application that demonstrates Single Sign-On (SSO) authentication using either Microsoft Entra ID directly or AWS Cognito as an identity provider router. The application handles the OAuth2 authorization code flow and displays user information after successful authentication.

## What This Example Does

This Flask application:

- Supports two authentication methods:
  1. **Direct Entra ID**: Authenticate directly with Microsoft Entra ID
  2. **AWS Cognito**: Use Cognito as an IdP router with Entra ID as the upstream provider
- Handles the OAuth2 callback at `/login/callback`
- Exchanges the authorization code for an access token
- Retrieves user profile information
- Displays the user information as JSON

## Requirements

- **Python 3.7 or higher** (recommended: Python 3.9+)
- Internet connection for authentication
- **For Option 1**: Microsoft Entra ID application registration
- **For Option 2**: AWS account with Cognito access + Microsoft Entra ID application registration

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

### Common Setup (Steps 1-2)

#### 1. Create and Activate Virtual Environment

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

#### 2. Install Dependencies

**Windows:**

```cmd
pip install -r requirements.txt
```

**Linux/macOS:**

```bash
pip install -r requirements.txt
```

### Option 1: Direct Entra ID Authentication

#### 3. Configure Entra ID Application

1. Go to [Azure Portal](https://portal.azure.com) > Entra ID > App registrations
2. Create a new application registration
3. Add redirect URI: `http://localhost:8080/login/callback`
4. Note down:
   - Tenant ID
   - Client ID
5. Create a Client Secret: "Overview" -> "Add a certificate or secret" -> "New client secret"
6. Set Microsoft Graph API permissions:
   - `User.Read` - Allows reading the signed-in user's profile information (name, email, job title, etc.)
   - `openid` - Enables OpenID Connect authentication flow
   - `profile` - Grants access to user's basic profile claims (name, preferred username)
   - `email` - Provides access to the user's email address
   - `GroupMember.Read.All` - Allows reading the user's group memberships (requires Entra ID admin consent)
7. Enterprise Apps > Your app > Properties > "Require assignment" = Yes
8. Add users/groups under "Users & Groups"

#### 4. Update Environment Configuration

```bash
cp .env.example .env
```

Edit `.env`:

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

#### 5. Run the Application

```bash
python run.py
```

---

### Option 2: AWS Cognito with Entra ID as IdP

#### 3. Configure Entra ID Application for Cognito

1. Go to [Azure Portal](https://portal.azure.com) > Entra ID > App registrations
2. Create a new application registration
3. Add redirect URI: `https://<your-cognito-domain>.auth.<region>.amazoncognito.com/oauth2/idpresponse`
4. Note down:
   - Tenant ID
   - Client ID
5. Create a Client Secret
6. Under "Token configuration", add optional claims:
   - **ID token**: `email`, `family_name`, `given_name`, `upn`
   - **Access token**: `email`, `family_name`, `given_name`, `upn`
7. Set Microsoft Graph API permissions:
   - `User.Read` - Allows reading the signed-in user's profile information (name, email, job title, etc.)
   - `openid` - Enables OpenID Connect authentication flow
   - `profile` - Grants access to user's basic profile claims (name, preferred username)
   - `email` - Provides access to the user's email address
8. Enterprise Apps > Your app > Properties > "Require assignment" = Yes
9. Add users/groups under "Users & Groups"

#### 4. Configure AWS Cognito User Pool

**Create User Pool:**

1. AWS Console > Cognito > Create user pool
2. Configure sign-in options: Email, Phone, Preferred username
3. Note the User Pool ID and Region

**Create App Client:**

1. User Pool > App integration > Create app client
2. App type: Confidential client
3. Callback URLs: `http://localhost:8080/login/callback`
4. Logout URLs: `http://localhost:8080/logout`
5. OAuth 2.0 grant types: Authorization code grant
6. OAuth scopes: `openid`, `profile`, `email`, `phone`
7. Note the Client ID and Client Secret

**Configure Identity Provider:**

1. User Pool > Sign-in experience > Add identity provider
2. Select "OpenID Connect"
3. Provider name: `EntraID` (or your choice)
4. Client ID: From Entra ID app
5. Client secret: From Entra ID app
6. Authorize scope: `openid profile email User.Read`
7. Issuer URL: `https://login.microsoftonline.com/<tenant-id>/v2.0`
8. Attributes request method: `GET`

**Configure Attribute Mapping:**

Under the Identity Provider settings, map the following attributes:

| Cognito Attribute  | OIDC Claim (Entra ID) |
| ------------------ | --------------------- |
| given_name         | given_name            |
| username           | sub                   |
| preferred_username | upn                   |
| email              | upn                   |
| email_verified     | email_verified        |
| name               | name                  |
| phone_number       | phone_number          |

**Note:** The `upn` (User Principal Name) claim must be added as an optional claim in Entra ID (step 3.6 above).

**Update App Client:**

1. Go back to your App client
2. Hosted UI settings > Identity providers > Select your EntraID provider
3. Save changes

#### 5. Update Environment Configuration

```bash
cp .env.example .env
```

Edit `.env`:

```env
AUTH_PROVIDER=COGNITO
SECRET_KEY=your-secret-key-here
TENANT_ID=<cognito-user-pool-id>
CLIENT_ID=<cognito-app-client-id>
CLIENT_SECRET=<cognito-app-client-secret>
HOST=http://localhost
PORT=8080
CALLBACK_PATH=/login/callback
LOGIN_PATH=/login
COGNITO_DOMAIN=https://<cognito-domain>.auth.<region>.amazoncognito.com
```

#### 6. Run the Application

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

### Direct Entra ID

**User Profile Data:**

```sh
GET https://graph.microsoft.com/v1.0/me
Authorization: Bearer {access_token}
```

**Group Memberships:**

```sh
GET https://graph.microsoft.com/v1.0/me/memberOf
Authorization: Bearer {access_token}
```

**Required Permissions:** `User.Read`, `GroupMember.Read.All`

---

### AWS Cognito

**User Info Endpoint:**

```sh
GET https://<cognito-domain>.auth.<region>.amazoncognito.com/oauth2/userInfo
Authorization: Bearer {access_token}
```

**Response Example:**

```json
{
  "sub": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "email_verified": "true",
  "given_name": "John",
  "name": "John Doe",
  "preferred_username": "john.doe@example.com",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "username": "EntraID_aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
}
```

**Note:** Cognito does not provide group memberships through the userInfo endpoint. For groups, you need to:

1. Configure group claims in Entra ID
2. Map them to custom attributes in Cognito
3. Or query groups directly from Entra ID using a separate Graph API call

Optionally by default Cognito creates its own group for each IDP it integrates, so you can query Cognito for their values.

## Deactivate Virtual Environment

**Windows & Linux:**

```bash
deactivate
```

## Docker

### Build and Run with Docker

**Build the image:**

```bash
docker build -t flask-entraid-sso:latest .
```

**Run the container:**

```bash
docker run -d \
  -p 8080:8080 \
  -e AUTH_PROVIDER=COGNITO \
  -e COGNITO_DOMAIN=your-domain.auth.region.amazoncognito.com \
  -e CLIENT_ID=your-client-id \
  -e CLIENT_SECRET=your-client-secret \
  --name flask-entraid-sso \
  flask-entraid-sso:latest
```

### Docker Compose

**Start the application:**

```bash
docker compose up -d
```

**Stop the application:**

```bash
docker compose down
```

**Note:** Edit `compose.yml` to configure environment variables for your setup.

## Environment Variables

| Variable         | Required | Default            | Description                                                        | Used By      |
| ---------------- | -------- | ------------------ | ------------------------------------------------------------------ | ------------ |
| `AUTH_PROVIDER`  | No       | `entraid`          | Authentication provider: `entraid` or `cognito`                    | Both         |
| `CLIENT_ID`      | Yes      | -                  | OAuth2 client ID from Entra ID or Cognito                          | Both         |
| `CLIENT_SECRET`  | Yes      | -                  | OAuth2 client secret from Entra ID or Cognito                      | Both         |
| `TENANT_ID`      | Yes*     | -                  | Entra ID tenant ID                                                 | Entraid only |
| `COGNITO_DOMAIN` | Yes**    | -                  | Cognito domain (e.g., `your-domain.auth.region.amazoncognito.com`) | Cognito only |
| `COGNITO_REGION` | No       | `eu-south-1`       | AWS region for Cognito                                             | Cognito only |
| `HOST`           | No       | `http://localhost` | Application host URL                                               | Both         |
| `PORT`           | No       | `8080`             | Application port number                                            | Both         |
| `CALLBACK_PATH`  | No       | `/login/callback`  | OAuth2 callback path                                               | Both         |
| `LOGIN_PATH`     | No       | `/login`           | Login endpoint path                                                | Both         |
| `SECRET_KEY`     | No       | Auto-generated     | Flask session secret key. Auto-generated if not provided           | Both         |

**Notes:**

- `*` Required for Entra ID as tenant ID, required for Cognito as User Pool ID
- `**` Required only when `AUTH_PROVIDER=cognito`
- `REDIRECT_URI` and `LOGOUT_URI` are computed automatically from `HOST`, `PORT`, and `CALLBACK_PATH`

## Troubleshooting

**Common Issues:**

- Ensure redirect URIs match exactly (including protocol and port)
- Verify all configuration values in `.env`
- Check that virtual environment is activated
- Confirm internet connectivity

**Entra ID Specific:**

- Verify API permissions and admin consent granted
- Check that users are assigned to the Enterprise App

**Cognito Specific:**

- Ensure Cognito domain is correctly configured
- Verify Identity Provider is enabled for the App Client
- Check attribute mappings match Entra ID claims
- Confirm `upn` claim is added as optional claim in Entra ID
- Verify callback URLs in both Cognito and Entra ID match

---

## DISCLAIMER

> README was generated with Amazon Q so not every command might work perfectly
