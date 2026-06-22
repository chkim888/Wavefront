import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Loading env variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES"))

# Takes a payload & returns a signed JWT string
def create_access_token(user_id):
    print("JWT_SECRET exists:", bool(SECRET_KEY))
    print("JWT_EXPIRY_MINUTES:", JWT_EXPIRY_MINUTES)
    expiry = datetime.utcnow() + timedelta(minutes=int(JWT_EXPIRY_MINUTES))
    payload = {
        "user_id": str(user_id),
        "exp": expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

# Takes a JWT string & returns the payload (or raise an error)
def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except InvalidTokenError:        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token"
        )