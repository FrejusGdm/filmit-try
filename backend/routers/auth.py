from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone
import logging

from schemas.user import UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest
from utils.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from utils.auth_dependencies import get_current_user
from routers import oauth

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

# Include OAuth routes
router.include_router(oauth.router)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username is taken
        existing_username = await db.users.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data.password)
        
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc),
            "is_active": True
        }
        
        await db.users.insert_one(new_user)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user_id, "email": user_data.email})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        logger.info(f"New user registered: {user_data.email}")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password."""
    try:
        # Find user by email
        user = await db.users.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create tokens
        access_token = create_access_token(data={"sub": user["id"], "email": user["email"]})
        refresh_token = create_refresh_token(data={"sub": user["id"]})
        
        logger.info(f"User logged in: {credentials.email}")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(token_request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = verify_token(token_request.refresh_token, token_type="refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user["id"], "email": user["email"]})
        new_refresh_token = create_refresh_token(data={"sub": user["id"]})
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout user (client should discard tokens)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}
