from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from uuid import UUID
from app.auth.dependencies import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User
from app.database import get_db_session

# Router initialization
router = APIRouter(prefix="/users")

## Create
# Create new user -- already taken care of in auth.py

## Read
# Read user information (username, email, created at)
@router.get("", response_model=UserResponse)
def get_user(user = Depends(get_current_user)):
    return user

## Update
# Update user information (username, email)
@router.patch("", response_model=UserResponse)
def update_user(updates: UserUpdate, user = Depends(get_current_user), db_session = Depends(get_db_session)):
    user_info = db_session.scalars(select(User).where(User.id == user.id)).first()
    if user_info:
        if updates.username:
            # Check if username already exists
            existing = db_session.scalars(select(User).where(User.username == updates.username)).first()
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already in use"
                )
            else:
                user_info.username = updates.username
        if updates.email:
            # Check if email already exists
            existing = db_session.scalars(select(User).where(User.email == updates.email)).first()
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
            else:
                user_info.email = updates.email
        db_session.commit()
        db_session.refresh(user_info)
        return user_info
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )

## Delete
# Delete user
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user = Depends(get_current_user), db_session = Depends(get_db_session)):
    db_session.delete(user)
    db_session.commit()