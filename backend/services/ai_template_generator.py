from typing import Dict, List, Optional
from openai import OpenAI
import json
import re
import html
from datetime import datetime
import os

class AITemplateGenerator:
    """Advanced AI-powered portfolio template generator with Gemini and ChatGPT support"""
    
    def __init__(self, api_key: str, use_chatgpt: bool = False):
        """
        Initialize AI Template Generator
        
        Args:
            api_key: API key for the AI service (OpenAI or Google)
            use_chatgpt: If True, use ChatGPT; otherwise use Gemini (default)
        """
        self.use_chatgpt = use_chatgpt
        self.api_key = api_key
        self.max_retries = 3
        
        if use_chatgpt:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"
        else:
            # Gemini setup - will be configured via environment
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Use gemini-pro which is more widely available
            self.model = "gemini-pro"
            self.gemini_client = genai.GenerativeModel(self.model)
        
    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent prompt injection"""
        if not text:
            return ''
        # Escape special characters and remove potential injection attempts
        text = html.escape(str(text).strip())
        # Remove prompt injection patterns
        dangerous_patterns = [
            r'ignore\s+previous',
            r'disregard\s+above',
            r'system\s*:',
            r'assistant\s*:',
            r'<\s*script',
        ]
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def _validate_user_data(self, user_data: Dict) -> Dict:
        """Validate and sanitize user data with sensible defaults"""
        # Provide defaults for missing fields
        sanitized = {
            'name': self._sanitize_input(user_data.get('name', 'John Doe')),
            'title': self._sanitize_input(user_data.get('title', 'Developer')),
            'email': user_data.get('email', 'email@example.com'),
            'phone': self._sanitize_input(user_data.get('phone', '')),
            'summary': self._sanitize_input(user_data.get('summary', '')),
            'skills': [self._sanitize_input(s) for s in user_data.get('skills', [])],
            'projects': self._sanitize_projects(user_data.get('projects', [])),
            'education': self._sanitize_education(user_data.get('education', [])),
            'links': self._sanitize_links(user_data.get('links', {}))
        }
        
        return sanitized
    
    def _sanitize_projects(self, projects: List[Dict]) -> List[Dict]:
        """Sanitize project data"""
        sanitized = []
        for proj in projects:
            sanitized.append({
                'name': self._sanitize_input(proj.get('name', 'Project')),
                'description': self._sanitize_input(proj.get('description', '')),
                'technologies': [self._sanitize_input(t) for t in proj.get('technologies', [])],
                'link': self._sanitize_url(proj.get('link', '')),
                'role': self._sanitize_input(proj.get('role', 'Developer')),
                'year': self._sanitize_input(proj.get('year', '2024'))
            })
        return sanitized
    
    def _sanitize_education(self, education: List[Dict]) -> List[Dict]:
        """Sanitize education data"""
        return [{
            'school': self._sanitize_input(edu.get('school', 'University')),
            'degree': self._sanitize_input(edu.get('degree', 'Degree')),
            'year': self._sanitize_input(edu.get('year', ''))
        } for edu in education]
    
    def _sanitize_links(self, links: Dict) -> Dict:
        """Sanitize social links"""
        return {
            'github': self._sanitize_url(links.get('github', '')),
            'linkedin': self._sanitize_url(links.get('linkedin', '')),
            'portfolio': self._sanitize_url(links.get('portfolio', '')),
            'twitter': self._sanitize_url(links.get('twitter', ''))
        }
    
    def _sanitize_url(self, url: str) -> str:
        """Validate and sanitize URLs"""
        if not url:
            return ''
        url = str(url).strip()
        if not (url.startswith('http://') or url.startswith('https://')):
            return ''
        return url
    
    def _build_comprehensive_prompt(
        self,
        framework: str,
        style_description: str,
        user_data: Dict,
        options: Dict
    ) -> str:
        """Build detailed prompt for AI generation"""
        
        # Format data for prompt
        projects_json = json.dumps(user_data['projects'][:8], indent=2)
        education_json = json.dumps(user_data['education'][:5], indent=2)
        skills_json = json.dumps(user_data['skills'][:20], indent=2)
        
        # Color scheme
        primary_color = options.get('primaryColor', '#667eea')
        secondary_color = options.get('secondaryColor', '#764ba2')
        
        prompt = f"""You are an expert web developer creating a professional portfolio website.

