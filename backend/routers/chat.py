from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from services.groq_client import generate as groq_generate
from services.lovable_style_generator import PortfolioGenerator
import uuid
from models import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Session as DBSession
import json
import re
import os

router = APIRouter()

# Store active portfolio chat sessions (lightweight adapter)
class SimplePortfolioChatService:
    def __init__(self, api_key: Optional[str] = None):
        self.generator = PortfolioGenerator()
        self.conversation_history: List[Dict] = []
        self.user_data: Dict = {}

    def add_system_context(self, user_data: Dict):
        self.user_data = user_data or {}

    async def chat(self, message: str) -> Dict:
        # Use PortfolioGenerator to create a concise response summary
        resp = await self.generator.refine_portfolio(
            refinement_request=message,
            current_files={},
            resume_data=self.user_data
        )
        summary = resp.get('summary') or resp.get('thought') or ''
        self.conversation_history.append({"role":"user","content":message})
        self.conversation_history.append({"role":"assistant","content":summary})
        return {"response": summary, "code_suggestions": [], "design_tips": []}

    async def get_quick_tips(self) -> Dict:
        return {"tips": ["Improve hero section", "Add case studies", "Optimize images"]}

    async def get_design_suggestions(self, focus_area: str) -> Dict:
        return {"suggestions": [{"title": f"Improve {focus_area}", "detail": "Use clearer hierarchy"}], "code_snippets": []}

    async def get_advanced_code_generation(self, request: str) -> Dict:
        resp = await self.generator.refine_portfolio(request, {}, self.user_data)
        return {"code": resp.get('files', {}), "explanation": resp.get('summary', '')}

    async def get_design_strategy(self) -> Dict:
        return {"color_strategy": "Use a primary color with high contrast", "typography": "Use system fonts and scale for hierarchy"}

    async def get_multiple_approaches(self, feature: str) -> Dict:
        return {"approaches": [{"level": "quick", "description": f"Simple {feature} change"}, {"level": "full", "description": f"Rebuild {feature} for performance"}]}


