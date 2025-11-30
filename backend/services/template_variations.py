"""
Template Generation Helpers
Provides methods for generating different UI variations based on template ID
"""

def get_minimal_clean_styles(primary_color: str, secondary_color: str) -> str:
    """Generate CSS for minimal clean template"""
    return f'''/* Minimal Clean Portfolio Styles */

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

:root {{
  --primary: {primary_color};
  --secondary: {secondary_color};
  --text-dark: #1a1a1a;
  --text-light: #666;
  --text-lighter: #999;
  --bg-white: #ffffff;
  --bg-light: #f5f5f5;
  --border: #e0e0e0;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text-dark);
  line-height: 1.8;
  letter-spacing: 0.3px;
}}

.portfolio {{
  min-height: 100vh;
  background: var(--bg-white);
}}

/* Minimal Navigation */
nav {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 0;
  z-index: 1000;
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
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: var(--text-dark);
}}

.nav-links {{
  display: flex;
  gap: 3rem;
}}

.nav-links a {{
  color: var(--text-light);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.3s;
  cursor: pointer;
}}

.nav-links a:hover {{
  color: var(--text-dark);
}}

/* Minimal Hero */
.hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 60px;
  text-align: center;
}}

.hero-content {{
  max-width: 700px;
  padding: 2rem;
}}

.hero-title {{
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -2px;
  margin-bottom: 1rem;
  line-height: 1.2;
}}

.hero-subtitle {{
  font-size: 1.4rem;
  color: var(--text-light);
  margin-bottom: 2rem;
  font-weight: 400;
}}

.hero-description {{
  font-size: 1.1rem;
  color: var(--text-light);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}}

.hero-buttons {{
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}}

/* Buttons */
.btn-primary,
.btn-secondary {{
  padding: 0.8rem 2rem;
  font-size: 0.95rem;
  font-weight: 600;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}}

.btn-primary {{
  background: var(--primary);
  color: white;
}}

.btn-primary:hover {{
  background: var(--secondary);
}}

.btn-secondary {{
  background: var(--bg-light);
  color: var(--text-dark);
  border: 1px solid var(--border);
}}

.btn-secondary:hover {{
  border-color: var(--primary);
}}

/* Sections */
.section {{
  padding: 6rem 0;
  border-bottom: 1px solid var(--border);
}}

.section:last-child {{
  border-bottom: none;
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
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -1px;
  margin-bottom: 3rem;
  text-align: center;
}}

/* Skills */
.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}}

.skill-category {{
  padding: 2rem;
}}

.skill-category h3 {{
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
}}

.skill-tag {{
  display: inline-block;
  padding: 0.5rem 1rem;
  background: var(--bg-light);
  border: 1px solid var(--border);
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 0;
  font-size: 0.9rem;
}}

/* Projects */
.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 3rem;
}}

.project-card {{
  padding: 0;
  border: 1px solid var(--border);
  transition: all 0.3s;
}}

.project-card:hover {{
  border-color: var(--primary);
}}

.project-header h3 {{
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}}

.project-desc {{
  color: var(--text-light);
  margin-bottom: 1rem;
  font-size: 0.95rem;
}}

/* Contact */
.contact-content {{
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}}

.contact-email {{
  font-size: 1.2rem;
  margin-bottom: 2rem;
}}

/* Footer */
.footer {{
  border-top: 1px solid var(--border);
  padding: 2rem;
  text-align: center;
  color: var(--text-light);
  font-size: 0.9rem;
}}

@media (max-width: 768px) {{
  .hero-title {{
    font-size: 2rem;
  }}
  
  .nav-links {{
    gap: 1.5rem;
  }}
  
  .projects-grid {{
    grid-template-columns: 1fr;
  }}
}}'''


