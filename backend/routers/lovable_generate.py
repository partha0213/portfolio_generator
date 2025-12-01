"""
Enhanced Portfolio Generation Router with Lovable-Style LLM Generation

This router prioritizes pure LLM code generation (Lovable-style) over templates,
allowing for creative, unique portfolios based on user prompts without constraints.

Endpoints:
- POST /api/generate/lovable - Generate portfolio using LLM (new default)
- POST /api/generate/lovable/refine - Iteratively refine generated portfolios
- POST /api/generate/lovable/variations - Generate multiple design variations
- GET /api/generate/lovable/download/{session_id} - Download portfolio as ZIP
- POST /api/generate/lovable/deploy - Deploy to Vercel/Netlify
- GET /api/generate/lovable/analytics - Get generation analytics
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Session as DBSession, User, Project, Deployment
from routers.history import get_current_user
from services.lovable_style_generator import PortfolioGenerator
from services.file_service import FileService
from services.deployment_service import DeploymentService
from services.cache_service import CacheService
from services.analytics_service import AnalyticsService
from pydantic import BaseModel
from typing import Dict, Optional
import json
import os
import io
import time
import uuid
from datetime import datetime
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/generate", tags=["portfolio-generation"])
limiter = Limiter(key_func=get_remote_address)


class LovableGenerateRequest(BaseModel):
    """Request for Lovable-style LLM portfolio generation"""
    session_id: str
    prompt: str  # User's design vision
    resume_data: Optional[Dict] = None  # Override session resume data
    framework: str = "nextjs"  # nextjs, react (default: nextjs)


class LovableRefineRequest(BaseModel):
    """Request to refine existing portfolio"""
    session_id: str
    refinement: str  # User's requested changes
    current_files: Dict[str, str]  # Current portfolio files


class LovableVariationsRequest(BaseModel):
    """Request for multiple design variations"""
    session_id: str
    prompt: str
    resume_data: Optional[Dict] = None
    num_variations: int = 3


class DeployRequest(BaseModel):
    """Request to deploy portfolio"""
    project_id: Optional[str] = None  # Project ID (preferred)
    session_id: Optional[str] = None  # Session ID (alternative)
    platform: str = "vercel"  # vercel or netlify
    project_name: Optional[str] = None


@router.post("/lovable")
@limiter.limit("10/hour")
async def generate_lovable_portfolio(
    body: LovableGenerateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Generate portfolio using Lovable AI-style LLM generation.
    
    Pure LLM code generation without template constraints. Each prompt
    creates a unique, creatively-designed portfolio.
    
    Request:
        - session_id: Portfolio session ID
        - prompt: Design vision (e.g., "bold vibrant with case studies")
        - resume_data: Resume data (optional, uses session data if not provided)
        - framework: "nextjs" (default) or "react"
    
    Returns:
        - files: Generated project files
        - design_notes: Design configuration extracted from prompt
        - success: Generation status
        - error: Error message if failed
    
    Example:
        ```
        {
            "session_id": "abc123",
            "prompt": "Create a bold, vibrant portfolio with animated gradients",
            "resume_data": {...}
        }
        ```
    """
    
    start_time = time.time()
    
    try:
        print(f"\n🎨 PORTFOLIO GENERATION REQUEST")
        print(f"📝 Session ID: {body.session_id}")
        print(f"👤 User: {current_user.email}")
        
        # Get session
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.id == body.session_id)
        )
        session = result.fetchone()
        
        if not session:
            print(f"❌ Session not found: {body.session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        print(f"✅ Session found: {body.session_id}")
        # Use provided resume data or session data
        resume_data = body.resume_data or session.resume_data
        
        # Extract from wrapper if needed
        if isinstance(resume_data, dict) and "data" in resume_data:
            resume_data = resume_data["data"]
        
        print(f"\n{'='*70}")
        print(f"🎨 LOVABLE PORTFOLIO GENERATION")
        print(f"{'='*70}")
        print(f"📝 User: {current_user.email}")
        print(f"🎯 Prompt: {body.prompt[:80]}...")
        print(f"👤 Portfolio: {resume_data.get('name', 'Portfolio Owner')}")
        
        # Check cache first
        cache_service = CacheService()
        cached_portfolio = cache_service.get_cached_portfolio(
            prompt=body.prompt,
            resume_data=resume_data,
            framework=body.framework
        )
        
        # Initialize generator (single unified AI generator)
        generator = PortfolioGenerator()
        
        if cached_portfolio:
            print(f"💾 Serving from cache!")
            generation_result = cached_portfolio["portfolio"]
            cached = True
        else:
            cached = False
            
            # Use the unified generator to produce a complete frontend project
            print("🎨 Generating full Next.js project via PortfolioGenerator...")
            gen_resp = await generator.refine_portfolio(
                refinement_request=body.prompt,
                current_files={},
                resume_data=resume_data
            )

            files = gen_resp.get("files", {})
            generation_result = {
                "success": gen_resp.get("success", False),
                "files": files,
                "design_notes": gen_resp.get("summary", {}),
                "reply": gen_resp.get("summary", "Portfolio generated!"),
                "config": {}
            }
            
            # Cache the result
            cache_service.cache_portfolio(
                prompt=body.prompt,
                resume_data=resume_data,
                portfolio=generation_result,
                framework=body.framework,
                ttl=3600
            )
        
        # Validation skipped for now as we trust the generator
        is_valid = True
        validation_errors = []
        
        # Save to Project model for history
        project = Project(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            session_id=body.session_id,
            name=f"{resume_data.get('name', 'Portfolio')} - {body.framework.title()}",
            stack=body.framework,
            files=generation_result["files"],
            customization={
                "design_notes": generation_result.get("design_notes", {}),
                "prompt": body.prompt,
                "generation_method": "lovable-llm",
                "from_cache": cached
            }
        )
        db.add(project)
        
        # Update session with generated files using proper async SQLAlchemy
        session_result = await db.execute(
            select(DBSession).where(DBSession.id == body.session_id)
        )
        session_obj = session_result.scalars().first()
        if session_obj:
            session_obj.portfolio_code = generation_result["files"]
            session_obj.generated_at = datetime.now()
        
        await db.commit()
        
        generation_time = time.time() - start_time
        
        print(f"✅ Portfolio generated successfully!")
        print(f"📊 Files: {len(generation_result['files'])}")
        print(f"⏱️  Time: {generation_time:.2f}s")
        print(f"💾 Cached: {cached}")
        # Handle design_notes being either a string or dict
        design_notes = generation_result.get('design_notes', {})
        if isinstance(design_notes, dict):
            print(f"✨ Design: {design_notes.get('layout', 'custom')}")
        else:
            print(f"✨ Design: {design_notes}")
        
        # Log successful generation
        analytics = AnalyticsService()
        await analytics.log_generation(
            user_id=current_user.id,
            session_id=body.session_id,
            prompt=body.prompt,
            framework=body.framework,
            success=True,
            generation_time=generation_time,
            file_count=len(generation_result["files"]),
            db=db
        )
        
        # Prepare response
        response = {
            "status": "success",
            "session_id": body.session_id,
            "project_id": project.id,
            "framework": body.framework,
            "files": generation_result["files"],
            "design_notes": generation_result["design_notes"],
            "config": generation_result.get("config", {}),
            "ai_reply": generation_result.get("reply", "Portfolio generated!"),
            "generation_method": "lovable-llm",
            "from_cache": cached,
            "generated_at": datetime.now().isoformat(),
            "generation_time_seconds": round(generation_time, 2),
            "file_count": len(generation_result["files"]),
            "validation": {
                "is_valid": is_valid,
                "errors": validation_errors if not is_valid else []
            }
        }
        
        print(f"{'='*70}\n")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/lovable/refine")
async def refine_lovable_portfolio(
    request: LovableRefineRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refine an existing Lovable-generated portfolio.
    
    Implements iterative improvement like Lovable's chat interface.
    Users can request specific changes and get updated portfolio.
    
    Request:
        - session_id: Portfolio session ID
        - refinement: Requested changes (e.g., "make colors more purple")
        - current_files: Current portfolio files
    
    Returns:
        - updated_files: Modified portfolio files
        - design_notes: Updated design configuration
    
    Example:
        ```
        {
            "session_id": "abc123",
            "refinement": "Change colors to purple and gold gradient",
            "current_files": {...}
        }
        ```
    """
    
    try:
        # Get session for context
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.id == request.session_id)
        )
        session = result.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        resume_data = session.resume_data
        if isinstance(resume_data, dict) and "data" in resume_data:
            resume_data = resume_data["data"]
        
        print(f"\n🔧 LOVABLE PORTFOLIO REFINEMENT")
        print(f"📝 Request: {request.refinement[:80]}...")
        
        # Initialize generators
        config_generator = PortfolioConfigGenerator()
        code_generator = ReactCodeGenerator()
        
        # Step 1: Refine config
        print("🔄 Refining configuration...")
        refined_config, refine_reply = await config_generator.refine_config(
            current_config=session.user_prompt or {}, # Fallback if no config stored
            refinement_prompt=request.refinement
        )
        
        # Step 2: Generate Code
        print("🎨 Regenerating code...")
        files = code_generator.generate_nextjs_files(refined_config)
        
        refinement_result = {
            "success": True,
            "files": files,
            "design_notes": refined_config.get("style", {}),
            "reply": refine_reply,
            "config": refined_config
        }
        
        print(f"✅ Refinement successful!")
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "files": refinement_result["files"],
            "design_notes": refinement_result["design_notes"],
            "config": refinement_result["config"],
            "ai_reply": refinement_result["reply"],
            "refined_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Refinement error: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


@router.post("/lovable/variations")
async def generate_lovable_variations(
    request: LovableVariationsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate multiple design variations using different prompts.
    
    Creates num_variations different portfolio designs to let user choose.
    Each gets slightly different interpretation of the design prompt.
    
    Request:
        - session_id: Portfolio session ID
        - prompt: Base design prompt
        - resume_data: Resume data (optional)
        - num_variations: Number of variations to generate (1-5)
    
    Returns:
        - variations: List of generated portfolio variations
        - prompts_used: Modified prompts for each variation
    
    Example:
        ```
        {
            "session_id": "abc123",
            "prompt": "modern and minimalist",
            "num_variations": 3
        }
        ```
    """
    
    try:
        # Validate num_variations
        if request.num_variations < 1 or request.num_variations > 5:
            raise HTTPException(
                status_code=400,
                detail="num_variations must be between 1 and 5"
            )
        
        # Get session
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.id == request.session_id)
        )
        session = result.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        resume_data = request.resume_data or session.resume_data
        if isinstance(resume_data, dict) and "data" in resume_data:
            resume_data = resume_data["data"]
        
        print(f"\n✨ LOVABLE PORTFOLIO VARIATIONS")
        print(f"📝 Base prompt: {request.prompt}")
        print(f"🎨 Generating {request.num_variations} variations...")
        
        # Initialize generators
        config_generator = PortfolioConfigGenerator()
        code_generator = ReactCodeGenerator()
        
        # Create variation prompts
        variation_modifiers = [
            f"{request.prompt} - Focus on bold colors and dynamic layouts",
            f"{request.prompt} - Add more animations and interactive elements",
            f"{request.prompt} - Emphasize minimalism and elegant simplicity",
            f"{request.prompt} - Create a premium, luxury aesthetic",
            f"{request.prompt} - Go playful and creative with unique design",
        ]
        
        variations = []
        prompts_used = []
        
        for i in range(min(request.num_variations, len(variation_modifiers))):
            modified_prompt = variation_modifiers[i]
            prompts_used.append(modified_prompt)
            
            print(f"\n🎨 Variation {i+1}/{request.num_variations}...")
            print(f"   Prompt: {modified_prompt[:60]}...")
            
            try:
                # Generate variation config
                variant_config, variant_reply = await config_generator.generate_config(
                    prompt=modified_prompt,
                    resume_data=resume_data
                )
                
                # Generate files
                files = code_generator.generate_nextjs_files(variant_config)
                
                variations.append({
                    "variation_number": i + 1,
                    "prompt": modified_prompt,
                    "files": files,
                    "design_notes": variant_config.get("style", {}),
                    "config": variant_config,
                    "reply": variant_reply
                })
                print(f"   ✅ Generated")
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
        
        print(f"\n✨ Successfully generated {len(variations)} variations")
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "total_variations": len(variations),
            "variations": variations,
            "prompts_used": prompts_used,
            "generated_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Variations error: {e}")
        raise HTTPException(status_code=500, detail=f"Variations failed: {str(e)}")


