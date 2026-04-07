import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = str(os.getenv("SUPABASE_URL"))
key: str = str(os.getenv("SUPABASE_KEY"))

supabase: Client = create_client(url, key)

# Instead of generating a new hash for each failed authentication attempt, we can use a fixed dummy hash.
# This way, we can ensure that the time taken for authentication is consistent regardless of whether the user exists or not, which helps mitigate timing attacks.
DUMMY_HASH = b"$2b$12$R9h/cIPz0gi.URNNX3kh2UXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

def create_user(username: str, password: str):
    existing_user = supabase.table("USERS").select("*").eq("username", username).execute()

    if existing_user.data:
        raise ValueError("User already exists")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    supabase.table("USERS").insert({
        "username": username,
        "password": password_hash.decode("utf-8")  # store as string
    }).execute()

def authenticate_user(username: str, password: str) -> bool:
    user = supabase.table("USERS").select("password").eq("username", username).execute()
    data : list = user.data

    if len(data) == 0:
        bcrypt.checkpw(password.encode(), DUMMY_HASH)
        return False
    
    stored_password = data[0].get("password")
    if not isinstance(stored_password, str):
        return False

    return bcrypt.checkpw(password.encode(), stored_password.encode())