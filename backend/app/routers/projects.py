from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from app.auth.dependencies import get_current_user
from app.schemas.user import ProjectBase, UsersProjectsBase, ProjectResponseWithRole, ProjectResponse, UsersProjectsResponse, ProjectUpdate
from app.models.user import Project, User_Project
from app.database import get_db_session

# Variables
OWNER = "owner"

# Router initialization
router = APIRouter(prefix="/projects")

## Create
# Create a new project & add the current user as the owner
@router.post("/project", response_model=ProjectResponse)
def create_project(project: ProjectBase, user=Depends(get_current_user), db_session = Depends(get_db_session)):
    # Check if there is already a project under the same name for the user
    duplicate_check = select(User_Project).where(
        and_(User_Project.user_id == user.id, 
             User_Project.project_id == select(Project.id).where(Project.name == project.name)))
    if (db_session.scalars(duplicate_check).first()):
        # return an error if there is a duplicate project
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There already exists a project with the same name under the user"
        )
    else:
        # Create a new project
        new_project = Project(
            name=project.name,
            description=project.description
        )
        db_session.add(new_project)
        db_session.commit()
        db_session.refresh(new_project)
        # Add the current user as the owner of the project
        new_role = User_Project(
            user_id=user.id,
            project_id=new_project.id,
            role=OWNER
        )
        db_session.add(new_role)
        db_session.commit()
        db_session.refresh(new_role)
        return new_project
    
# Assign a role for a user to a project
@router.post("/role", response_model=UsersProjectsResponse)
def assign_role(new_assignment: UsersProjectsBase, curr_user = Depends(get_current_user), db_session = Depends(get_db_session)):
    # Check if current user is an owner
    user_role = select(User_Project.role).where(and_(User_Project.user_id == curr_user.id, User_Project.project_id == new_assignment.project_id))
    if OWNER == db_session.scalars(user_role).first():
        # Skipping manual duplicate check -- will reject from DB since they're primary composite keys
        new_role = User_Project(
            user_id=new_assignment.user_id,
            project_id=new_assignment.project_id,
            role=new_assignment.role
        )
        db_session.add(new_role)
        db_session.commit()
        db_session.refresh(new_role)
        return new_role
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current user does not have permission to assign other users roles"
        )
            
## Read
# Read projects under current user (including user's )
@router.get("/all-projects", response_model=list[ProjectResponseWithRole])
def get_all_projects(user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Check all projects
    project_query = select(User_Project.project_id, User_Project.role).where(User_Project.user_id == user.id)
    all_projects = db_session.execute(project_query).all()
    result = list()
    for project_id, role in all_projects:
        project = db_session.scalars(select(Project).where(Project.id == project_id)).first()
        project_return = ProjectResponseWithRole(
            name=project.name,
            description=project.description,
            id=project_id,
            created_at=project.created_at,
            role=role
        )
        result.append(project_return)
    return result

# Get one project info
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_info(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Check if the user has access to the project
    permission_check = select(User_Project).where(and_(project_id == User_Project.project_id, user.id == User_Project.user_id))
    if not db_session.scalars(permission_check).first(): # user does not have access
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have access to the project"
        )
    else: # User has access
        project_to_return = db_session.scalars(select(Project).where(Project.id == project_id)).first()
        return project_to_return


# Get user's role for the project
@router.get("/role/{project_id}", response_model=UsersProjectsResponse)
def get_role(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Fetch user information for the project
    role_info = db_session.scalars(select(User_Project).where(
        and_(User_Project.project_id == project_id, User_Project.user_id == user.id)
    )).first()
    if not role_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have a role for the project"
        )
    else:
        return role_info

## Update
# Update project name or description
@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: UUID, update_info: ProjectUpdate, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # check user permission for the project
    user_role = select(User_Project.role).where(and_(User_Project.user_id == user.id, User_Project.project_id == project_id))    
    if OWNER == db_session.scalars(user_role).first():
        project = db_session.scalars(select(Project).where(Project.id == project_id)).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if update_info.name:
            # Check if project already exists with the same name
            all_user_projects = db_session.scalars(
                select(User_Project.project_id).where(User_Project.user_id == user.id)
            ).all()
            existing = db_session.scalars(
                select(Project).where(
                    and_(Project.name == update_info.name,
                         Project.id.in_(all_user_projects))
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project with the same name already in use"
                )
            project.name = update_info.name
        if update_info.description:
            project.description = update_info.description
        db_session.commit()
        db_session.refresh(project)
        return project
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have access to modify the project"
        )
    
## Delete
# Delete project
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Check user permission (owner?)
    user_role = select(User_Project.role).where(and_(User_Project.user_id == user.id, User_Project.project_id == project_id))
    if OWNER == db_session.scalars(user_role).first():
        project = select(Project).where(Project.id == project_id)
        db_session.delete(project)
        db_session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have access to delete the project"
        )
    
# Delete user from project
@router.delete("/role/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_from_project(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Check if user is in project
    check_user = select(User_Project).where(and_(User_Project.user_id == user.id, User_Project.project_id == project_id))
    user_returned = db_session.scalars(check_user).first()
    if not user_returned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in project"
        )
    else:
        db_session.delete(user_returned)
        db_session.commit()