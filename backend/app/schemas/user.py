from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## User
class UserBase(BaseModel): # Base class for User type
    username: str
    email: str

class UserCreate(UserBase): # When new user is created
    password: str

class UserResponse(UserBase): # What user gets in return
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

## Project
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

## Users_Projects
class UsersProjectsBase(BaseModel):
    user_id: UUID
    project_id: UUID
    role: Literal['owner', 'viewer']

class UsersProjectsResponse(UsersProjectsBase):
    model_config = ConfigDict(from_attributes=True)