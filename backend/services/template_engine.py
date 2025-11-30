from typing import Dict
import os
from pathlib import Path
import json
import random
import html

class TemplateEngine:
    """Manages portfolio templates for different frameworks"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
    
    def _sanitize_html(self, text: str) -> str:
        """Escape HTML to prevent XSS"""
        if not text:
            return ''
        return html.escape(str(text).strip())
    
    def _sanitize_url(self, url: str) -> str:
        """Validate and sanitize URLs"""
        if not url:
            return ''
        url = str(url).strip()
        # Only allow http(s) URLs
        if not (url.startswith('http://') or url.startswith('https://')):
            return ''
        return html.escape(url)
    
    def generate(self, stack: str, data: Dict, options: Dict = {}, template_id: str = None) -> Dict[str, str]:
        """Generate complete project files for selected stack"""
        
        # Default to modern-gradient if no template specified
        if not template_id:
            template_id = "modern-gradient"
        
        if stack == "react":
            return self._generate_react(data, options, template_id)
        elif stack == "nextjs":
            return self._generate_nextjs(data, options, template_id)
        elif stack == "vue":
            return self._generate_vue(data, options, template_id)
        elif stack == "svelte":
            return self._generate_svelte(data, options, template_id)
        else:
            raise ValueError(f"Unsupported stack: {stack}")
    
    def _get_theme_config(self, options: Dict) -> Dict:
        """Get theme-specific configuration for visual variety"""
        theme = options.get('theme', 'gradient')
        
        configs = {
            'gradient': {
                'hero_style': 'full-height gradient',
                'section_order': ['about', 'skills', 'projects', 'contact'],
                'card_style': 'shadow',
                'nav_transparent': True
            },
            'minimal': {
                'hero_style': 'centered simple',
                'section_order': ['skills', 'projects', 'about', 'contact'],
                'card_style': 'border',
                'nav_transparent': False
            },
            'dark': {
                'hero_style': 'dark fullscreen',
                'section_order': ['projects', 'skills', 'about', 'contact'],
                'card_style': 'dark-card',
                'nav_transparent': True
            },
            'colorful': {
                'hero_style': 'animated colorful',
                'section_order': ['about', 'projects', 'skills', 'contact'],
                'card_style': 'colorful-card',
                'nav_transparent': False
            }
        }
        
        return configs.get(theme, configs['gradient'])
    
    def _generate_react(self, data: Dict, options: Dict, template_id: str = "modern-gradient") -> Dict[str, str]:
        """Generate React + Vite portfolio matchingparthasarathyg.netlify.app style"""
        name = data.get('name', 'Your Name')
        title = data.get('title', 'Full Stack Developer')
        email = data.get('email', 'hello@example.com')
        phone = data.get('phone', '')
        summary = data.get('summary', 'A highly motivated and detail-oriented software developer passionate about building innovative solutions.')
        skills = data.get('skills', [])
        projects = data.get('projects', [])
        education = data.get('education', [])
        links = data.get('links', {})
        
        # Color theme
        primary_color = options.get('primaryColor', '#667eea')
        secondary_color = options.get('secondaryColor', '#764ba2')
        
        files = {
            "package.json": json.dumps({
                "name": "portfolio",
                "private": True,
                "version": "1.0.0",
                "type": "module",
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
                    "@types/react": "^18.2.43",
                    "@types/react-dom": "^18.2.17",
                    "@vitejs/plugin-react": "^4.2.1",
                    "vite": "^5.0.8"
                }
            }, indent=2),
            
            "index.html": f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name} | Portfolio</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
            
            "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
            
            "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
            
            "src/App.jsx": self._create_modern_portfolio_app(data, options),
            "src/index.css": self._create_modern_portfolio_styles(primary_color, secondary_color),
            "README.md": f"# {name}'s Portfolio\n\nModern, responsive portfolio built with React + Vite\n\n## Features\n- Smooth scrolling navigation\n- Responsive design\n- Modern UI with gradients\n- Project showcase\n- Contact form\n\n## Run Locally\n```bash\nnpm install\nnpm run dev\n```"
        }
        
        return files
    
    def _create_modern_portfolio_app(self, data: Dict, options: Dict) -> str:
        """Create modern portfolio app matching parthasarathyg.netlify.app"""
        name = self._sanitize_html(data.get('name', 'Your Name'))
        title = self._sanitize_html(data.get('title', 'Developer'))
        email = self._sanitize_html(data.get('email', 'hello@example.com'))
        phone = self._sanitize_html(data.get('phone', ''))
        summary = self._sanitize_html(data.get('summary', 'A highly motivated software developer passionate about innovation.'))
        skills = data.get('skills', [])
        projects = data.get('projects', [])
        education = data.get('education', [])
        links = data.get('links', {})
        
        # Build skills sections - fix circular reference
        languages = [self._sanitize_html(s) for s in skills if any(lang in s.lower() for lang in ['python', 'java', 'javascript', 'c++', 'php', 'react', 'typescript'])]
        technologies = [self._sanitize_html(s) for s in skills if s not in languages]
        
        skill_categories = {
            'Languages': languages,
            'Technologies': technologies,
        }
        
        skills_sections = []
        for category, skills_list in skill_categories.items():
            if skills_list:
                skill_tags = '\n            '.join([f'<span className="skill-tag">{skill}</span>' for skill in skills_list[:6]])
                skills_sections.append(f'''        <div className="skill-category">
          <h3>{category}</h3>
          <div className="skills-list">
            {skill_tags}
          </div>
        </div>''')
        
        skills_jsx = '\n'.join(skills_sections)
        
        # Build projects
        projects_sections = []
        for proj in projects[:6]:
            link_html = f'<a href="{self._sanitize_url(proj.get("link"))}" className="project-link" target="_blank">View on GitHub →</a>' if proj.get('link') else ''
            tech = ', '.join([self._sanitize_html(t) for t in proj.get('technologies', [])])
            projects_sections.append(f'''        <div className="project-card">
          <div className="project-header">
            <h3>{self._sanitize_html(proj.get('name', 'Project'))}</h3>
            <span className="project-year">({self._sanitize_html(proj.get('year', '2024'))})</span>
          </div>
          <p className="project-role">Role: {self._sanitize_html(proj.get('role', 'Developer'))}</p>
          <p className="project-desc">{self._sanitize_html(proj.get('description', ''))}</p>
          <div className="project-tech">
            {tech}
          </div>
          {link_html}
        </div>''')
        
        projects_jsx = '\n'.join(projects_sections)
        
        # Build education
        education_sections = []
        for edu in education[:3]:
            education_sections.append(f'''<div className="education-item">
                  <h4>{self._sanitize_html(edu.get('school', 'University'))}</h4>
                  <p>{self._sanitize_html(edu.get('degree', 'Degree'))}</p>
                  <span className="education-year">{self._sanitize_html(edu.get('year', ''))}</span>
                </div>''')

        education_jsx = '\n                '.join(education_sections)
        
        # Build experience
        experience = data.get('experience', [])
        experience_sections = []
        for exp in experience[:5]:
            exp_desc = self._sanitize_html(exp.get('description', ''))
            experience_sections.append(f'''        <div className="experience-item">
          <div className="experience-header">
            <h3>{self._sanitize_html(exp.get('title', 'Position'))}</h3>
            <span className="experience-period">{self._sanitize_html(exp.get('startDate', ''))} - {self._sanitize_html(exp.get('endDate', ''))}</span>
          </div>
          <p className="experience-company">{self._sanitize_html(exp.get('company', 'Company'))}</p>
          <p className="experience-desc">{exp_desc}</p>
        </div>''')
        
        experience_jsx = '\n'.join(experience_sections)
        
        phone_html = f'<p className="contact-phone">Phone: {phone}</p>' if phone else ''
        
        return f"""import {{ useState, useEffect }} from 'react'

