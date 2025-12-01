from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db
from models import Project, User, Session, PortfolioSnapshot
from services.lovable_style_generator import PortfolioGenerator
from services.auth import auth_service
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import os
import json

router = APIRouter()
# Use HTTPBearer but don't auto-error so we can return controlled responses
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    """Verify JWT token and return current user"""
    # Log raw Authorization header and extracted credentials for debugging
    header_auth = request.headers.get('authorization')
    print(f"DEBUG: Raw Authorization header: {header_auth}")
    token = credentials.credentials if credentials else None
    print(f"DEBUG: Extracted credentials object: {credentials}")
    print(f"DEBUG: Received token: {token[:50] if token else 'None'}...")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = auth_service.verify_token(token)
    print(f"DEBUG: Payload after verification: {payload}")

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
    updatedAt: datetime
    status: str = "draft"
    description: str = ""
    framework: str = ""
    theme: str = "default"
    views: int = 0
    thumbnail: Optional[str] = None
    deploymentUrl: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    portfolios: List[ProjectResponse]


class SnapshotCreate(BaseModel):
    files: dict
    description: str = "Auto-save"


@router.get("", response_model=HistoryResponse)
@router.get("/", response_model=HistoryResponse, openapi_extra={"security": [{"Bearer": []}]})
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
    
    portfolios = [
        ProjectResponse(
            id=p.id,
            name=p.name or "Untitled Portfolio",
            stack=p.stack or "react",
            created_at=p.created_at,
            updatedAt=p.updated_at,
            status="draft",
            description="",
            framework=p.stack or "react",
            theme="default",
            views=0,
            thumbnail=None,
            deploymentUrl=None,
            url=None
        )
        for p in projects
    ]
    
    return HistoryResponse(portfolios=portfolios)


@router.get("/debug/sessions")
async def debug_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint: List all sessions for current user"""
    result = await db.execute(
        select(Session)
        .where(Session.user_id == current_user.id)
        .order_by(desc(Session.created_at))
    )
    sessions = result.scalars().all()
    
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "session_count": len(sessions),
        "sessions": [
            {
                "id": s.id,
                "resume_filename": s.resume_filename,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "user_prompt": s.user_prompt[:100] if s.user_prompt else None
            }
            for s in sessions
        ]
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()
    
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/duplicate")
async def duplicate_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate a project"""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create a new project as a duplicate
    new_project = Project(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        session_id=project.session_id,
        name=f"{project.name or 'Untitled Portfolio'} (Copy)",
        stack=project.stack,
        files=project.files,
        customization=project.customization
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return ProjectResponse(
        id=new_project.id,
        name=new_project.name,
        stack=new_project.stack,
        created_at=new_project.created_at,
        updatedAt=new_project.updated_at,
        status="draft",
        description="",
        framework=new_project.stack or "react",
        theme="default",
        views=0,
        thumbnail=None,
        deploymentUrl=None,
        url=None
    )


# --- Snapshot / Undo-Redo Endpoints ---


@router.post("/sessions/{session_id}/snapshot")
async def save_snapshot(
    session_id: str, 
    snapshot: SnapshotCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Save a snapshot of the current portfolio state"""
    # Verify session exists
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Calculate size
    files_json = json.dumps(snapshot.files)
    size_bytes = len(files_json.encode('utf-8'))

    # Create snapshot
    new_snapshot = PortfolioSnapshot(
        id=str(uuid.uuid4()),
        session_id=session_id,
        files=snapshot.files,
        description=snapshot.description,
        size_bytes=size_bytes
    )
    
    db.add(new_snapshot)
    await db.commit()
    await db.refresh(new_snapshot)
    
    return {
        "id": new_snapshot.id,
        "created_at": new_snapshot.created_at,
        "size_bytes": size_bytes
    }


@router.get("/sessions/{session_id}/snapshots")
async def get_snapshots(
    session_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """Get all snapshots for a session"""
    result = await db.execute(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.session_id == session_id)
        .order_by(desc(PortfolioSnapshot.created_at))
    )
    snapshots = result.scalars().all()
    
    return [
        {
            "id": s.id,
            "created_at": s.created_at,
            "description": s.description,
            "size_bytes": s.size_bytes
        }
        for s in snapshots
    ]


@router.get("/sessions/{session_id}/snapshot/{snapshot_id}")
async def get_snapshot_content(
    session_id: str,
    snapshot_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the full content of a specific snapshot"""
    result = await db.execute(
        select(PortfolioSnapshot)
        .where(
            PortfolioSnapshot.session_id == session_id,
            PortfolioSnapshot.id == snapshot_id
        )
    )
    snapshot = result.scalars().first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
        
    return {
        "id": snapshot.id,
        "files": snapshot.files,
        "created_at": snapshot.created_at
    }


@router.post("/sessions/{session_id}/snapshots/dev-create")
async def create_sample_snapshot(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Create a sample PortfolioSnapshot for the given session using the ReactCodeGenerator.

    This is intended for development/testing so the frontend can fetch snapshots
    without going through the full generation flow.
    """
    # Verify session exists
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Generate sample files using the unified PortfolioGenerator
    try:
        generator = PortfolioGenerator()
        # Pass hint author/name when available
        author = None
        if session.resume_data and isinstance(session.resume_data, dict):
            author = session.resume_data.get('name') or session.resume_data.get('full_name')

        gen_resp = await generator.refine_portfolio(
            refinement_request="Create a small, dev-friendly Next.js portfolio sample",
            current_files={},
            resume_data={"name": author or "Dev User"}
        )
        files = gen_resp.get('files', {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generator error: {str(e)}")

    size_bytes = len(json.dumps(files).encode('utf-8'))

    new_snapshot = PortfolioSnapshot(
        id=str(uuid.uuid4()),
        session_id=session_id,
        files=files,
        description="Dev sample snapshot",
        size_bytes=size_bytes,
    )

    db.add(new_snapshot)
    await db.commit()
    await db.refresh(new_snapshot)

    return {
        "id": new_snapshot.id,
        "created_at": new_snapshot.created_at,
        "size_bytes": size_bytes
    }


@router.post("/sessions/dev/create")
async def create_dev_session(
    session_id: Optional[str] = None,
    resume_data: Optional[dict] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Dev-only helper: create a session for testing snapshots/UI flows.

    If `SESSION_DEV_ALLOWED` env var is set to '1' this endpoint will run;
    otherwise it's still available but should be used only in development.
    """
    # Simple guard — optionally require an env var for safety
    dev_allowed = os.getenv("SESSION_DEV_ALLOWED", "1")
    if dev_allowed != "1":
        raise HTTPException(status_code=403, detail="Dev session creation disabled")

    sid = session_id or str(uuid.uuid4())
    new_session = Session(
        id=sid,
        user_id=user_id,
        resume_filename="dev_resume.json",
        resume_data=resume_data or {"name": "Dev User"},
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return {
        "id": new_session.id,
        "created_at": new_session.created_at,
        "resume_data": new_session.resume_data
    }