**USER DATA (MUST USE EXACTLY AS PROVIDED):**

Personal Information:
- Name: {user_data['name']}
- Title/Role: {user_data['title']}
- Email: {user_data['email']}
- Phone: {user_data['phone']}
- Summary/Bio: {user_data['summary']}

Skills (use ALL {len(user_data['skills'])} skills):
{skills_json}

Projects (use ALL {len(user_data['projects'])} projects with complete details):
{projects_json}

Education (use ALL {len(user_data['education'])} entries):
{education_json}

Social Links:
- GitHub: {user_data['links']['github']}
- LinkedIn: {user_data['links']['linkedin']}
- Portfolio: {user_data['links']['portfolio']}

**DESIGN REQUIREMENTS:**

Framework: {framework}
Style: {style_description}
Color Scheme:
- Primary: {primary_color}
- Secondary: {secondary_color}

**CRITICAL RULES (FAILURE = REJECTION):**

1. DATA USAGE:
   ✓ Use "{user_data['name']}" NOT "John Doe" or any placeholder
   ✓ Use "{user_data['title']}" NOT generic "Developer"
   ✓ Display ALL {len(user_data['projects'])} projects with real names
   ✓ Display ALL {len(user_data['skills'])} skills (no generic React/JS only)
   ✓ Use actual email: {user_data['email']}
   ✓ Include ALL education entries with exact details

2. PROJECT SECTION REQUIREMENTS:
   ✓ Show each project with: name, description, technologies, role, year
   ✓ If project.link exists, add "View Project" button
   ✓ Use placeholder images: https://via.placeholder.com/600x400?text=ProjectName
   ✓ Display technologies as tags/badges

3. IMAGE HANDLING:
   ✓ ALL images must use HTTPS URLs (external)
   ✓ Project images: https://via.placeholder.com/600x400?text={{ProjectName}}
   ✓ Background images: https://images.unsplash.com/...
   ✓ NO local file paths (/assets/, ./images/, etc.)

4. CODE STRUCTURE ({framework}):
   ✓ package.json with correct dependencies
   ✓ index.html with proper structure
   ✓ src/App.jsx (or .tsx) with complete component
   ✓ src/styles.css with responsive design
   ✓ For React: Use CDN imports in HTML OR npm packages in package.json
   ✓ Component must export default and mount to #root

5. SECTIONS TO INCLUDE:
   ✓ Hero (name, title, summary, CTA buttons)
   ✓ About (detailed bio/summary)
   ✓ Skills (categorized by type if possible)
   ✓ Projects (all projects with details)
   ✓ Education (all entries)
   ✓ Contact (email, phone, social links)
   ✓ Footer (copyright, social icons)

6. RESPONSIVE DESIGN:
   ✓ Mobile-first approach
   ✓ Works on: mobile (320px+), tablet (768px+), desktop (1024px+)
   ✓ Hamburger menu for mobile navigation

7. UI/UX BEST PRACTICES:
   ✓ Smooth scroll navigation
   ✓ Hover effects and transitions
   ✓ Professional color scheme
   ✓ Accessible (ARIA labels, semantic HTML)
   ✓ Fast loading (optimized CSS)

**OUTPUT FORMAT:**

Return ONLY valid JSON (no markdown, no code blocks):

{{
  "package.json": "{{...}}",
  "index.html": "<!DOCTYPE html>...",
  "src/App.jsx": "import React from 'react'...",
  "src/styles.css": "* {{ margin: 0; ... }}",
  "README.md": "# Portfolio for {user_data['name']}"
}}

**VERIFICATION BEFORE RETURNING:**