def get_dark_professional_styles(primary_color: str, secondary_color: str) -> str:
    """Generate CSS for dark professional template"""
    return f'''/* Dark Professional Portfolio Styles */

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

:root {{
  --primary: {primary_color};
  --secondary: {secondary_color};
  --bg-dark: #0f0f0f;
  --bg-darker: #1a1a1a;
  --text-light: #e0e0e0;
  --text-lighter: #a0a0a0;
  --card-bg: #1a1a2e;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text-light);
  background: var(--bg-dark);
  line-height: 1.6;
}}

.portfolio {{
  min-height: 100vh;
}}

/* Dark Navigation */
nav {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: var(--bg-darker);
  border-bottom: 1px solid var(--primary);
  border-bottom-width: 2px;
  opacity: 0.95;
  padding: 1.5rem 0;
  z-index: 1000;
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
  font-size: 1.3rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.nav-links {{
  display: flex;
  gap: 2.5rem;
}}

.nav-links a {{
  color: var(--text-lighter);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  cursor: pointer;
}}

.nav-links a:hover {{
  color: var(--primary);
}}

/* Dark Hero */
.hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--bg-darker) 0%, var(--card-bg) 100%);
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
  background: radial-gradient(circle at 20% 50%, var(--primary)05 0%, transparent 50%);
  pointer-events: none;
}}

.hero-content {{
  position: relative;
  text-align: center;
  max-width: 800px;
  padding: 2rem;
}}

.hero-title {{
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 1rem;
}}

.hero-subtitle {{
  font-size: 1.8rem;
  color: var(--primary);
  margin-bottom: 1.5rem;
}}

.hero-description {{
  font-size: 1.1rem;
  color: var(--text-lighter);
  margin-bottom: 2rem;
}}

/* Buttons */
.btn-primary {{
  padding: 1rem 2.5rem;
  background: var(--primary);
  color: #000;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}}

.btn-primary:hover {{
  background: var(--secondary);
  transform: translateY(-3px);
}}

.btn-secondary {{
  padding: 1rem 2.5rem;
  background: transparent;
  color: var(--primary);
  border: 2px solid var(--primary);
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}}

.btn-secondary:hover {{
  background: var(--primary);
  color: #000;
}}

/* Sections */
.section {{
  padding: 6rem 0;
}}

.section-alt {{
  background: var(--card-bg);
  border-top: 1px solid var(--primary);
  border-bottom: 1px solid var(--primary);
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
}}

.section-title::after {{
  content: '';
  display: block;
  width: 60px;
  height: 3px;
  background: var(--primary);
  margin: 1rem auto 0;
}}

/* Skills */
.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}}

.skill-category {{
  padding: 2rem;
  background: var(--bg-darker);
  border: 1px solid var(--primary);
  border-radius: 8px;
  transition: all 0.3s;
}}

.skill-category:hover {{
  border-color: var(--secondary);
  box-shadow: 0 0 20px var(--primary)20;
}}

.skill-tag {{
  display: inline-block;
  padding: 0.5rem 1rem;
  background: var(--primary);
  color: #000;
  border-radius: 50px;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
}}

/* Projects */
.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2.5rem;
}}

.project-card {{
  background: var(--card-bg);
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid var(--primary);
  transition: all 0.3s;
}}

.project-card:hover {{
  border-color: var(--secondary);
  box-shadow: 0 0 30px var(--secondary)40;
  transform: translateY(-5px);
}}

.project-header h3 {{
  color: var(--primary);
  font-size: 1.4rem;
  margin-bottom: 0.5rem;
}}

.project-desc {{
  color: var(--text-lighter);
  margin-bottom: 1rem;
}}

/* Footer */
.footer {{
  background: var(--bg-darker);
  border-top: 2px solid var(--primary);
  color: var(--text-lighter);
  text-align: center;
  padding: 2rem;
}}

@media (max-width: 768px) {{
  .hero-title {{
    font-size: 2.5rem;
  }}
  
  .projects-grid {{
    grid-template-columns: 1fr;
  }}
}}'''