portfolio_chat_sessions: Dict[str, SimplePortfolioChatService] = {}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: str
    current_files: Optional[Dict[str, str]] = None

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Stream chat responses for real-time UI with rich events"""
    try:
        # Get session data for context
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.id == request.session_id)
        )
        session = result.fetchone()
        
        if not session:
            # Fallback for new sessions or testing
            resume_data = {}
        else:
            resume_data = session.resume_data
        
        # Get latest user message
        user_message = request.messages[-1].content if request.messages else ""
        
        async def generate_events():
            try:
                # Stream events from the generator
                async for event in generator.stream_refine_portfolio(
                    refinement_request=user_message,
                    current_files=request.current_files or {},
                    resume_data=resume_data
                ):
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                error_event = {"type": "error", "message": str(e)}
                yield f"data: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            generate_events(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no", # Disable buffering for Nginx/proxies
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from services import LovableStyleGenerator

# Initialize generator
generator = LovableStyleGenerator()

@router.post("/")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Code-aware chat endpoint that can modify files"""
    try:
        # Get session data for context
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.id == request.session_id)
        )
        session = result.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        resume_data = session.resume_data
        
        # Get latest user message
        user_message = request.messages[-1].content if request.messages else ""
        
        # Use PortfolioGenerator to refine the portfolio
        result = await generator.refine_portfolio(
            refinement_request=user_message,
            current_files=request.current_files or {},
            resume_data=resume_data
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
        # Extract data from result
        assistant_response = result.get("summary", "I've updated your portfolio.")
        thought = result.get("thought")
        file_changes = result.get("refined_files", {})
        tools_used = result.get("tools_used", [])
        edits_made = result.get("edits_made", [])
        thought_time = result.get("thought_time", 0)
        
        # Save to database
        # Note: We currently store simple file_changes map in DB. 
        # Detailed tools/edits are returned to UI but not yet persisted in their own columns.
        chat_entry = ChatHistory(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            user_id=request.session_id, # Temporary: using session_id as user_id if no auth
            role="assistant",
            message=assistant_response,
            thought=thought,
            file_changes=file_changes
        )
        db.add(chat_entry)
        await db.commit()
        
        return {
            "success": True,
            "response": assistant_response,
            "thought": thought,
            "thought_time": thought_time,
            "file_changes": file_changes,
            "tools_used": tools_used,
            "edits_made": edits_made,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def initialize_portfolio_chat(session_id: str, user_data: Dict) -> Dict:
    """Initialize a new portfolio improvement chat session"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        chat_service = PortfolioChatService(api_key)
        chat_service.add_system_context(user_data)

        portfolio_chat_sessions[session_id] = chat_service

        return {
            'status': 'initialized',
            'session_id': session_id,
            'message': '✨ Welcome! I\'m here to help you create a stunning portfolio. What would you like to improve?',
            'suggestions': [
                'Improve the hero section',
                'Enhance color scheme',
                'Add animations',
                'Better typography',
                'Improve responsiveness'
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")


@router.post("/portfolio/improve")
async def improve_portfolio(request: Dict):
    """Get portfolio improvement suggestions through conversation"""
    try:
        session_id = request.get("session_id")
        message = request.get("message")
        user_data = request.get("user_data")
        
        # Initialize session if needed
        if session_id not in portfolio_chat_sessions:
            if not user_data:
                raise HTTPException(status_code=404, detail="Session not found and no user data provided")

            chat_service = SimplePortfolioChatService()
            chat_service.add_system_context(user_data)
            portfolio_chat_sessions[session_id] = chat_service

        chat_service = portfolio_chat_sessions[session_id]
        response = await chat_service.chat(message)
        
        return {
            'response': response['response'],
            'code_suggestions': response.get('code_suggestions'),
            'design_tips': response.get('design_tips'),
            'next_steps': response.get('next_steps'),
            'conversation_length': len(chat_service.conversation_history)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/portfolio/quick-tips")
async def get_portfolio_tips(session_id: str, user_data: Optional[Dict] = None) -> Dict:
    """Get quick portfolio improvement tips"""
    try:
        if session_id not in portfolio_chat_sessions:
            if not user_data:
                raise HTTPException(status_code=404, detail="Session not found")
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
            chat_service = PortfolioChatService(api_key)
            chat_service.add_system_context(user_data)
            portfolio_chat_sessions[session_id] = chat_service
        
            chat_service = portfolio_chat_sessions[session_id]
            tips = await chat_service.get_quick_tips()
        
        return tips
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/portfolio/focus-suggestions")
async def get_focus_suggestions(session_id: str, focus_area: str) -> Dict:
    """Get detailed suggestions for a specific portfolio area"""
    try:
        if session_id not in portfolio_chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found. Initialize first.")
        
            chat_service = portfolio_chat_sessions[session_id]
            suggestions = await chat_service.get_design_suggestions(focus_area)
        
        return {
            'focus_area': focus_area,
            'suggestions': suggestions['suggestions'],
            'code_snippets': suggestions.get('code_snippets', [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/portfolio/history/{session_id}")
async def get_portfolio_chat_history(session_id: str) -> Dict:
    """Get conversation history"""
    try:
        if session_id not in portfolio_chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        chat_service = portfolio_chat_sessions[session_id]
        history = chat_service.get_conversation_history()
        
        return {
            'session_id': session_id,
            'messages': history,
            'message_count': len(history)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/portfolio/session/{session_id}")
async def close_portfolio_session(session_id: str) -> Dict:
    """Close a portfolio chat session"""
    try:
        if session_id in portfolio_chat_sessions:
            del portfolio_chat_sessions[session_id]
        
        return {
            'status': 'closed',
            'session_id': session_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============= Advanced/Extensive AI Features =============

@router.post("/portfolio/advanced-code")
async def get_advanced_code_generation(session_id: str, request: str, user_data: Optional[Dict] = None) -> Dict:
    """Generate advanced, production-quality code"""
    try:
        if session_id not in portfolio_chat_sessions:
            if not user_data:
                raise HTTPException(status_code=404, detail="Session not found")

            chat_service = SimplePortfolioChatService()
            chat_service.add_system_context(user_data)
            portfolio_chat_sessions[session_id] = chat_service

        chat_service = portfolio_chat_sessions[session_id]
        result = await chat_service.get_advanced_code_generation(request)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/portfolio/design-strategy")
async def get_design_strategy(session_id: str, user_data: Optional[Dict] = None) -> Dict:
    """Get comprehensive design strategy"""
    try:
        if session_id not in portfolio_chat_sessions:
            if not user_data:
                raise HTTPException(status_code=404, detail="Session not found")

            chat_service = SimplePortfolioChatService()
            chat_service.add_system_context(user_data)
            portfolio_chat_sessions[session_id] = chat_service

        chat_service = portfolio_chat_sessions[session_id]
        strategy = await chat_service.get_design_strategy()
        
        return strategy
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/portfolio/multiple-approaches")
async def get_multiple_approaches(session_id: str, feature: str, user_data: Optional[Dict] = None) -> Dict:
    """Generate multiple implementation approaches"""
    try:
        if session_id not in portfolio_chat_sessions:
            if not user_data:
                raise HTTPException(status_code=404, detail="Session not found")

            chat_service = SimplePortfolioChatService()
            chat_service.add_system_context(user_data)
            portfolio_chat_sessions[session_id] = chat_service

        chat_service = portfolio_chat_sessions[session_id]
        approaches = await chat_service.get_multiple_approaches(feature)
        
        return approaches
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
