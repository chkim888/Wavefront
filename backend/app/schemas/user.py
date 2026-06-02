from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## User
class User(BaseModel): # Base class for User type
    username: str
    email: str

class UserCreate(User): # When new user is created
    password: str

class UserResponse(User): # What user gets in return
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

## Project
class Project(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(Project):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

## Users_Projects
class UsersProjects(BaseModel):
    user_id: UUID
    project_id: UUID
    role: Literal['owner', 'viewer']

class UsersProjectsResponse(UsersProjects):
    model_config = ConfigDict(from_attributes=True)