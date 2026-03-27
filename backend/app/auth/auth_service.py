"""
Authentication Service - MongoDB Only
User authentication using MongoDB
"""
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from ..config.settings import settings
from ..database.mongodb import collections
from bson import ObjectId

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Convert ObjectId to string for JWT
    if "_id" in to_encode:
        to_encode["_id"] = str(to_encode["_id"])
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode JWT access token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def register_user(email: str, password: str, name: str = None) -> dict:
    """Register new user in MongoDB"""
    users = collections.users()
    
    # Check if user exists
    existing_user = await users.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user document
    user_doc = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name or email.split('@')[0],
        "business_ids": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Create access token
    access_token = create_access_token({"user_id": str(result.inserted_id), "email": email})
    
    return {
        "user_id": str(result.inserted_id),
        "email": email,
        "name": user_doc["name"],
        "access_token": access_token,
        "token_type": "bearer"
    }

async def login_user(email: str, password: str) -> dict:
    """Login user"""
    users = collections.users()
    
    # Find user
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token({"user_id": str(user["_id"]), "email": email})
    
    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", email.split('@')[0]),
        "access_token": access_token,
        "token_type": "bearer"
    }

async def get_current_user(token: str) -> dict:
    """Get current user from token"""
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    users = collections.users()
    user = await users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", ""),
        "business_ids": user.get("business_ids", [])
    }