def get_creative_timeline_html(resume_data: dict, name: str) -> str:
    """Generate HTML structure for timeline layout"""
    education = resume_data.get('education', [])
    experience = resume_data.get('experience', [])
    
    timeline_events = []
    
    # Add education
    for edu in education:
        timeline_events.append({
            'year': edu.get('year', 'N/A'),
            'title': edu.get('degree', 'Education'),
            'company': edu.get('school', ''),
            'description': f"Completed {edu.get('degree', 'degree')} at {edu.get('school', '')}",
            'type': 'education'
        })
    
    # Add experience
    for exp in experience:
        timeline_events.append({
            'year': exp.get('duration', 'N/A'),
            'title': exp.get('title', 'Experience'),
            'company': exp.get('company', ''),
            'description': exp.get('description', ''),
            'type': 'experience'
        })
    
    # Sort by year (simplified)
    timeline_events.sort(key=lambda x: x['year'], reverse=True)
    
    timeline_html = '<div class="timeline">\n'
    for idx, event in enumerate(timeline_events):
        timeline_html += f'''  <div class="timeline-event timeline-{event['type']}">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <h3>{event['title']}</h3>
      <p class="timeline-company">{event['company']}</p>
      <p class="timeline-year">{event['year']}</p>
      <p>{event['description']}</p>
    </div>
  </div>
'''
    timeline_html += '</div>'
    
    return timeline_html


def get_brutalist_styles() -> str:
    """Generate CSS for brutalist minimal template"""
    return '''/* Brutalist Minimal Portfolio */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --text-color: #000;
  --bg-color: #fff;
  --border-color: #000;
}

body {
  font-family: 'Courier New', monospace;
  color: var(--text-color);
  background: var(--bg-color);
  line-height: 1.6;
}

.portfolio {
  min-height: 100vh;
}

/* Grid-based Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 2rem;
}

/* Navigation */
nav {
  grid-column: 1 / -1;
  border-bottom: 3px solid var(--border-color);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 2rem;
}

.logo {
  font-size: 1.2rem;
  font-weight: bold;
  letter-spacing: 3px;
}

.nav-links {
  display: flex;
  gap: 2rem;
  justify-content: flex-end;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-color);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
}

.nav-links a:hover {
  border-bottom: 2px solid var(--border-color);
}

/* Hero */
.hero {
  grid-column: 1 / -1;
  border: 3px solid var(--border-color);
  padding: 4rem;
  margin-bottom: 4rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  letter-spacing: -2px;
  line-height: 1.2;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.4rem;
  font-weight: normal;
  letter-spacing: 1px;
}

/* Sections */
.section {
  grid-column: 1 / -1;
  border: 3px solid var(--border-color);
  padding: 3rem;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  letter-spacing: 2px;
  margin-bottom: 2rem;
  text-transform: uppercase;
  border-bottom: 3px solid var(--border-color);
  padding-bottom: 1rem;
}

/* Skills */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.skill-category {
  border: 2px solid var(--border-color);
  padding: 1.5rem;
}

.skill-category h3 {
  font-weight: bold;
  letter-spacing: 1px;
  margin-bottom: 1rem;
  text-transform: uppercase;
  font-size: 1rem;
}

.skill-tag {
  display: inline-block;
  padding: 0.5rem 1rem;
  border: 2px solid var(--border-color);
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
  font-size: 0.85rem;
}

/* Projects */
.projects-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.project-card {
  border: 3px solid var(--border-color);
  padding: 2rem;
}

.project-header h3 {
  font-size: 1.2rem;
  font-weight: bold;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}

.project-desc {
  line-height: 1.8;
  margin-bottom: 1rem;
}

/* Buttons */
.btn-primary {
  background: var(--text-color);
  color: var(--bg-color);
  padding: 1rem 2rem;
  border: 3px solid var(--text-color);
  font-family: 'Courier New', monospace;
  font-weight: bold;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.btn-primary:hover {
  background: var(--bg-color);
  color: var(--text-color);
}

/* Footer */
.footer {
  grid-column: 1 / -1;
  border-top: 3px solid var(--border-color);
  padding-top: 2rem;
  margin-top: 4rem;
  text-align: center;
  font-weight: bold;
  letter-spacing: 1px;
}

@media (max-width: 768px) {
  .skills-grid,
  .projects-grid {
    grid-template-columns: 1fr;
  }
}'''
