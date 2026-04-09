import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client
import jwt
from datetime import datetime, timedelta

load_dotenv()

url: str = str(os.getenv("SUPABASE_URL"))
key: str = str(os.getenv("SUPABASE_KEY"))

supabase: Client = create_client(url, key)

# Instead of generating a new hash for each failed authentication attempt, we can use a fixed dummy hash.
# This way, we can ensure that the time taken for authentication is consistent regardless of whether the user exists or not, which helps mitigate timing attacks.
DUMMY_HASH = b"$2b$12$R9h/cIPz0gi.URNNX3kh2UXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# JWT configuration (can be overridden with environment variables)
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "3600"))

def create_user(username: str, password: str):
    existing_user = supabase.table("USERS").select("*").eq("username", username).execute()

    if existing_user.data:
        raise ValueError("User already exists")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    supabase.table("USERS").insert({
        "username": username,
        "password": password_hash.decode("utf-8")  # store as string
    }).execute()

def generate_auth_token(username: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(seconds=JWT_EXP_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def verify_auth_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]  # return the username
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def authenticate_user(username: str, password: str) -> str:
    """Authenticate the user and return a JWT token on success.

    Raises ValueError on authentication failure.
    """
    user = supabase.table("USERS").select("password").eq("username", username).execute()
    data : list = user.data

    if len(data) == 0:
        # dummy check to mitigate timing attacks
        try:
            bcrypt.checkpw(password.encode(), DUMMY_HASH)
        except Exception:
            pass
        raise ValueError("Invalid username or password")
    
    stored_password = data[0].get("password")
    if not isinstance(stored_password, str):
        raise ValueError("Invalid username or password")

    if not bcrypt.checkpw(password.encode(), stored_password.encode()):
        raise ValueError("Invalid username or password")

    return generate_auth_token(username)
