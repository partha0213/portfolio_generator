import os
from openai import OpenAI
from config import settings
from typing import Dict, List, AsyncGenerator
import json

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"
    
    async def stream_chat(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Stream chat responses for real-time UI updates"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def parse_resume(self, text: str) -> Dict:
        """Extract structured data from resume text using AI"""
        prompt = f"""Extract information from this resume and return ONLY valid JSON.

Resume:
{text}

Return JSON with this structure:
{{
  "data": {{
      "name": "Full Name",
      "email": "email@example.com",
      "phone": "phone number",
      "title": "Professional Title",
      "summary": "Professional summary",
      "skills": ["skill1", "skill2"],
      "experience": [
        {{"company": "Company", "title": "Job Title", "duration": "2020-2023", "description": "What you did"}}
      ],
      "projects": [
        {{"name": "Project Name", "description": "What it does", "technologies": ["tech1", "tech2"], "link": "url"}}
      ],
      "education": [
        {{"school": "University", "degree": "Degree", "year": "2020"}}
      ],
      "links": {{
        "github": "url",
        "linkedin": "url",
        "portfolio": "url"
      }}
  }},
  "confidence": {{
    "name": 0.95,
    "email": 0.98,
    "skills": 0.75,
    "projects": 0.8
  }}
}}

Confidence scores should be 0-1 based on how clearly the information was stated in the resume. Use 1.0 for explicit matches, 0.5-0.8 for inferred data, and < 0.5 for guesses."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a resume parser. Return only valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            parsed = json.loads(content)
            
            # Handle potential structure mismatch if model ignores instruction
            if "data" not in parsed:
                return {
                    "data": parsed,
                    "confidence": {},
                    "needs_review": True
                }
            
            return {
                "data": parsed["data"],
                "confidence": parsed.get("confidence", {}),
                "needs_review": any(score < 0.7 for score in parsed.get("confidence", {}).values())
            }
        except Exception as e:
            print(f"[ERROR] OpenAI parsing failed: {e}")
            return None
    
    async def customize_template(self, template_code: str, data: Dict, customization: Dict) -> str:
        """Use AI to customize template with user data and preferences"""
        prompt = f"""Customize this portfolio template with the user's data.

Template: {template_code[:500]}...

User Data:
{json.dumps(data, indent=2)}

Customization:
{json.dumps(customization, indent=2)}

Return the customized code maintaining the same structure."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code customization assistant. Return only code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except:
            return template_code  # Fallback to original
    
    async def generate_portfolio_code(self, prompt: str, resume_data: Dict, stack: str) -> Dict:
        """Generate complete portfolio code using AI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert web developer. Generate complete, working portfolio code. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            return json.loads(content)
        except Exception as e:
            print(f"[ERROR] AI code generation failed: {e}")
            return None

openai_service = OpenAIService()
