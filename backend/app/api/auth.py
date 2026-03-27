"""
Authentication API - MongoDB Only
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from ..auth.auth_service import register_user, login_user, get_current_user

router = APIRouter()

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user_id: str
    email: str
    name: str
    access_token: str
    token_type: str

@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Register new user in MongoDB"""
    try:
        result = await register_user(request.email, request.password, request.name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    try:
        result = await login_user(request.email, request.password)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/me")
async def get_me(authorization: str = Header(None)):
    """Get current user from token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    return user

# Dependency for protected routes
async def get_current_user_id(authorization: str = Header(None)) -> str:
    """Get current user ID from token (for dependency injection)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    return user["user_id"]