function App() {{
  const [activeSection, setActiveSection] = useState('home')
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {{
    const handleScroll = () => {{
      setScrolled(window.scrollY > 50)
    }}
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }}, [])

  const scrollToSection = (id) => {{
    const element = document.getElementById(id)
    if (element) {{
      element.scrollIntoView({{ behavior: 'smooth' }})
      setActiveSection(id)
    }}
  }}

  return (
    <div className="portfolio">
      {{/* Navigation */}}
      <nav className={{scrolled ? 'nav scrolled' : 'nav'}}>
        <div className="nav-container">
          <div className="logo">{name}</div>
          <div className="nav-links">
            <a onClick={{() => scrollToSection('home')}}>Home</a>
            <a onClick={{() => scrollToSection('about')}}>About</a>
            <a onClick={{() => scrollToSection('skills')}}>Skills</a>
            <a onClick={{() => scrollToSection('projects')}}>Projects</a>
            <a onClick={{() => scrollToSection('contact')}}>Contact</a>
          </div>
        </div>
      </nav>

      {{/* Hero Section */}}
      <section id="home" className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Hi, I'm {name}</h1>
          <div className="hero-subtitle">
            <span>I'm a </span>
            <span className="typing-text">{title}</span>
          </div>
          <p className="hero-description">{summary}</p>
          <div className="hero-buttons">
            <button onClick={{() => scrollToSection('contact')}} className="btn-primary">
              Hire Me
            </button>
            <button onClick={{() => scrollToSection('projects')}} className="btn-secondary">
              My Work
            </button>
          </div>
        </div>
      </section>

      {{/* About Section */}}
      <section id="about" className="section">
        <div className="container">
          <h2 className="section-title">About Me</h2>
          <div className="about-content">
            <div className="about-text">
              <h3>Objective</h3>
              <p>{summary}</p>
              
              <h3>Education</h3>
              <div className="education-list">
                {education_jsx or '<div className="education-item"><h4>Education</h4><p>Add your education details</p></div>'}
              </div>
            </div>
          </div>
        </div>
      </section>

      {{/* Experience Section */}}
      <section id="experience" className="section section-alt">
        <div className="container">
          <h2 className="section-title">Work Experience</h2>
          <div className="experience-timeline">
{experience_jsx or '''            <div className="experience-item">
              <div className="experience-header">
                <h3>Your Position</h3>
                <span className="experience-period">Start Date - End Date</span>
              </div>
              <p className="experience-company">Company Name</p>
              <p className="experience-desc">Description of your role and achievements</p>
            </div>'''}
          </div>
        </div>
      </section>

      {{/* Skills Section */}}
      <section id="skills" className="section section-alt">
        <div className="container">
          <h2 className="section-title">Areas of Interest & Skills</h2>
          <div className="skills-grid">
{skills_jsx or '''            <div className="skill-category">
              <h3>Technologies</h3>
              <div className="skills-list">
                <span className="skill-tag">JavaScript</span>
                <span className="skill-tag">React</span>
                <span className="skill-tag">Node.js</span>
              </div>
            </div>'''}
          </div>
        </div>
      </section>

      {{/* Projects Section */}}
      <section id="projects" className="section">
        <div className="container">
          <h2 className="section-title">Featured Projects</h2>
          <div className="projects-grid">
{projects_jsx or '''            <div className="project-card">
              <div className="project-header">
                <h3>Sample Project</h3>
                <span className="project-year">(2024)</span>
              </div>
              <p className="project-role">Role: Full Stack Developer</p>
              <p className="project-desc">Description of the project goes here.</p>
              <div className="project-tech">React, Node.js, MongoDB</div>
            </div>'''}
          </div>
        </div>
      </section>

      {{/* Contact Section */}}
      <section id="contact" className="section section-alt">
        <div className="container">
          <h2 className="section-title">Contact Me!</h2>
          <div className="contact-content">
            <p className="contact-email">Email: {email}</p>
            {phone_html}
            <a href="mailto:{email}" className="btn-primary">Send Message</a>
          </div>
        </div>
      </section>

      {{/* Footer */}}
      <footer className="footer">
        <p>© 2025 {name} | All Rights Reserved</p>
      </footer>
    </div>
  )
}}

export default App"""

    def _create_modern_portfolio_styles(self, primary: str, secondary: str) -> str:
        """Create modern styles matching parthasarathyg.netlify.app"""
        return f"""/* Modern Portfolio Styles - Inspired by parthasarathyg.netlify.app */

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

:root {{
  --primary: {primary};
  --secondary: {secondary};
  --text-dark: #2d3748;
  --text-light: #718096;
  --bg-light: #f7fafc;
  --white: #ffffff;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Inter', sans-serif;
  color: var(--text-dark);
  line-height: 1.6;
  overflow-x: hidden;
}}

.portfolio {{
  min-height: 100vh;
}}

/* Navigation */
.nav {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: transparent;
  padding: 1.5rem 0;
  z-index: 1000;
  transition: all 0.3s ease;
}}

.nav.scrolled {{
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}}

.nav-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.logo {{
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.nav-links {{
  display: flex;
  gap: 2rem;
}}

.nav-links a {{
  color: var(--text-dark);
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s;
}}

.nav-links a:hover {{
  color: var(--primary);
}}

/* Hero Section */
.hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  position: relative;
  overflow: hidden;
}}

.hero::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,...') no-repeat center/cover;
  opacity: 0.1;
}}

.hero-content {{
  position: relative;
  text-align: center;
  color: var(--white);
  padding: 2rem;
  max-width: 800px;
}}

.hero-title {{
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 1rem;
  animation: fadeInUp 0.8s ease;
}}

.hero-subtitle {{
  font-size: 2rem;
  margin-bottom: 1.5rem;
  animation: fadeInUp 1s ease;
}}

.typing-text {{
  border-right: 3px solid var(--white);
  animation: typing 3.5s steps(40, end) infinite, blink 0.75s step-end infinite;
}}

.hero-description {{
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.95;
  animation: fadeInUp 1.2s ease;
}}