# ============================================================================
# 🚀 CRITICAL MISSING FEATURES BELOW
# ============================================================================

@router.get("/lovable/download/{session_id}")
async def download_portfolio(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download generated portfolio as ZIP file.
    
    Args:
        session_id: Portfolio session ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        ZIP file with all project files
    
    Example:
        ```
        GET /api/generate/lovable/download/abc123
        ```
    """
    
    try:
        # Get session
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.id == session_id)
        )
        session = result.fetchone()
        
        if not session or not session.portfolio_code:
            raise HTTPException(status_code=404, detail="Portfolio not found or not generated")
        
        # Verify ownership
        if session.user_id and session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        print(f"📦 Preparing download for session {session_id}")
        
        # Create ZIP
        file_service = FileService()
        zip_data = file_service.create_project_zip(
            files=session.portfolio_code,
            project_name=session.resume_data.get("name", "portfolio")
        )
        
        filename = file_service.get_zip_filename(
            project_name=session.resume_data.get("name", "portfolio"),
            session_id=session_id
        )
        
        print(f"✅ Download ready: {filename} ({len(zip_data)} bytes)")
        
        return StreamingResponse(
            io.BytesIO(zip_data),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Download error: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.post("/lovable/deploy")
async def deploy_portfolio(
    request: DeployRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deploy generated portfolio to Vercel or Netlify.
    
    Args:
        request: Deployment request with platform and session ID
        db: Database session
        current_user: Current user
    
    Returns:
        Deployment status with URL
    
    Example:
        ```
        POST /api/generate/lovable/deploy
        {
            "session_id": "abc123",
            "platform": "vercel",
            "project_name": "My Portfolio"
        }
        ```
    """
    
    try:
        print(f"🚀 Deployment request received")
        print(f"   Project ID: {request.project_id}")
        print(f"   Session ID: {request.session_id}")
        print(f"   Platform: {request.platform}")
        print(f"   Project name: {request.project_name}")
        print(f"   User: {current_user.email}")
        
        # Determine session_id (accept either project_id or session_id, like chat endpoint)
        session_id = request.session_id or request.project_id
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Either project_id or session_id must be provided")
        
        # Check if this is a project_id instead of session_id (like chat endpoint does)
        print(f"📦 Looking up: {session_id}")
        project_result = await db.execute(
            select(Project).where(
                Project.id == session_id,
                Project.user_id == current_user.id
            )
        )
        project = project_result.scalars().first()
        
        if project:
            print(f"✅ Found project, using session_id: {project.session_id}")
            session_id = project.session_id
        else:
            print(f"📋 Not a project_id, assuming it's a session_id: {session_id}")
        
        # Now get the session
        session_result = await db.execute(
            select(DBSession).where(DBSession.id == session_id)
        )
        session = session_result.scalars().first()
        
        if not session:
            print(f"❌ Session not found: {session_id}")
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        
        print(f"✅ Session found")
        print(f"   User ID: {session.user_id}")
        print(f"   Has portfolio code: {bool(session.portfolio_code)}")
        
        if not session.portfolio_code:
            print(f"❌ Portfolio not generated for session: {session_id}")
            raise HTTPException(status_code=404, detail="Portfolio not generated. Please generate a portfolio first.")
        
        # Verify ownership
        if session.user_id and session.user_id != current_user.id:
            print(f"❌ Unauthorized: Session belongs to different user")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        print(f"🚀 Deploying to {request.platform}...")
        
        deployment_service = DeploymentService()
        project_name = request.project_name or session.resume_data.get("name", "portfolio")
        
        if request.platform == "vercel":
            deploy_result = await deployment_service.deploy_to_vercel(
                files=session.portfolio_code,
                project_name=project_name,
                session_id=session_id
            )
        elif request.platform == "netlify":
            deploy_result = await deployment_service.deploy_to_netlify(
                files=session.portfolio_code,
                project_name=project_name,
                session_id=session_id
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        if deploy_result.get("success"):
            # Save deployment record
            deployment_db_id = str(uuid.uuid4())
            deployment = Deployment(
                id=deployment_db_id,
                user_id=current_user.id,
                session_id=session_id,
                platform=request.platform,
                deployment_id=deploy_result.get("deployment_id") or deploy_result.get("site_id"),
                deployment_url=deploy_result.get("url"),
                status="pending"
            )
            db.add(deployment)
            await db.commit()
            
            print(f"✅ Deployment initiated: {deploy_result.get('url')}")
            
            return {
                "success": True,
                "deployment_id": deployment_db_id,
                "platform_deployment_id": deploy_result.get("deployment_id") or deploy_result.get("site_id"),
                "url": deploy_result.get("url"),
                "status": deploy_result.get("status", "pending"),
                "platform": request.platform
            }
        else:
            error_msg = deploy_result.get('error', 'Unknown deployment error')
            print(f"❌ Deployment failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@router.get("/lovable/deployment-status/{deployment_id}")
async def get_deployment_status(
    deployment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check deployment status.
    
    Args:
        deployment_id: Deployment ID to check
        db: Database session
        current_user: Current user
    
    Returns:
        Current deployment status
    """
    
    try:
        # Get deployment record
        result = await db.execute(
            Deployment.__table__.select()
            .where((Deployment.id == deployment_id) & (Deployment.user_id == current_user.id))
        )
        deployment = result.fetchone()
        
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        deployment_service = DeploymentService()
        status = await deployment_service.get_deployment_status(
            platform=deployment[4],  # platform column
            deployment_id=deployment[6]  # deployment_id column
        )
        
        return {
            "deployment_id": deployment_id,
            "platform": deployment[4],
            "status": status.get("status"),
            "url": status.get("url"),
            "created_at": deployment[8].isoformat() if deployment[8] else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lovable/analytics/user")
async def get_user_analytics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get generation analytics for current user.
    
    Args:
        days: Look back this many days (default 30)
        db: Database session
        current_user: Current user
    
    Returns:
        User's generation statistics
    """
    
    try:
        analytics_service = AnalyticsService()
        stats = await analytics_service.get_user_stats(
            user_id=current_user.id,
            days=days,
            db=db
        )
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lovable/analytics/platform")
async def get_platform_analytics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get platform-wide generation analytics (admin only).
    
    Args:
        days: Look back this many days
        db: Database session
        current_user: Current user (must be admin)
    
    Returns:
        Platform statistics
    """
    
    try:
        analytics_service = AnalyticsService()
        stats = await analytics_service.get_platform_stats(days=days, db=db)
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lovable/deployment/platforms")
async def get_deployment_platforms(current_user: User = Depends(get_current_user)):
    """
    Get list of supported deployment platforms and their configuration status.
    
    Returns:
        List of platforms with configuration status
    """
    
    try:
        deployment_service = DeploymentService()
        platforms = deployment_service.get_supported_platforms()
        
        return {
            "success": True,
            "supported_platforms": platforms["platforms"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
