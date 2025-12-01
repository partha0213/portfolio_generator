# services/resume_parser.py

from pypdf import PdfReader
from docx import Document
import os
import json
from .groq_client import generate as groq_generate

class ResumeParser:
    """Parse resume files (PDF/DOCX) and extract structured data"""
    
    def __init__(self):
        # Configure Groq via environment variables
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_api_url = os.getenv("GROQ_API_URL")
        if self.groq_api_key and self.groq_api_url:
            print("✅ Groq configuration detected for resume parsing")
        else:
            print("⚠️ GROQ_API_KEY or GROQ_API_URL not found. Resume parsing will use fallback parser only.")
    
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
        
        # Use Groq AI to parse if configured
        if self.groq_api_key and self.groq_api_url:
            try:
                parsed_data = await self._parse_with_ai(text)
                return parsed_data
            except Exception as e:
                print(f"⚠️ Groq parsing failed: {e}. Using fallback.")
                return self._fallback_parse(text)

        return self._fallback_parse(text)
    
    async def _parse_with_ai(self, text: str) -> dict:
        """Parse resume text using Groq endpoint"""
        prompt = f"""Extract structured information from this resume and return ONLY valid JSON.

Resume Text:
{text}

Return JSON with this EXACT structure:
{{
  "data": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number or empty string",
    "title": "Professional Title/Role",
    "summary": "Professional summary (2-3 sentences)",
    "skills": ["skill1", "skill2", "skill3"],
    "experience": [
      {{
        "company": "Company Name",
        "title": "Job Title",
        "duration": "Start - End (e.g. 2020-2023)",
        "description": "What they did in this role"
      }}
    ],
    "projects": [
      {{
        "name": "Project Name",
        "description": "Project description",
        "technologies": ["tech1", "tech2"],
        "link": "URL or empty string"
      }}
    ],
    "education": [
      {{
        "school": "University Name",
        "degree": "Degree Name",
        "year": "Graduation Year or Duration"
      }}
    ],
    "links": {{
      "github": "URL or empty string",
      "linkedin": "URL or empty string",
      "portfolio": "URL or empty string",
      "twitter": "URL or empty string"
    }}
  }},
  "confidence": {{
    "name": 0.95,
    "email": 0.98,
    "skills": 0.85,
    "projects": 0.80
  }}
}}

RULES:
1. Return ONLY valid JSON, no markdown, no code blocks, no explanations
2. All fields must be present even if empty
3. Confidence scores: 0.9-1.0 for explicit data, 0.6-0.8 for inferred, <0.5 for guesses
4. If a field is not found, use empty string or empty array
5. Extract ALL skills mentioned in the resume
6. Extract ALL projects with as much detail as possible
"""

        try:
            resp = await groq_generate(prompt, return_json=True)

            # resp may be dict or string; normalize to dict
            if isinstance(resp, str):
                content = resp.strip()
                # strip markdown fences
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                parsed = json.loads(content)
            elif isinstance(resp, dict):
                # common provider shapes
                if "text" in resp and isinstance(resp["text"], str):
                    try:
                        parsed = json.loads(resp["text"])
                    except Exception:
                        parsed = resp
                else:
                    parsed = resp
            else:
                raise ValueError("Unexpected response type from Groq")

            if "data" not in parsed:
                return {"data": parsed, "confidence": {}, "needs_review": True}

            confidence_scores = parsed.get("confidence", {})
            needs_review = any(score < 0.7 for score in confidence_scores.values() if isinstance(score, (int, float)))

            return {"data": parsed["data"], "confidence": confidence_scores, "needs_review": needs_review}

        except Exception as e:
            print(f"⚠️ Groq parsing failed: {e}")
            raise e

    # OpenAI/Gemini removed: rely on Groq via _parse_with_ai or fallback parser
    
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
        """Fallback parser when AI fails or is unavailable"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Try to extract email
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Try to extract phone
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        
        return {
            "data": {
                "name": lines[0] if lines else "Unknown",
                "email": emails[0] if emails else "",
                "phone": phones[0] if phones else "",
                "title": "Developer",
                "summary": "",
                "skills": [],
                "projects": [],
                "experience": [],
                "education": [],
                "links": {
                    "github": "",
                    "linkedin": "",
                    "portfolio": "",
                    "twitter": ""
                }
            },
            "confidence": {
                "name": 0.5,
                "email": 0.8 if emails else 0.0,
                "skills": 0.0,
                "projects": 0.0
            },
            "needs_review": True
        }

# Singleton instance
resume_parser = ResumeParser()