.hero-buttons {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  animation: fadeInUp 1.4s ease;
}}

/* Buttons */
.btn-primary,
.btn-secondary {{
  padding: 1rem 2.5rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}}

.btn-primary {{
  background: var(--white);
  color: var(--primary);
}}

.btn-primary:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}}

.btn-secondary {{
  background: transparent;
  color: var(--white);
  border: 2px solid var(--white);
}}

.btn-secondary:hover {{
  background: var(--white);
  color: var(--primary);
}}

/* Sections */
.section {{
  padding: 6rem 0;
}}

.section-alt {{
  background: var(--bg-light);
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}}

.section-title {{
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
  color: var(--text-dark);
}}

.section-title::after {{
  content: '';
  display: block;
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  margin: 1rem auto 0;
  border-radius: 2px;
}}

/* About Section */
.about-content {{
  max-width: 900px;
  margin: 0 auto;
}}

.about-text h3 {{
  font-size: 1.8rem;
  color: var(--text-dark);
  margin-top: 2rem;
  margin-bottom: 1rem;
}}

.about-text p {{
  color: var(--text-light);
  font-size: 1.1rem;
  line-height: 1.8;
}}

.education-list {{
  margin-top: 1.5rem;
}}

.education-item {{
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: var(--white);
  border-radius: 12px;
  border-left: 4px solid var(--primary);
}}

.education-item h4 {{
  color: var(--text-dark);
  font-size: 1.2rem;
}}

.education-year {{
  color: var(--text-light);
  font-size: 0.9rem;
}}

/* Skills Section */
.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}}

.skill-category {{
  padding: 2rem;
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: transform 0.3s ease;
}}

.skill-category:hover {{
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}}

.skill-category h3 {{
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--text-dark);
}}

.skills-list {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}}

.skill-tag {{
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: var(--white);
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
}}

/* Projects Section */
.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2.5rem;
}}

.project-card {{
  background: var(--white);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}}

.project-card:hover {{
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary);
}}

.project-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}}

.project-header h3 {{
  font-size: 1.4rem;
  color: var(--text-dark);
}}

.project-year {{
  color: var(--text-light);
  font-size: 0.9rem;
}}

.project-role {{
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 0.8rem;
}}

.project-desc {{
  color: var(--text-light);
  margin-bottom: 1rem;
  line-height: 1.7;
}}

.project-tech {{
  color: var(--text-light);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}}

.project-link {{
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}}

.project-link:hover {{
  gap: 0.8rem;
}}

/* Contact Section */
.contact-content {{
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}}

.contact-email,
.contact-phone {{
  font-size: 1.3rem;
  color: var(--text-dark);
  margin-bottom: 1.5rem;
}}

/* Footer */
.footer {{
  background: var(--text-dark);
  color: var(--white);
  text-align: center;
  padding: 2rem;
}}

