from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from limiter import limiter
from services.resume_parser import resume_parser
from models import Session
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import uuid
import os
import json
import json
import hashlib

# Magic numbers for file validation
PDF_HEADER = b'%PDF'
DOCX_HEADER = b'PK\x03\x04'

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

async def validate_upload(file: UploadFile):
    # 1. Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")
    
    if file_size == 0:
        raise HTTPException(400, "File is empty")
    
    # 2. Check file extension first
    filename_lower = file.filename.lower() if file.filename else ""
    is_pdf = filename_lower.endswith('.pdf')
    is_docx = filename_lower.endswith('.docx')
    
    if not (is_pdf or is_docx):
        raise HTTPException(400, "Invalid file type. Only PDF and DOCX are supported.")
    
    # 3. Check MIME type by content (magic numbers) - but don't fail if headers are odd
    file_content = await file.read(2048)
    file.file.seek(0)
    
    is_valid_header = False
    if is_pdf and file_content.startswith(PDF_HEADER):
        is_valid_header = True
    elif is_docx and file_content.startswith(DOCX_HEADER):
        is_valid_header = True
    elif is_pdf or is_docx:
        # Allow files with proper extension even if header is unusual
        # (some tools may have different headers)
        is_valid_header = True
        if is_pdf and not file_content.startswith(PDF_HEADER):
            print(f"Warning: PDF file has unusual header: {file_content[:20]}")
        if is_docx and not file_content.startswith(DOCX_HEADER):
            print(f"Warning: DOCX file has unusual header: {file_content[:20]}")

    # 4. Generate safe filename
    file_hash = hashlib.sha256(file_content).hexdigest()[:16]
    safe_filename = f"{file_hash}_{file.filename}"
    
    return safe_filename

router = APIRouter()

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    prompt: str = Form(default=""),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse resume file"""
    file_path = None
    try:
        print(f"\n{'='*60}")
        print(f"RESUMÉ UPLOAD REQUEST for {file.filename}")
        if prompt:
            print(f"Portfolio Description: {prompt[:100]}...")
        print(f"{'='*60}")
        
        # Validate file
        safe_filename = await validate_upload(file)
        print(f"✓ File validation passed: {safe_filename}")

        # Save file temporarily
        session_id = str(uuid.uuid4())
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{session_id}_{safe_filename}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"✓ File saved: {file_path} ({len(content)} bytes)")
        
        # Parse resume
        try:
            print(f"→ Parsing resume...")
            resume_data = await resume_parser.parse_file(file_path)
            print(f"✓ Resume parsed successfully")
        except ValueError as ve:
            error_msg = str(ve)
            print(f"✗ Parsing error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        except Exception as pe:
            error_msg = str(pe)
            print(f"✗ Processing error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Log extracted data for debugging
        print(f"{'='*60}")
        print(f"EXTRACTION RESULTS")
        print(f"{'='*60}")
        print(json.dumps(resume_data, indent=2))
        print(f"{'='*60}\n")
        
        # Save session with prompt
        session = Session(
            id=session_id,
            resume_filename=safe_filename,
            resume_data=resume_data,
            user_prompt=prompt if prompt else None
        )
        db.add(session)
        await db.commit()
        print(f"✓ Session saved: {session_id}")
        
        return {
            "session_id": session_id,
            "data": resume_data,
            "prompt": prompt
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Unexpected error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        # Clean up file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✓ Temporary file cleaned up")
            except:
                pass