Before you return the code, verify:
1. ✓ Name "{user_data['name']}" appears at least 3 times
2. ✓ Title "{user_data['title']}" appears at least 2 times
3. ✓ Email "{user_data['email']}" appears in contact section
4. ✓ ALL {len(user_data['projects'])} project names are present
5. ✓ ALL {len(user_data['skills'])} skills are displayed
6. ✓ ALL {len(user_data['education'])} education entries shown
7. ✓ GitHub link "{user_data['links']['github']}" is included
8. ✓ No placeholder text like "John Doe", "example@email.com"
9. ✓ All images use HTTPS URLs
10. ✓ Code is complete and functional

Generate the portfolio now."""

        return prompt
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            response = self.gemini_client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 4500,
                }
            )
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _call_chatgpt(self, prompt: str) -> str:
        """Call OpenAI ChatGPT API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web developer. Generate COMPLETE, PRODUCTION-READY portfolio code using EXACT user data. Replace ALL placeholders. Use ALL provided projects, skills, and education. Return ONLY valid JSON with no markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4500,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"ChatGPT API error: {str(e)}")
    
    async def generate_unlimited_template(
        self,
        framework: str,
        style_description: str,
        user_data: Dict,
        options: Dict = None
    ) -> Dict[str, str]:
        """Generate custom template using AI (Gemini by default, ChatGPT optional) with retry logic"""
        
        if options is None:
            options = {}
        
        # Validate and sanitize input
        try:
            validated_data = self._validate_user_data(user_data)
        except ValueError as e:
            raise ValueError(f"Invalid user data: {e}")
        
        # Validate framework
        supported_frameworks = ['react', 'nextjs', 'vue', 'svelte']
        if framework.lower() not in supported_frameworks:
            raise ValueError(f"Framework must be one of: {', '.join(supported_frameworks)}")
        
        # Build prompt
        prompt = self._build_comprehensive_prompt(
            framework, 
            style_description, 
            validated_data, 
            options
        )
        
        # Try generation with retries
        for attempt in range(self.max_retries):
            try:
                ai_service = "ChatGPT" if self.use_chatgpt else "Gemini"
                print(f"→ Attempt {attempt + 1}/{self.max_retries}: Calling {ai_service} API...")
                
                if self.use_chatgpt:
                    content = self._call_chatgpt(prompt)
                else:
                    try:
                        content = self._call_gemini(prompt)
                    except Exception as gemini_error:
                        print(f"⚠ Gemini failed: {gemini_error}")
                        print(f"→ Falling back to ChatGPT...")
                        # Try to get ChatGPT API key and fallback
                        chatgpt_key = os.getenv('OPENAI_API_KEY')
                        if chatgpt_key:
                            openai_client = OpenAI(api_key=chatgpt_key)
                            self.client = openai_client
                            content = self._call_chatgpt(prompt)
                        else:
                            raise Exception("ChatGPT fallback unavailable: No OpenAI API key")
                
                print(f"✓ Received response ({len(content)} characters)")
                
                # Parse JSON
                files = self._parse_and_validate_response(content, validated_data)
                
                print(f"✓ Successfully generated {len(files)} files")
                return files
                
            except json.JSONDecodeError as e:
                print(f"⚠ Attempt {attempt + 1} failed: JSON parsing error - {e}")
                if attempt == self.max_retries - 1:
                    print("❌ All retries exhausted, using fallback template")
                    return self._get_fallback_template(framework, validated_data, style_description)
                continue
                
            except Exception as e:
                print(f"⚠ Attempt {attempt + 1} failed: {type(e).__name__} - {e}")
                if attempt == self.max_retries - 1:
                    print("❌ All retries exhausted, using fallback template")
                    return self._get_fallback_template(framework, validated_data, style_description)
                continue
        
        # Should never reach here, but just in case
        return self._get_fallback_template(framework, validated_data, style_description)
    
    def _parse_and_validate_response(self, content: str, user_data: Dict) -> Dict[str, str]:
        """Parse and validate AI response"""
        
        # Remove markdown code blocks if present (backup safety)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        # Parse JSON
        files = json.loads(content)
        
        # Validate structure
        required_files = ['package.json', 'index.html']
        for file in required_files:
            if file not in files:
                raise ValueError(f"Missing required file: {file}")
        
        # Validate content includes user data
        all_content = ' '.join(files.values()).lower()
        
        # Check if user's name appears (case-insensitive)
        if user_data['name'].lower() not in all_content:
            print(f"⚠ Warning: User name '{user_data['name']}' not found in generated code")
        
        # Check if email appears
        if user_data['email'].lower() not in all_content:
            print(f"⚠ Warning: User email '{user_data['email']}' not found in generated code")
        
        return files
    
    def _get_fallback_template(
        self, 
        framework: str, 
        user_data: Dict, 
        style: str
    ) -> Dict[str, str]:
        """Production-ready fallback template"""
        
        name = user_data['name']
        title = user_data['title']
        email = user_data['email']
        phone = user_data['phone']
        summary = user_data['summary']
        
        # Build skills HTML
        skills_html = '\n'.join([
            f'            <span class="skill-badge">{skill}</span>'
            for skill in user_data['skills'][:15]
        ])
        
        # Build projects HTML
        projects_html = '\n'.join([
            f'''          <div class="project-card">
            <h3>{proj['name']}</h3>
            <p>{proj['description']}</p>
            <div class="tech-tags">
              {' '.join([f'<span class="tech-tag">{tech}</span>' for tech in proj['technologies']])}
            </div>
            {f'<a href="{proj["link"]}" target="_blank" class="project-link">View Project →</a>' if proj['link'] else ''}
          </div>'''
            for proj in user_data['projects'][:6]
        ])
        
        # Build education HTML
        education_html = '\n'.join([
            f'''          <div class="education-item">
            <h4>{edu['school']}</h4>
            <p>{edu['degree']}</p>
            <span class="year">{edu['year']}</span>
          </div>'''
            for edu in user_data['education'][:3]
        ])
        
        return {
            "package.json": json.dumps({
                "name": "portfolio",
                "version": "1.0.0",
                "description": f"Portfolio for {name}",
                "main": "index.html",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "devDependencies": {
                    "vite": "^5.0.0",
                    "@vitejs/plugin-react": "^4.2.0"
                }
            }, indent=2),
            
            "index.html": f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | Portfolio</title>
  <link rel="stylesheet" href="/src/styles.css">
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>''',
            
            "src/main.jsx": f'''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)''',
            
            "src/App.jsx": f'''import React from 'react'

