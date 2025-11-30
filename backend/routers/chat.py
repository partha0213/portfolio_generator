from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from services.openai_service import openai_service
from services.portfolio_chat_service import PortfolioChatService
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Session as DBSession
import json
import re
import os

router = APIRouter()

# Store active portfolio chat sessions
portfolio_chat_sessions: Dict[str, PortfolioChatService] = {}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: str
    current_files: Optional[Dict[str, str]] = None

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat responses for real-time UI"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        async def generate():
            async for chunk in openai_service.stream_chat(messages):
                yield f"data: {json.dumps({'content': chunk})}\\n\\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Build system prompt with code context
        system_prompt = f"""You are an expert portfolio developer assistant. You help users customize their portfolio code.

Current portfolio files: {list(request.current_files.keys()) if request.current_files else []}

Resume data: {json.dumps(resume_data, indent=2)}

When the user asks to modify the code (e.g., "change to dark theme", "make text bigger", "change colors"):
1. Provide a brief explanation of what you're changing
2. On a new line, write: FILE_CHANGE: <filename>
3. Then provide the complete modified file content wrapped in ```
4. You can modify multiple files if needed

Example response format:
"I'll update your portfolio to a dark theme with darker backgrounds and lighter text.

FILE_CHANGE: src/index.css
```css
:root {{
  --bg-dark: #0a0a0a;
  --text-light: #f0f0f0;
}}
...
```"

Always provide COMPLETE file contents, not just the changes."""

        # Prepare messages with system prompt
        chat_messages = [{"role": "system", "content": system_prompt}]
        chat_messages.extend([{"role": msg.role, "content": msg.content} for msg in request.messages])
        
        # Get AI response
        full_response = ""
        async for chunk in openai_service.stream_chat(chat_messages):
            full_response += chunk
        
        # Parse response for file changes
        file_changes = {}
        response_text = full_response
        
        # Extract file changes using regex
        file_pattern = r'FILE_CHANGE:\s*([^\n]+)\n```(?:css|javascript|jsx)?\n(.*?)```'
        matches = re.findall(file_pattern, full_response, re.DOTALL)
        
        for filename, content in matches:
            filename = filename.strip()
            file_changes[filename] = content.strip()
        
        # Remove file change syntax from response text for cleaner display
        response_text = re.sub(r'FILE_CHANGE:.*?```(?:css|javascript|jsx)?\n.*?```', '', full_response, flags=re.DOTALL).strip()
        
        return {
            "response": response_text or full_response,
            "file_changes": file_changes if file_changes else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Portfolio Improvement Chat Endpoints =============

@router.post("/portfolio/initialize")
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
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
            chat_service = PortfolioChatService(api_key)
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
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
            chat_service = PortfolioChatService(api_key)
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
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
            chat_service = PortfolioChatService(api_key)
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
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
            chat_service = PortfolioChatService(api_key)
            chat_service.add_system_context(user_data)
            portfolio_chat_sessions[session_id] = chat_service
        
        chat_service = portfolio_chat_sessions[session_id]
        approaches = await chat_service.get_multiple_approaches(feature)
        
        return approaches
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
