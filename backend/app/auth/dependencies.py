from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, and_
from fastapi import HTTPException, status, Depends
from uuid import UUID
from app.models.user import User, User_Project
from app.auth.jwt import verify_token
from app.database import get_db_session

# automatically gets the token from the header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# return the current user
def get_current_user(token: str=Depends(oauth2_scheme), db=Depends(get_db_session)):
    # verify token
    payload = verify_token(token)
    # extract user id from payload
    user_id = payload["user_id"]
    # query database for this user
    db_user = db.scalars(
        select(User).where(User.id == user_id)
    ).first()
    # return the user or raise error if not found
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    return db_user

# Determine whether user has owner access 
def permission_check(user_id: UUID, project_id: UUID, db_session):
    user_role = db_session.scalars( # Get user role for the project (if exists)
        select(User_Project.role).where(and_(
            user_id == User_Project.user_id, 
            project_id == User_Project.project_id))).first()
    if not user_role: # User is not an owner / not a part of the project
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized for the project"
        )
    return user_role