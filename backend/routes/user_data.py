from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from models.user import User
from config.db import conn
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

user = APIRouter()

templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate a bcrypt hash for a sample password
hashed_password = pwd_context.hash("password")
print("Hashed Password:", hashed_password)

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Login model
class LoginModel(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str):
    user = conn.user.user_details.find_one({"username": username})
    if not user:
        return False
    # If user password is plaintext, hash it (not recommended for production)
    hashed_password = pwd_context.hash(user["password"]) if "hashed_password" not in user else user["hashed_password"]
    if not verify_password(password, hashed_password):
        return False
    return user


@user.post("/login", response_model=Token)
async def login(login_data: LoginModel):
    user = authenticate_user(login_data.username, login_data.password)
    print(user)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": login_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@user.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    #print(conn.list_database_names())  # Check if 'user' is listed
    #print(conn["user"].list_collection_names())  # Check if 'user_details' is listed
    data = conn.user.user_details.find({})
    print(data)
    lst = []
    for d in data:
        lst.append({"id": d["_id"],
                    "name": d["name"]})
    #print(lst)
    return templates.TemplateResponse(request=request, name="index.html", context={"lst": lst})

@user.post("/register", response_class= HTMLResponse)
async def add_user(request: Request):
    try:
        data = await request.json()
        print(data)
        user_data = conn.user.user_details.insert_one(data)
        return JSONResponse({"Success": True})
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