/* Animations */
@keyframes fadeInUp {{
  from {{
    opacity: 0;
    transform: translateY(30px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes typing {{
  from {{ width: 0 }}
  to {{ width: 100% }}
}}

@keyframes blink {{
  50% {{ border-color: transparent }}
}}

/* Responsive */
@media (max-width: 768px) {{
  .hero-title {{
    font-size: 2.5rem;
  }}
  
  .hero-subtitle {{
    font-size: 1.5rem;
  }}
  
  .nav-links {{
    gap: 1rem;
  }}
  
  .section-title {{
    font-size: 2rem;
  }}
  
  
  .projects-grid,
  .skills-grid {{
    grid-template-columns: 1fr;
  }}
}}"""
    
    def _generate_nextjs(self, data: Dict, options: Dict, template_id: str = "modern-gradient") -> Dict[str, str]:
        """Generate Next.js 14 portfolio with App Router"""
        name = self._sanitize_html(data.get('name', 'Your Name'))
        title = self._sanitize_html(data.get('title', 'Full Stack Developer'))
        email = self._sanitize_html(data.get('email', 'hello@example.com'))
        phone = self._sanitize_html(data.get('phone', ''))
        summary = self._sanitize_html(data.get('summary', 'A highly motivated and detail-oriented software developer passionate about building innovative solutions.'))
        skills = data.get('skills', [])
        projects = data.get('projects', [])
        education = data.get('education', [])
        
        primary_color = options.get('primaryColor', '#667eea')
        secondary_color = options.get('secondaryColor', '#764ba2')
        
        # Build skills template for Next.js
        skills_tsx = ""
        languages = [self._sanitize_html(s) for s in skills if any(lang in s.lower() for lang in ['python', 'java', 'javascript', 'c++', 'php', 'react', 'typescript'])]
        technologies = [self._sanitize_html(s) for s in skills if s not in languages]
        
        skills_tsx = ""
        if languages:
            skill_tags = '\n            '.join([f'<span className="skill-tag">{skill}</span>' for skill in languages[:6]])
            skills_tsx += f'''          <div className="skill-category">
            <h3>Languages</h3>
            <div className="skills-list">
              {skill_tags}
            </div>
          </div>\n'''
        if technologies:
            skill_tags = '\n            '.join([f'<span className="skill-tag">{skill}</span>' for skill in technologies[:6]])
            skills_tsx += f'''          <div className="skill-category">
            <h3>Technologies</h3>
            <div className="skills-list">
              {skill_tags}
            </div>
          </div>'''
        
        if not skills_tsx:
            skills_tsx = '''          <div className="skill-category">
            <h3>Technologies</h3>
            <div className="skills-list">
              <span className="skill-tag">JavaScript</span>
              <span className="skill-tag">React</span>
              <span className="skill-tag">Node.js</span>
            </div>
          </div>'''
        
        # Build projects
        projects_tsx = ""
        for proj in projects[:6]:
            link_html = f'<a href="{self._sanitize_url(proj.get("link"))}" className="project-link" target="_blank" rel="noopener noreferrer">View on GitHub →</a>' if proj.get('link') else ''
            tech = ', '.join([self._sanitize_html(t) for t in proj.get('technologies', [])])
            projects_tsx += f'''          <div className="project-card">
            <div className="project-header">
              <h3>{self._sanitize_html(proj.get('name', 'Project'))}</h3>
              <span className="project-year">({self._sanitize_html(proj.get('year', '2024'))})</span>
            </div>
            <p className="project-role">Role: {self._sanitize_html(proj.get('role', 'Developer'))}</p>
            <p className="project-desc">{self._sanitize_html(proj.get('description', ''))}</p>
            <div className="project-tech">{tech}</div>
            {link_html}
          </div>\n'''
        
        if not projects_tsx:
            projects_tsx = '''          <div className="project-card">
            <div className="project-header">
              <h3>Sample Project</h3>
              <span className="project-year">(2024)</span>
            </div>
            <p className="project-role">Role: Full Stack Developer</p>
            <p className="project-desc">Description of the project goes here.</p>
            <div className="project-tech">React, Node.js, MongoDB</div>
          </div>'''
        
        # Build education
        education_tsx = ""
        for edu in education[:3]:
            education_tsx += f'''            <div className="education-item">
              <h4>{self._sanitize_html(edu.get('school', 'University'))}</h4>
              <p>{self._sanitize_html(edu.get('degree', 'Degree'))}</p>
              <span className="education-year">{self._sanitize_html(edu.get('year', ''))}</span>
            </div>\n'''
        
        if not education_tsx:
            education_tsx = '''            <div className="education-item">
              <h4>Education</h4>
              <p>Add your education details</p>
            </div>'''
        
        phone_html = f'<p className="contact-phone">Phone: {phone}</p>' if phone else ''
        
        return {
            "package.json": json.dumps({
                "name": "portfolio-nextjs",
                "version": "1.0.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint"
                },
                "dependencies": {
                    "next": "14.0.3",
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "devDependencies": {
                    "@types/node": "^20",
                    "@types/react": "^18",
                    "@types/react-dom": "^18",
                    "typescript": "^5"
                }
            }, indent=2),
            
            "app/layout.tsx": f'''import type {{ Metadata }} from 'next'
import './globals.css'

export const metadata: Metadata = {{
  title: '{name} | Portfolio',
  description: '{summary}',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  )
}}''',
            
            "app/page.tsx": f'''"use client"

import {{ useState, useEffect }} from 'react'

export default function Portfolio() {{
  const [activeSection, setActiveSection] = useState('home')
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {{
    const handleScroll = () => {{
      setScrolled(window.scrollY > 50)
    }}
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }}, [])

  const scrollToSection = (id: string) => {{
    const element = document.getElementById(id)
    if (element) {{
      element.scrollIntoView({{ behavior: 'smooth' }})
      setActiveSection(id)
    }}
  }}

  return (
    <div className="portfolio">
      {{/* Navigation */}}
      <nav className={{scrolled ? 'nav scrolled' : 'nav'}}>
        <div className="nav-container">
          <div className="logo">{name}</div>
          <div className="nav-links">
            <a onClick={{() => scrollToSection('home')}}>Home</a>
            <a onClick={{() => scrollToSection('about')}}>About</a>
            <a onClick={{() => scrollToSection('skills')}}>Skills</a>
            <a onClick={{() => scrollToSection('projects')}}>Projects</a>
            <a onClick={{() => scrollToSection('contact')}}>Contact</a>
          </div>
        </div>
      </nav>

      {{/* Hero Section */}}
      <section id="home" className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Hi, I&apos;m {name}</h1>
          <div className="hero-subtitle">
            <span>I&apos;m a </span>
            <span className="typing-text">{title}</span>
          </div>
          <p className="hero-description">{summary}</p>
          <div className="hero-buttons">
            <button onClick={{() => scrollToSection('contact')}} className="btn-primary">
              Hire Me
            </button>
            <button onClick={{() => scrollToSection('projects')}} className="btn-secondary">
              My Work
            </button>
          </div>
        </div>
      </section>

      {{/* About Section */}}
      <section id="about" className="section">
        <div className="container">
          <h2 className="section-title">About Me</h2>
          <div className="about-content">
            <div className="about-text">
              <h3>Objective</h3>
              <p>{summary}</p>
              
              <h3>Education</h3>
              <div className="education-list">
{education_tsx}
              </div>
            </div>
          </div>
        </div>
      </section>

      {{/* Skills Section */}}
      <section id="skills" className="section section-alt">
        <div className="container">
          <h2 className="section-title">Areas of Interest & Skills</h2>
          <div className="skills-grid">
{skills_tsx}
          </div>
        </div>
      </section>

      {{/* Projects Section */}}
      <section id="projects" className="section">
        <div className="container">
          <h2 className="section-title">Featured Projects</h2>
          <div className="projects-grid">
{projects_tsx}
          </div>
        </div>
      </section>

      {{/* Contact Section */}}
      <section id="contact" className="section section-alt">
        <div className="container">
          <h2 className="section-title">Contact Me!</h2>
          <div className="contact-content">
            <p className="contact-email">Email: {email}</p>
            {phone_html}
            <a href="mailto:{email}" className="btn-primary">Send Message</a>
          </div>
        </div>
      </section>

      {{/* Footer */}}
      <footer className="footer">
        <p>© 2025 {name} | All Rights Reserved</p>
      </footer>
    </div>
  )
}}''',
            
            "app/globals.css": f'''/* Modern Portfolio Styles */

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

:root {{
  --primary: {primary_color};
  --secondary: {secondary_color};
  --text-dark: #2d3748;
  --text-light: #718096;
  --bg-light: #f7fafc;
  --white: #ffffff;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Inter', sans-serif;
  color: var(--text-dark);
  line-height: 1.6;
  overflow-x: hidden;
}}

.portfolio {{
  min-height: 100vh;
}}

/* Navigation */
.nav {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: transparent;
  padding: 1.5rem 0;
  z-index: 1000;
  transition: all 0.3s ease;
}}

.nav.scrolled {{
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}}

.nav-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.logo {{
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.nav-links {{
  display: flex;
  gap: 2rem;
}}

.nav-links a {{
  color: var(--text-dark);
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s;
}}

.nav-links a:hover {{
  color: var(--primary);
}}

/* Hero Section */
.hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  position: relative;
  overflow: hidden;
}}

.hero-content {{
  position: relative;
  text-align: center;
  color: var(--white);
  padding: 2rem;
  max-width: 800px;
}}

.hero-title {{
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 1rem;
  animation: fadeInUp 0.8s ease;
}}

.hero-subtitle {{
  font-size: 2rem;
  margin-bottom: 1.5rem;
  animation: fadeInUp 1s ease;
}}

.typing-text {{
  border-right: 3px solid var(--white);
  animation: blink 0.75s step-end infinite;
}}

.hero-description {{
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.95;
  animation: fadeInUp 1.2s ease;
}}

.hero-buttons {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  animation: fadeInUp 1.4s ease;
}}

/* Buttons */
.btn-primary,
.btn-secondary {{
  padding: 1rem 2.5rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}}

.btn-primary {{
  background: var(--white);
  color: var(--primary);
}}

.btn-primary:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}}

.btn-secondary {{
  background: transparent;
  color: var(--white);
  border: 2px solid var(--white);
}}

.btn-secondary:hover {{
  background: var(--white);
  color: var(--primary);
}}

/* Sections */
.section {{
  padding: 6rem 0;
}}

.section-alt {{
  background: var(--bg-light);
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}}

.section-title {{
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
  color: var(--text-dark);
}}

.section-title::after {{
  content: '';
  display: block;
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  margin: 1rem auto 0;
  border-radius: 2px;
}}

/* About Section */
.about-content {{
  max-width: 900px;
  margin: 0 auto;
}}

.about-text h3 {{
  font-size: 1.8rem;
  color: var(--text-dark);
  margin-top: 2rem;
  margin-bottom: 1rem;
}}

.about-text p {{
  color: var(--text-light);
  font-size: 1.1rem;
  line-height: 1.8;
}}

.education-list {{
  margin-top: 1.5rem;
}}

.education-item {{
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: var(--white);
  border-radius: 12px;
  border-left: 4px solid var(--primary);
}}

.education-item h4 {{
  color: var(--text-dark);
  font-size: 1.2rem;
}}

.education-year {{
  color: var(--text-light);
  font-size: 0.9rem;
}}

/* Skills Section */
.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}}

.skill-category {{
  padding: 2rem;
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: transform 0.3s ease;
}}

.skill-category:hover {{
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}}

.skill-category h3 {{
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--text-dark);
}}

.skills-list {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}}

.skill-tag {{
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: var(--white);
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
}}

/* Projects Section */
.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2.5rem;
}}

.project-card {{
  background: var(--white);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}}

.project-card:hover {{
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary);
}}

.project-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}}

.project-header h3 {{
  font-size: 1.4rem;
  color: var(--text-dark);
}}

.project-year {{
  color: var(--text-light);
  font-size: 0.9rem;
}}

.project-role {{
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 0.8rem;
}}

.project-desc {{
  color: var(--text-light);
  margin-bottom: 1rem;
  line-height: 1.7;
}}

.project-tech {{
  color: var(--text-light);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}}

.project-link {{
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}}

.project-link:hover {{
  gap: 0.8rem;
}}

/* Contact Section */
.contact-content {{
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}}

.contact-email,
.contact-phone {{
  font-size: 1.3rem;
  color: var(--text-dark);
  margin-bottom: 1.5rem;
}}

/* Footer */
.footer {{
  background: var(--text-dark);
  color: var(--white);
  text-align: center;
  padding: 2rem;
}}

/* Animations */
@keyframes fadeInUp {{
  from {{
    opacity: 0;
    transform: translateY(30px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes blink {{
  50% {{ border-color: transparent }}
}}

/* Responsive */
@media (max-width: 768px) {{
  .hero-title {{
    font-size: 2.5rem;
  }}
  
  .hero-subtitle {{
    font-size: 1.5rem;
  }}
  
  .nav-links {{
    gap: 1rem;
  }}
  
  .section-title {{
    font-size: 2rem;
  }}
  
  .projects-grid,
  .skills-grid {{
    grid-template-columns: 1fr;
  }}
}}''',
            
            "README.md": f"# {name}'s Portfolio\n\nModern Next.js portfolio built with Next.js 14 App Router\n\n## Run Locally\n```bash\nnpm install\nnpm run dev\n```"
        }
    
    def _generate_vue(self, data: Dict, options: Dict, template_id: str = "modern-gradient") -> Dict[str, str]:
        """Generate Vue 3 + Vite portfolio"""
        name = self._sanitize_html(data.get('name', 'Your Name'))
        title = self._sanitize_html(data.get('title', 'Full Stack Developer'))
        email = self._sanitize_html(data.get('email', 'hello@example.com'))
        phone = self._sanitize_html(data.get('phone', ''))
        summary = self._sanitize_html(data.get('summary', 'A highly motivated and detail-oriented software developer passionate about building innovative solutions.'))
        skills = data.get('skills', [])
        projects = data.get('projects', [])
        education = data.get('education', [])
        
        primary_color = options.get('primaryColor', '#667eea')
        secondary_color = options.get('secondaryColor', '#764ba2')
        
        # Build skills template
        skills_vue = ""
        languages = [self._sanitize_html(s) for s in skills if any(lang in s.lower() for lang in ['python', 'java', 'javascript', 'c++', 'php', 'react', 'typescript', 'vue'])]
        technologies = [self._sanitize_html(s) for s in skills if s not in languages]
        
        if languages:
            skill_tags = '\n            '.join([f'<span class="skill-tag">{skill}</span>' for skill in languages[:6]])
            skills_vue += f'''        <div class="skill-category">
          <h3>Languages</h3>
          <div class="skills-list">
            {skill_tags}
          </div>
        </div>\n'''
        if technologies:
            skill_tags = '\n            '.join([f'<span class="skill-tag">{skill}</span>' for skill in technologies[:6]])
            skills_vue += f'''        <div class="skill-category">
          <h3>Technologies</h3>
          <div class="skills-list">
            {skill_tags}
          </div>
        </div>'''
        
        if not skills_vue:
            skills_vue = '''        <div class="skill-category">
          <h3>Technologies</h3>
          <div class="skills-list">
            <span class="skill-tag">JavaScript</span>
            <span class="skill-tag">Vue</span>
            <span class="skill-tag">Node.js</span>
          </div>
        </div>'''
        
        # Build education for Vue
        education_vue = ""
        for edu in education[:3]:
            education_vue += f'''        <div class="education-item">
          <h4>{self._sanitize_html(edu.get('school', 'University'))}</h4>
          <p>{self._sanitize_html(edu.get('degree', 'Degree'))}</p>
          <span class="education-year">{self._sanitize_html(edu.get('year', ''))}</span>
        </div>
'''
        if not education_vue:
            education_vue = '''        <div class="education-item">
          <h4>Education</h4>
          <p>Add your education details</p>
        </div>'''
        
        # Build projects for Vue
        projects_vue = ""
        for proj in projects[:6]:
            link_html = f'<a href="{self._sanitize_url(proj.get("link"))}" class="project-link" target="_blank">View →</a>' if proj.get('link') else ''
            tech = ', '.join([self._sanitize_html(t) for t in proj.get('technologies', [])])
            projects_vue += f'''        <div class="project-card">
          <h3>{self._sanitize_html(proj.get('name', 'Project'))}</h3>
          <p class="project-desc">{self._sanitize_html(proj.get('description', ''))}</p>
          <span class="project-tech">{tech}</span>
          {link_html}
        </div>
'''
        if not projects_vue:
            projects_vue = '''        <div class="project-card">
          <h3>Project</h3>
          <p>Add your project details</p>
        </div>'''
        
        phone_html = f'<p class="contact-phone">Phone: {phone}</p>' if phone else ''
        
        # Build education for Svelte (used in this Vue function that returns Svelte)
        education_svelte = ""
        for edu in education[:3]:
            education_svelte += f'''        <div class="education-item">
          <h4>{self._sanitize_html(edu.get('school', 'University'))}</h4>
          <p>{self._sanitize_html(edu.get('degree', 'Degree'))}</p>
          <span class="education-year">{self._sanitize_html(edu.get('year', ''))}</span>
        </div>
'''
        if not education_svelte:
            education_svelte = '''        <div class="education-item">
          <h4>Education</h4>
          <p>Add your education details</p>
        </div>'''
        
        # Build projects for Svelte
        projects_svelte = ""
        for proj in projects[:6]:
            link_html = f'<a href="{self._sanitize_url(proj.get("link"))}" class="project-link" target="_blank">View →</a>' if proj.get('link') else ''
            tech = ', '.join([self._sanitize_html(t) for t in proj.get('technologies', [])])
            projects_svelte += f'''        <div class="project-card">
          <h3>{self._sanitize_html(proj.get('name', 'Project'))}</h3>
          <p class="project-desc">{self._sanitize_html(proj.get('description', ''))}</p>
          <span class="project-tech">{tech}</span>
          {link_html}
        </div>
'''
        if not projects_svelte:
            projects_svelte = '''        <div class="project-card">
          <h3>Project</h3>
          <p>Add your project details</p>
        </div>'''
        
        # Build skills for Svelte
        skills_svelte = ""
        languages = [self._sanitize_html(s) for s in skills if any(lang in s.lower() for lang in ['python', 'java', 'javascript', 'c++', 'php', 'react', 'typescript', 'svelte'])]
        technologies = [self._sanitize_html(s) for s in skills if s not in languages]
        
        if languages:
            skill_tags = '\n            '.join([f'<span class="skill-tag">{skill}</span>' for skill in languages[:6]])
            skills_svelte += f'''        <div class="skill-category">
          <h3>Languages</h3>
          <div class="skills-list">
            {skill_tags}
          </div>
        </div>\n'''
        if technologies:
            skill_tags = '\n            '.join([f'<span class="skill-tag">{skill}</span>' for skill in technologies[:6]])
            skills_svelte += f'''        <div class="skill-category">
          <h3>Technologies</h3>
          <div class="skills-list">
            {skill_tags}
          </div>
        </div>'''
        if not skills_svelte:
            skills_svelte = '''        <div class="skill-category">
          <h3>Technologies</h3>
          <div class="skills-list">
            <span class="skill-tag">JavaScript</span>
            <span class="skill-tag">Svelte</span>
            <span class="skill-tag">Node.js</span>
          </div>
        </div>'''
        
        return {
            "package.json": json.dumps({
                "name": "portfolio-vue",
                "version": "1.0.0",
                "private": True,
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "vue": "^3.3.4"
                },
                "devDependencies": {
                    "@vitejs/plugin-vue": "^4.3.4",
                    "vite": "^5.0.8"
                }
            }, indent=2),
            
            "index.html": f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/svg+xml" href="/vite.svg">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Portfolio</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>''',
            
            "vite.config.js": '''import {{ defineConfig }} from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({{
  plugins: [vue()],
}})''',
            
            "src/main.js": '''import {{ createApp }} from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')''',
            
            "src/App.vue": f'''<template>
  <div class="portfolio">
    <!-- Navigation -->
    <nav :class="{{scrolled: isScrolled}}">
      <div class="nav-container">
        <div class="logo">{name}</div>
        <div class="nav-links">
          <a @click="scrollToSection('home')">Home</a>
          <a @click="scrollToSection('about')">About</a>
          <a @click="scrollToSection('skills')">Skills</a>
          <a @click="scrollToSection('projects')">Projects</a>
          <a @click="scrollToSection('contact')">Contact</a>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero">
      <div class="hero-content">
        <h1 class="hero-title">Hi, I'm {name}</h1>
        <div class="hero-subtitle">
          <span>I'm a </span>
          <span class="typing-text">{title}</span>
        </div>
        <p class="hero-description">{summary}</p>
        <div class="hero-buttons">
          <button @click="scrollToSection('contact')" class="btn-primary">
            Hire Me
          </button>
          <button @click="scrollToSection('projects')" class="btn-secondary">
            My Work
          </button>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section">
      <div class="container">
        <h2 class="section-title">About Me</h2>
        <div class="about-content">
          <div class="about-text">
            <h3>Objective</h3>
            <p>{summary}</p>
            
            <h3>Education</h3>
            <div class="education-list">
{education_vue}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Skills Section -->
    <section id="skills" class="section section-alt">
      <div class="container">
        <h2 class="section-title">Areas of Interest & Skills</h2>
        <div class="skills-grid">
{skills_vue}
        </div>
      </div>
    </section>

    <!-- Projects Section -->
    <section id="projects" class="section">
      <div class="container">
        <h2 class="section-title">Featured Projects</h2>
        <div class="projects-grid">
{projects_vue}
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="section section-alt">
      <div class="container">
        <h2 class="section-title">Contact Me!</h2>
        <div class="contact-content">
          <p class="contact-email">Email: {email}</p>
          {phone_html}
          <a href="mailto:{email}" class="btn-primary">Send Message</a>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>© 2025 {name} | All Rights Reserved</p>
    </footer>
  </div>
</template>

<script setup>
import {{ ref, onMounted, onBeforeUnmount }} from 'vue'

const isScrolled = ref(false)

function handleScroll() {{
  isScrolled.value = window.scrollY > 50
}}

function scrollToSection(id) {{
  const element = document.getElementById(id)
  if (element) {{
    element.scrollIntoView({{ behavior: 'smooth' }})
  }}
}}

onMounted(() => {{
  window.addEventListener('scroll', handleScroll)
}})

onBeforeUnmount(() => {{
  window.removeEventListener('scroll', handleScroll)
}})
</script>

<style scoped>
  /* Modern Portfolio Styles - Vue Version */

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  :root {{
    --primary: {primary_color};
    --secondary: {secondary_color};
    --text-dark: #2d3748;
    --text-light: #718096;
    --bg-light: #f7fafc;
    --white: #ffffff;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Inter', sans-serif;
    color: var(--text-dark);
    line-height: 1.6;
    overflow-x: hidden;
  }}

  .portfolio {{
    min-height: 100vh;
  }}

  /* Navigation */
  nav {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: transparent;
    padding: 1.5rem 0;
    z-index: 1000;
    transition: all 0.3s ease;
  }}

  nav.scrolled {{
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    padding: 1rem 0;
  }}

  .nav-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .logo {{
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .nav-links {{
    display: flex;
    gap: 2rem;
  }}

  .nav-links a {{
    color: var(--text-dark);
    text-decoration: none;
    font-weight: 500;
    cursor: pointer;
    transition: color 0.3s;
  }}

  .nav-links a:hover {{
    color: var(--primary);
  }}

  /* Hero Section */
  .hero {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6rem 2rem;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
  }}

  .hero-content {{
    text-align: center;
    max-width: 600px;
  }}

  .hero-title {{
    font-size: 3.5rem;
    margin-bottom: 1rem;
    line-height: 1.2;
  }}

  .hero-subtitle {{
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    opacity: 0.9;
  }}

  .typing-text {{
    color: #ffd700;
    font-weight: 600;
  }}

  .hero-description {{
    font-size: 1.1rem;
    margin-bottom: 2rem;
    opacity: 0.95;
  }}

  .hero-buttons {{
    display: flex;
    gap: 1rem;
    justify-content: center;
  }}

  .btn-primary {{
    background: white;
    color: var(--primary);
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.3s;
    text-decoration: none;
  }}

  .btn-primary:hover {{
    transform: translateY(-2px);
  }}

  .btn-secondary {{
    background: transparent;
    color: white;
    padding: 0.75rem 2rem;
    border: 2px solid white;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }}

  .btn-secondary:hover {{
    background: white;
    color: var(--primary);
  }}

  /* Sections */
  .section {{
    padding: 5rem 2rem;
    background: var(--white);
  }}

  .section-alt {{
    background: var(--bg-light);
  }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
  }}

  .section-title {{
    font-size: 2.5rem;
    margin-bottom: 3rem;
    text-align: center;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  /* About Section */
  .about-content {{
    display: grid;
    gap: 3rem;
  }}

  .about-text h3 {{
    font-size: 1.5rem;
    margin: 1.5rem 0 0.75rem;
    color: var(--primary);
  }}

  .about-text p {{
    color: var(--text-light);
  }}

  .education-list {{
    display: grid;
    gap: 1.5rem;
  }}

  .education-item {{
    padding: 1.5rem;
    background: white;
    border-radius: 8px;
    border-left: 4px solid var(--primary);
  }}

  .education-item h4 {{
    color: var(--primary);
    margin-bottom: 0.5rem;
  }}

  .education-year {{
    color: var(--text-light);
    font-size: 0.9rem;
  }}

  /* Skills Section */
  .skills-grid {{
    display: grid;
    gap: 2rem;
  }}

  .skill-category {{
    padding: 1.5rem;
    background: white;
    border-radius: 8px;
    border: 2px solid var(--bg-light);
  }}

  .skill-category h3 {{
    color: var(--primary);
    margin-bottom: 1rem;
  }}

  .skills-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }}

  .skill-tag {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
  }}

  /* Projects Section */
  .projects-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }}

  .project-card {{
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    border: 2px solid var(--bg-light);
    transition: all 0.3s;
  }}

  .project-card:hover {{
    border-color: var(--primary);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transform: translateY(-5px);
  }}

  .project-card h3 {{
    color: var(--primary);
    margin-bottom: 0.75rem;
  }}

  .project-desc {{
    color: var(--text-light);
    margin-bottom: 1rem;
  }}

  .project-tech {{
    display: block;
    font-size: 0.85rem;
    color: var(--text-light);
    margin-bottom: 1rem;
  }}

  .project-link {{
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s;
  }}

  .project-link:hover {{
    color: var(--secondary);
  }}

  /* Contact Section */
  .contact-content {{
    text-align: center;
    max-width: 500px;
    margin: 0 auto;
  }}

  .contact-email {{
    font-size: 1.2rem;
    margin-bottom: 0.75rem;
  }}

  .contact-phone {{
    margin-bottom: 2rem;
  }}

  /* Footer */
  .footer {{
    background: var(--text-dark);
    color: white;
    text-align: center;
    padding: 2rem;
    margin-top: 3rem;
  }}

  @media (max-width: 768px) {{
    .hero-title {{
      font-size: 2rem;
    }}

    .hero-subtitle {{
      font-size: 1.2rem;
    }}

    .section-title {{
      font-size: 1.8rem;
    }}

    .nav-links {{
      gap: 1rem;
    }}

    .projects-grid {{
      grid-template-columns: 1fr;
    }}

    .hero-buttons {{
      flex-direction: column;
    }}
  }}
</style>''',
            
            "src/style.css": f'''/* Global Styles */

:root {{
  --primary: {primary_color};
  --secondary: {secondary_color};
}}
}}

.section-alt {{
  background: var(--bg-light);
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}}

.section-title {{
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
  color: var(--text-dark);
}}

.section-title::after {{
  content: '';
  display: block;
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  margin: 1rem auto 0;
  border-radius: 2px;
}}

/* About Section */
.about-content {{
  max-width: 900px;
  margin: 0 auto;
}}

.about-text h3 {{
  font-size: 1.8rem;
  color: var(--text-dark);
  margin-top: 2rem;
  margin-bottom: 1rem;
}}

.about-text p {{
  color: var(--text-light);
  font-size: 1.1rem;
  line-height: 1.8;
}}

.education-list {{
  margin-top: 1.5rem;
}}

.education-item {{
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: var(--white);
  border-radius: 12px;
  border-left: 4px solid var(--primary);
}}

.education-item h4 {{
  color: var(--text-dark);
  font-size: 1.2rem;
}}

.education-year {{
  color: var(--text-light);
  font-size: 0.9rem;
}}

/* Skills Section */
.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}}

.skill-category {{
  padding: 2rem;
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: transform 0.3s ease;
}}

.skill-category:hover {{
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}}

.skill-category h3 {{
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--text-dark);
}}

.skills-list {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}}

.skill-tag {{
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: var(--white);
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
}}

/* Projects Section */
.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2.5rem;
}}

.project-card {{
  background: var(--white);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}}

.project-card:hover {{
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary);
}}

.project-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}}

.project-header h3 {{
  font-size: 1.4rem;
  color: var(--text-dark);
}}

.project-year {{
  color: var(--text-light);
  font-size: 0.9rem;
}}

.project-role {{
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 0.8rem;
}}

.project-desc {{
  color: var(--text-light);
  margin-bottom: 1rem;
  line-height: 1.7;
}}

.project-tech {{
  color: var(--text-light);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}}

.project-link {{
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}}

.project-link:hover {{
  gap: 0.8rem;
}}

/* Contact Section */
.contact-content {{
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}}

.contact-email,
.contact-phone {{
  font-size: 1.3rem;
  color: var(--text-dark);
  margin-bottom: 1.5rem;
}}

/* Footer */
.footer {{
  background: var(--text-dark);
  color: var(--white);
  text-align: center;
  padding: 2rem;
}}

/* Animations */
@keyframes fadeInUp {{
  from {{
    opacity: 0;
    transform: translateY(30px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes typing {{
  from {{ width: 0 }}
  to {{ width: 100% }}
}}

@keyframes blink {{
  50% {{ border-color: transparent }}
}}

/* Responsive */
@media (max-width: 768px) {{
  .hero-title {{
    font-size: 2.5rem;
  }}
  
  .hero-subtitle {{
    font-size: 1.5rem;
  }}
  
  .nav-links {{
    gap: 1rem;
  }}
  
  .section-title {{
    font-size: 2rem;
  }}
  
  .projects-grid,
  .skills-grid {{
    grid-template-columns: 1fr;
  }}
}}''',
            
            "README.md": f"# {name}'s Portfolio\n\nModern Svelte portfolio built with Svelte + Vite\n\n## Run Locally\n```bash\nnpm install\nnpm run dev\n```"
        }

    def _generate_svelte(self, data: Dict, options: Dict, template_id: str = "modern-gradient") -> Dict[str, str]:
        """Generate Svelte + Vite portfolio"""
        
        # Extract data
        name = self._sanitize_html(data.get('name', 'Your Name'))
        title = self._sanitize_html(data.get('title', 'Full Stack Developer'))
        email = self._sanitize_html(data.get('email', ''))
        phone = self._sanitize_html(data.get('phone', ''))
        summary = self._sanitize_html(data.get('summary', ''))
        skills = data.get('skills', [])
        experience = data.get('experience', [])
        education = data.get('education', [])
        projects = data.get('projects', [])
        
        # Get theme configuration
        theme = self._get_theme_config(options)
        
        # Color theme from options (not theme config)
        primary = options.get('primaryColor', '#667eea')
        secondary = options.get('secondaryColor', '#764ba2')
        
        # Pre-build skills HTML to avoid f-string bracket issues
        skills_html = ''.join([f'<div class="skill-tag">{self._sanitize_html(skill)}</div>' for skill in skills[:12]])
        
        # Pre-build projects HTML
        projects_html = ''
        for proj in projects[:6]:
            tech_tags = ''.join([f'<span class="tech-tag">{self._sanitize_html(tech)}</span>' for tech in proj.get('technologies', [])[:3]])
            projects_html += f'''
      <div class="project-card">
        <h3>{self._sanitize_html(proj.get('name', 'Project'))}</h3>
        <p>{self._sanitize_html(proj.get('description', ''))[:150]}</p>
        <div class="project-tech">
          {tech_tags}
        </div>
      </div>
      '''

        
        return {
            "package.json": json.dumps({
                "name": "svelte-portfolio",
                "version": "1.0.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "devDependencies": {
                    "@sveltejs/vite-plugin-svelte": "^3.0.0",
                    "svelte": "^4.0.0",
                    "vite": "^5.0.0"
                }
            }, indent=2),
            
            "index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Portfolio</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>''',
            
            "src/main.js": '''import App from './App.svelte';
import './app.css';

const app = new App({
  target: document.getElementById('app')
});

export default app;''',
            
            f"src/App.svelte": f'''<script>
  let scrolled = false;
  
  function handleScroll() {{
    scrolled = window.scrollY > 50;
  }}
  
  function scrollToSection(id) {{
    document.getElementById(id)?.scrollIntoView({{ behavior: 'smooth' }});
  }}
</script>

<svelte:window on:scroll={{handleScroll}} />

<nav class:scrolled>
  <div class="nav-container">
    <h2 class="logo">{name}</h2>
    <div class="nav-links">
      <button on:click={{() => scrollToSection('about')}}>About</button>
      <button on:click={{() => scrollToSection('skills')}}>Skills</button>
      <button on:click={{() => scrollToSection('projects')}}>Projects</button>
      <button on:click={{() => scrollToSection('contact')}}>Contact</button>
    </div>
  </div>
</nav>

<section class="hero">
  <div class="hero-content">
    <h1 class="glitch" data-text="{name}">{name}</h1>
    <p class="subtitle">{title}</p>
    <p class="tagline">{summary if summary else "Crafting digital experiences with code"}</p>
    <button class="cta-button" on:click={{() => scrollToSection('projects')}}>View My Work</button>
  </div>
</section>

<section id="about" class="section about">
  <div class="container">
    <h2 class="section-title">About Me</h2>
    <p class="about-text">{summary if summary else "Passionate developer creating innovative solutions."}</p>
  </div>
</section>

<section id="skills" class="section">
  <div class="container">
    <h2 class="section-title">Skills</h2>
    <div class="skills-grid">
      {skills_html}
    </div>
  </div>
</section>

<section id="projects" class="section">
  <div class="container">
    <h2 class="section-title">Featured Projects</h2>
    <div class="projects-grid">
      {projects_html}
    </div>
  </div>
</section>

<section id="contact" class="section contact">
  <div class="container">
    <h2 class="section-title">Get In Touch</h2>
    <p class="contact-text">Let's work together on your next project</p>
    <div class="contact-links">
      {f'<a href="mailto:{email}" class="contact-button">Email Me</a>' if email else ''}
      {f'<a href="tel:{phone}" class="contact-button">Call Me</a>' if phone else ''}
    </div>
  </div>
</section>

<footer>
  <p>&copy; 2024 {name}. All rights reserved.</p>
</footer>

<style>
  /* Global styles in app.css */
</style>''',
            
            f"src/app.css": f'''* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0a0e27;
  color: #ffffff;
  overflow-x: hidden;
}}

nav {{
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(10, 14, 39, 0.8);
  backdrop-filter: blur(10px);
  z-index: 1000;
  transition: all 0.3s;
}}

nav.scrolled {{
  background: rgba(10, 14, 39, 0.95);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}}

.nav-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.logo {{
  font-size: 1.5rem;
  background: linear-gradient(135deg, {primary}, {secondary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.nav-links {{
  display: flex;
  gap: 2rem;
}}

.nav-links button {{
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  transition: color 0.3s;
}}

.nav-links button:hover {{
  color: {primary};
}}

.hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
  position: relative;
  overflow: hidden;
}}

.hero-content {{
  text-align: center;
  z-index: 1;
}}

.glitch {{
  font-size: 4rem;
  font-weight: 900;
  margin-bottom: 1rem;
  position: relative;
}}

.subtitle {{
  font-size: 2rem;
  margin-bottom: 1rem;
  opacity: 0.9;
}}

.tagline {{
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.8;
}}

.cta-button {{
  background: #fff;
  color: #0a0e27;
  border: none;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
}}

.cta-button:hover {{
  transform: translateY(-3px);
  box-shadow: 0 15px 40px rgba(255, 255, 255, 0.3);
}}

.section {{
  padding: 5rem 2rem;
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
}}

.section-title {{
  font-size: 2.5rem;
  margin-bottom: 3rem;
  text-align: center;
  background: linear-gradient(135deg, {primary}, {secondary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}}

.skill-tag {{
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.2);
}}

.skill-tag:hover {{
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-5px);
}}

.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}}

.project-card {{
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}}

.project-card:hover {{
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  background: rgba(255, 255, 255, 0.08);
}}

.project-tech {{
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}}

.tech-tag {{
  background: {primary};
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
}}

.contact {{
  text-align: center;
}}

.contact-text {{
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.8;
}}

.contact-links {{
  display: flex;
  gap: 1rem;
  justify-content: center;
}}

.contact-button {{
  background: linear-gradient(135deg, {primary}, {secondary});
  color: #fff;
  text-decoration: none;
  padding: 1rem 2rem;
  border-radius: 50px;
  transition: all 0.3s;
}}

.contact-button:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
}}

footer {{
  background: #050814;
  padding: 2rem;
  text-align: center;
  opacity: 0.7;
}}

@media (max-width: 768px) {{
  .hero {{
    padding: 2rem;
  }}
  
  .glitch {{
    font-size: 2.5rem;
  }}
  
  .subtitle {{
    font-size: 1.5rem;
  }}
  
  .nav-links {{
    gap: 1rem;
  }}
  
  .projects-grid, .skills-grid {{
    grid-template-columns: 1fr;
  }}
}}''',
            
            "README.md": f"# {name}'s Portfolio\n\nModern Svelte portfolio built with Svelte + Vite\n\n## Run Locally\n```bash\nnpm install\nnpm run dev\n```"
        }

template_engine = TemplateEngine()