function App() {{
  return (
    <div className="portfolio">
      <section className="hero">
        <div className="container">
          <h1>{name}</h1>
          <h2>{title}</h2>
          <p className="summary">{summary}</p>
          <div className="cta-buttons">
            <a href="#contact" className="btn-primary">Get In Touch</a>
            <a href="#projects" className="btn-secondary">View Work</a>
          </div>
        </div>
      </section>

      <section id="about" className="section">
        <div className="container">
          <h2 className="section-title">About Me</h2>
          <p>{summary}</p>
        </div>
      </section>

      <section id="skills" className="section bg-light">
        <div className="container">
          <h2 className="section-title">Skills</h2>
          <div className="skills-grid">
{skills_html or '            <span className="skill-badge">JavaScript</span>'}
          </div>
        </div>
      </section>

      <section id="projects" className="section">
        <div className="container">
          <h2 className="section-title">Projects</h2>
          <div className="projects-grid">
{projects_html or '          <div className="project-card"><h3>Sample Project</h3></div>'}
          </div>
        </div>
      </section>

      <section id="education" className="section bg-light">
        <div className="container">
          <h2 className="section-title">Education</h2>
          <div className="education-list">
{education_html or '          <div className="education-item"><h4>University</h4></div>'}
          </div>
        </div>
      </section>

      <section id="contact" className="section">
        <div className="container">
          <h2 className="section-title">Contact Me</h2>
          <p className="contact-email">Email: {email}</p>
          {{phone and <p className="contact-phone">Phone: {phone}</p>}}
          <div className="social-links">
            {{user_data.get('links', {{}}).get('github') and <a href="{{user_data['links']['github']}}" target="_blank">GitHub</a>}}
            {{user_data.get('links', {{}}).get('linkedin') and <a href="{{user_data['links']['linkedin']}}" target="_blank">LinkedIn</a>}}
          </div>
        </div>
      </section>

      <footer className="footer">
        <p>&copy; 2025 {name}. All rights reserved.</p>
      </footer>
    </div>
  )
}}

