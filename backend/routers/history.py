from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db
from models import Project, User
from services.auth import auth_service
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = auth_service.verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

class ProjectResponse(BaseModel):
    id: str
    name: str
    stack: str
    created_at: datetime
    customization: Optional[dict] = None

@router.get("/", response_model=List[ProjectResponse])
async def get_user_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of generated portfolios for the current user"""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(desc(Project.created_at))
    )
    projects = result.scalars().all()
    
    return [
        ProjectResponse(
            id=p.id,
            name=p.name or "Untitled Portfolio",
            stack=p.stack,
            created_at=p.created_at,
            customization=p.customization
        )
        for p in projects
    ]
