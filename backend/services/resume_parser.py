from pypdf import PdfReader
from docx import Document
from services.openai_service import openai_service
import os

class ResumeParser:
    """Parse resume files (PDF/DOCX) and extract structured data"""
    
    def __init__(self):
        self.openai = openai_service
    
    async def parse_file(self, file_path: str) -> dict:
        """Parse resume file and return structured data"""
        # Extract text
        try:
            if file_path.endswith('.pdf'):
                text = self._extract_pdf(file_path)
            elif file_path.endswith('.docx'):
                text = self._extract_docx(file_path)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            raise ValueError(f"Failed to extract text from file: {str(e)}")
        
        # Validate extracted text
        if not text or not text.strip():
            raise ValueError("Resume file appears to be empty or unreadable")
        
        # Use AI to parse
        parsed_data = await self.openai.parse_resume(text)
        return parsed_data or self._fallback_parse(text)
    
    def _extract_pdf(self, path: str) -> str:
        """Extract text from PDF"""
        try:
            reader = PdfReader(path)
            
            # Check if PDF is valid and has pages
            if not reader.pages:
                raise ValueError("PDF has no pages or is corrupted")
            
            text = ""
            extracted_count = 0
            failed_pages = 0
            
            for idx, page in enumerate(reader.pages):
                try:
                    extracted = page.extract_text()
                    if extracted and extracted.strip():
                        text += extracted + "\n"
                        extracted_count += 1
                except Exception as page_error:
                    failed_pages += 1
                    print(f"Warning: Could not extract text from page {idx}: {page_error}")
                    continue
            
            if extracted_count == 0:
                raise ValueError(f"Could not extract text from any of {len(reader.pages)} pages")
            
            if failed_pages > 0:
                print(f"Successfully extracted {extracted_count}/{len(reader.pages)} pages (skipped {failed_pages})")
                
            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")
    
    def _extract_docx(self, path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(path)
            paragraphs = [para.text for para in doc.paragraphs]
            
            if not paragraphs:
                raise ValueError("DOCX file has no text content")
            
            text = "\n".join(paragraphs)
            if not text.strip():
                raise ValueError("DOCX file appears to be empty")
                
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {str(e)}")
    
    def _fallback_parse(self, text: str) -> dict:
        """Fallback parser when AI fails"""
        lines = text.split('\n')
        return {
            "name": lines[0] if lines else "Unknown",
            "email": "",
            "title": "Developer",
            "summary": "",
            "skills": [],
            "projects": [],
            "experience": [],
            "education": []
        }

resume_parser = ResumeParser()