export default App''',
            
            "src/styles.css": '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Hero Section */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.hero h1 {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
}

.hero h2 {
  font-size: 2rem;
  font-weight: 400;
  margin-bottom: 1rem;
}

.summary {
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto 2rem;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary,
.btn-secondary {
  padding: 1rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.3s;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-primary:hover,
.btn-secondary:hover {
  transform: translateY(-3px);
}

/* Sections */
.section {
  padding: 5rem 0;
}

.bg-light {
  background: #f8f9fa;
}

.section-title {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
}

/* Skills */
.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.skill-badge {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50px;
  font-weight: 500;
}

/* Projects */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.project-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.project-card:hover {
  transform: translateY(-5px);
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
}

.tech-tag {
  padding: 0.25rem 0.75rem;
  background: #e9ecef;
  border-radius: 20px;
  font-size: 0.875rem;
}

/* Education */
.education-list {
  max-width: 800px;
  margin: 0 auto;
}

.education-item {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border-left: 4px solid #667eea;
}

/* Contact */
#contact {
  text-align: center;
}

.contact-email,
.contact-phone {
  font-size: 1.2rem;
  margin: 1rem 0;
}

.social-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.social-links a {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.3s;
}

.social-links a:hover {
  background: #764ba2;
}

/* Footer */
.footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .hero h2 {
    font-size: 1.5rem;
  }
  
  .cta-buttons {
    flex-direction: column;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
}''',
            
            "README.md": f'''# {name}'s Portfolio

AI-Generated portfolio website with {style} design.

## Features
- Responsive design
- Modern UI
- Project showcase
- Skills display
- Contact information

## Technology Stack
- Framework: {framework}
- Styling: CSS3
- Generated: {datetime.now().strftime("%Y-%m-%d")}

## Run Locally
```bash
npm install
npm run dev
```

## Build for Production
```bash
npm run build
```
'''
        }
    
    async def generate_theme_variations(
        self,
        framework: str,
        base_data: Dict,
        num_variations: int = 3
    ) -> List[Dict]:
        """Generate multiple theme variations"""
        
        themes = [
            {"name": "Modern Gradient", "description": "Bold gradients with smooth animations"},
            {"name": "Minimalist Dark", "description": "Clean dark theme with subtle accents"},
            {"name": "Professional Light", "description": "Classic light design with corporate feel"},
            {"name": "Creative Colorful", "description": "Vibrant colors with playful elements"},
            {"name": "Tech Focused", "description": "Code-inspired design with terminal aesthetics"}
        ]
        
        variations = []
        for theme in themes[:num_variations]:
            try:
                files = await self.generate_unlimited_template(
                    framework=framework,
                    style_description=theme['description'],
                    user_data=base_data,
                    options={'theme': theme['name']}
                )
                variations.append({
                    'name': theme['name'],
                    'description': theme['description'],
                    'files': files
                })
            except Exception as e:
                print(f"Failed to generate variation '{theme['name']}': {e}")
                continue
        
        return variations
    
    async def enhance_with_ai(
        self,
        current_code: str,
        enhancement_request: str,
        user_data: Dict
    ) -> str:
        """Enhance existing code with AI"""
        
        prompt = f"""You are modifying an existing portfolio website.

Current Code:
{current_code[:2000]}  # First 2000 chars

User Request: {enhancement_request}

User Data for Context:
- Name: {user_data['name']}
- Email: {user_data['email']}

Rules:
1. Make ONLY the requested changes
2. Keep all existing user data intact
3. Maintain code structure
4. Return ONLY the modified code (no explanations)

Generate the enhanced code now."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a code enhancement expert. Modify code as requested while preserving structure and data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=3000
        )
        
        return response.choices[0].message.content.strip()