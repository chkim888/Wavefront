from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from app.models.user import User
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