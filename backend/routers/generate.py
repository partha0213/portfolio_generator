from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.openai_service import openai_service
from services.template_engine import template_engine
from services.ai_template_generator import AITemplateGenerator
from services.template_registry import template_registry, TemplateStyle
from models import Session as DBSession, Project, User
from pydantic import BaseModel
from typing import Dict, Optional, List
import random
import os
from routers.history import get_current_user

router = APIRouter()

class GenerateRequest(BaseModel):
    session_id: str
    stack: str
    template_id: Optional[str] = None  # Specific template to use
    style: Optional[str] = None         # Preferred style (e.g., 'minimal', 'modern')
    options: Optional[Dict] = {}
    resume_data: Optional[Dict] = None  # Edited resume data from frontend

class UnlimitedTemplateRequest(BaseModel):
    """Request for AI-powered unlimited template generation"""
    framework: str
    style_description: str
    resume_data: Dict
    options: Optional[Dict] = {}

class CustomSectionRequest(BaseModel):
    """Request for generating custom portfolio sections"""
    framework: str
    section_type: str  # hero, about, skills, projects, contact, etc.
    style: str
    resume_data: Optional[Dict] = None

@router.post("/generate")
async def generate_portfolio(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate portfolio code using AI based on resume data"""
    
    # Get session data
    result = await db.execute(
        DBSession.__table__.select().where(DBSession.id == request.session_id)
    )
    session = result.fetchone()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Use edited resume data from frontend if provided, otherwise use original
    resume_data = request.resume_data if request.resume_data else session.resume_data
    print(f"📝 Using {'edited' if request.resume_data else 'original'} resume data")
    
    # Select template
    if request.template_id:
        # Use specific template if requested
        template_metadata = template_registry.get_template(request.template_id)
        if not template_metadata:
            raise HTTPException(status_code=400, detail=f"Template not found: {request.template_id}")
        template_id = request.template_id
        print(f"🎯 Using requested template: {template_id}")
    else:
        # Auto-select template based on style or randomize
        if request.style:
            try:
                style = TemplateStyle(request.style.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid style: {request.style}")
            
            template_id, template_metadata = template_registry.get_random_template(
                stack=request.stack,
                style=style
            )
            print(f"🎯 Selected template by style '{style.value}': {template_id}")
        else:
            # Fully random selection
            template_id, template_metadata = template_registry.get_random_template(
                stack=request.stack
            )
            print(f"🎯 Randomly selected template: {template_id}")
    
    # Get color scheme for template
    if 'primaryColor' not in request.options or 'secondaryColor' not in request.options:
        primary_color, secondary_color = template_registry.get_random_color_scheme(template_id)
        request.options['primaryColor'] = request.options.get('primaryColor', primary_color)
        request.options['secondaryColor'] = request.options.get('secondaryColor', secondary_color)
    
    print(f"\n{'='*60}")
    print(f"PORTFOLIO GENERATION")
    print(f"{'='*60}")
    print(f"Template: {template_metadata.name}")
    print(f"Style: {template_metadata.style.value}")
    print(f"Layout: {template_metadata.layout.value}")
    print(f"Animation Level: {template_metadata.animation_level}/3")
    print(f"Colors: {request.options['primaryColor']} → {request.options['secondaryColor']}")
    print(f"Stack: {request.stack}")
    print(f"{'='*60}\n")
    
    # Generate portfolio files using template engine
    files = template_engine.generate(
        stack=request.stack,
        data=resume_data,
        options=request.options,
        template_id=template_id
    )
    
    return {
        "files": files,
        "stack": request.stack,
        "template": {
            "id": template_id,
            "name": template_metadata.name,
            "style": template_metadata.style.value,
            "layout": template_metadata.layout.value,
            "features": template_metadata.features
        },
        "colors": {
            "primary": request.options['primaryColor'],
            "secondary": request.options['secondaryColor']
        }
    }

@router.get("/templates")
async def list_templates(
    stack: Optional[str] = None,
    style: Optional[str] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 20
):
    """List all available templates with metadata and pagination"""
    
    style_enum = None
    if style:
        try:
            style_enum = TemplateStyle(style.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid style: {style}")
    
    all_templates = template_registry.list_templates(stack=stack, style=style_enum)
    
    # Pagination
    total = len(all_templates)
    start = (page - 1) * limit
    end = start + limit
    paginated_templates = dict(list(all_templates.items())[start:end])
    
    return {
        "templates": [
            {
                "id": template_id,
                "name": metadata.name,
                "style": metadata.style.value,
                "layout": metadata.layout.value,
                "description": metadata.description,
                "animation_level": metadata.animation_level,
                "features": metadata.features,
                "supported_stacks": metadata.supported_stacks,
                "color_schemes": metadata.color_schemes
            }
            for template_id, metadata in paginated_templates.items()
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.post("/suggest-template")
async def suggest_template(
    prompt: str,
    stack: Optional[str] = None
):
    """Suggest a template based on user's description"""
    
    template_id, metadata = template_registry.suggest_template(prompt, stack)
    
    return {
        "suggested_template": {
            "id": template_id,
            "name": metadata.name,
            "style": metadata.style.value,
            "layout": metadata.layout.value,
            "description": metadata.description,
            "features": metadata.features
        }
    }


# ============= UNLIMITED TEMPLATE GENERATION (AI-Powered) =============

@router.post("/unlimited-template")
async def generate_unlimited_template(request: UnlimitedTemplateRequest):
    """Generate truly unlimited custom templates using AI - not constrained by presets"""
    
    print(f"\n{'='*60}")
    print(f"UNLIMITED TEMPLATE REQUEST")
    print(f"{'='*60}")
    print(f"Framework: {request.framework}")
    print(f"Style Description: {request.style_description}")
    print(f"{'='*60}\n")
    
    try:
        # Get the appropriate API key based on configuration
        use_gemini = os.getenv('USE_GEMINI', 'true').lower() == 'true'
        
        if use_gemini:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("⚠️  Gemini API key not configured, falling back to ChatGPT")
                api_key = os.getenv('OPENAI_API_KEY')
                use_gemini = False
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("⚠️  ChatGPT API key not configured, trying Gemini")
                api_key = os.getenv('GEMINI_API_KEY')
                use_gemini = True
        
        if not api_key:
            print("❌ ERROR: No AI API key configured (neither Gemini nor ChatGPT)")
            raise HTTPException(status_code=500, detail="AI API not configured")
        
        ai_service = "Gemini" if use_gemini else "ChatGPT"
        print(f"✓ {ai_service} API key found")
        print(f"→ Initializing AITemplateGenerator ({ai_service})...")
        
        ai_generator = AITemplateGenerator(api_key, use_chatgpt=not use_gemini)
        
        print(f"→ Generating unlimited template...")
        files = await ai_generator.generate_unlimited_template(
            framework=request.framework,
            style_description=request.style_description,
            user_data=request.resume_data,
            options=request.options
        )
        
        print(f"✓ Template generation complete")
        
        return {
            "status": "success",
            "framework": request.framework,
            "style": request.style_description,
            "files": files,
            "message": f"✨ Generated unlimited custom {request.framework} template"
        }
    
    except NotImplementedError as nie:
        error_msg = str(nie)
        print(f"\n❌ NOT IMPLEMENTED ERROR: {error_msg}")
        raise HTTPException(status_code=501, detail=f"Feature not implemented: {error_msg}")
    
    except Exception as e:
        error_msg = str(e)
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ UNEXPECTED ERROR in unlimited-template:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {error_msg}")
        print(f"Full Traceback:\n{error_trace}")
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Template generation failed: {error_msg}")


@router.post("/theme-variations")
async def generate_theme_variations(
    framework: str,
    num_variations: int = 5
):
    """Generate unlimited unique theme variations - each completely different"""
    
    try:
        use_gemini = os.getenv('USE_GEMINI', 'true').lower() == 'true'
        api_key = os.getenv('GEMINI_API_KEY') if use_gemini else os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY' if use_gemini else 'GEMINI_API_KEY')
            use_gemini = not use_gemini
        
        if not api_key:
            raise HTTPException(status_code=500, detail="AI API not configured")
        
        ai_generator = AITemplateGenerator(api_key, use_chatgpt=not use_gemini)
        
        variations = await ai_generator.generate_theme_variations(
            framework=framework,
            num_variations=num_variations
        )
        
        return {
            "status": "success",
            "framework": framework,
            "total_variations": len(variations),
            "variations": variations,
            "message": f"✨ Generated {len(variations)} unique theme variations"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theme generation failed: {str(e)}")


@router.post("/custom-section")
async def generate_custom_section(request: CustomSectionRequest):
    """Generate unlimited custom sections for any part of the portfolio"""
    
    try:
        use_gemini = os.getenv('USE_GEMINI', 'true').lower() == 'true'
        api_key = os.getenv('GEMINI_API_KEY') if use_gemini else os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY' if use_gemini else 'GEMINI_API_KEY')
            use_gemini = not use_gemini
        
        if not api_key:
            raise HTTPException(status_code=500, detail="AI API not configured")
        
        ai_generator = AITemplateGenerator(api_key)
        
        section_code = await ai_generator.generate_custom_section(
            framework=request.framework,
            section_type=request.section_type,
            style=request.style,
            user_data=request.resume_data
        )
        
        return {
            "status": "success",
            "framework": request.framework,
            "section_type": request.section_type,
            "code": section_code,
            "message": f"✨ Generated custom {request.section_type} section"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Section generation failed: {str(e)}")
