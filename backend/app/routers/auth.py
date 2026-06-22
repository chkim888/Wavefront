from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
import bcrypt
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.models.user import User
from app.database import get_db_session
from app.auth.jwt import create_access_token


# Create an API router to facilitate connections
router = APIRouter(prefix="/auth")

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db_session = Depends(get_db_session)):
    # check if email or username is in the database
    duplicate_check = select(User).where(
        or_(User.email == user.email, User.username == user.username))
    if (db_session.scalars(duplicate_check).first()):
        # return an error if duplicate user info found in database
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email address and/or username already exists"
        )
    else:
        # hash password
        password_bytes = user.password.encode('utf-8')
        salt = bcrypt.gensalt() # random characters added before getting hashed
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        # save new user information to database
        new_user = User(
            username=user.username, 
            email=user.email, 
            password_hash=hashed_password.decode('utf-8'))
        db_session.add(new_user)     # staging the created user to be added 
        db_session.commit()          # committing staged changes (i.e. adding new user)
        db_session.refresh(new_user) # syncing new user object with new database values
        return new_user

@router.post("/login")
def login(user: UserLogin, db_session = Depends(get_db_session)):
    # check if username exists 
    db_user = db_session.scalars(
        select(User).where(User.username == user.username)
    ).first()
    if not db_user: # No user with matching info found -- raise an exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with a matching username found"
        )
    if not bcrypt.checkpw( # extracts salt automatically when hashing
        user.password.encode('utf-8'),
        db_user.password_hash.encode('utf-8')
    ): # matching username found but password doesn't match
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User password does not match the record"
        )
    # user validation successful -- return JWT
    return {"access_token": create_access_token(db_user.id), "token_type": "bearer"}