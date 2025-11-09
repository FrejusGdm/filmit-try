from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone
import logging
import httpx

from schemas.user import Token
from utils.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/oauth", tags=["oauth"])
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth login."""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    
    # Auto-detect redirect URI based on request host
    host = request.headers.get('host', 'localhost:8001')
    is_production = 'emergentagent.com' in host or 'https' in str(request.base_url)
    
    if is_production:
        # Production URL
        redirect_uri = f"https://{host}/api/auth/oauth/google/callback"
    else:
        # Development URL
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8001/api/auth/oauth/google/callback')
    
    # Check if credentials are configured
    if not client_id or not os.getenv('GOOGLE_CLIENT_SECRET'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured. Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env file."
        )
    
    # Build Google OAuth URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return RedirectResponse(url=google_auth_url)

@router.get("/google/callback")
async def google_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Google OAuth callback."""
    try:
        # Auto-detect URLs based on request host
        host = request.headers.get('host', 'localhost:8001')
        is_production = 'emergentagent.com' in host
        
        if is_production:
            frontend_url = f"https://{host}"
            redirect_uri = f"https://{host}/api/auth/oauth/google/callback"
        else:
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8001/api/auth/oauth/google/callback')
        
        # Check for OAuth errors
        if error:
            logger.error(f"Google OAuth error: {error}")
            return RedirectResponse(url=f"{frontend_url}/login?error=oauth_failed")
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided"
            )
        
        # Exchange code for access token
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(
                'https://oauth2.googleapis.com/token',
                data=token_data
            )
            
            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received"
                )
            
            # Get user info
            user_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if user_response.status_code != 200:
                logger.error(f"User info request failed: {user_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user information from Google"
                )
            
            user_info = user_response.json()
        
        email = user_info.get('email')
        name = user_info.get('name', '')
        google_id = user_info.get('id')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = await db.users.find_one({"email": email})
        
        if user:
            # User exists - login
            user_id = user['id']
            logger.info(f"Existing user logged in via Google: {email}")
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            
            # Generate username from name or email
            username = name.lower().replace(' ', '_') if name else email.split('@')[0]
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while await db.users.find_one({"username": username}):
                username = f"{base_username}{counter}"
                counter += 1
            
            new_user = {
                "id": user_id,
                "email": email,
                "username": username,
                "hashed_password": "",  # No password for OAuth users
                "oauth_provider": "google",
                "oauth_id": google_id,
                "created_at": datetime.now(timezone.utc),
                "is_active": True
            }
            
            await db.users.insert_one(new_user)
            logger.info(f"New user created via Google OAuth: {email}")
        
        # Create JWT tokens
        jwt_access_token = create_access_token(data={"sub": user_id, "email": email})
        jwt_refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Redirect to frontend with tokens (use already determined frontend_url)
        callback_url = f"{frontend_url}/auth/callback?access_token={jwt_access_token}&refresh_token={jwt_refresh_token}"
        
        return RedirectResponse(url=callback_url)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        # Use production or dev URL based on host
        host = request.headers.get('host', 'localhost:8001')
        is_production = 'emergentagent.com' in host
        error_url = f"https://{host}/login?error=oauth_failed" if is_production else "http://localhost:3000/login?error=oauth_failed"
        return RedirectResponse(url=error_url)
