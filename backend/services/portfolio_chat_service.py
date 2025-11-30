"""
Chat service for AI-powered portfolio modifications and improvements
Users can chat with AI to request changes, improvements, and design suggestions
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import AsyncOpenAI
import json

@dataclass
class ChatMessage:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class PortfolioChatService:
    """AI-powered chat for portfolio customization and improvements"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"
        self.conversation_history: List[ChatMessage] = []
    
    def add_system_context(self, user_data: Dict):
        """Add context about the user's portfolio"""
        self.user_data = user_data
        self.system_prompt = self._create_system_prompt(user_data)
    
    def _create_system_prompt(self, user_data: Dict) -> str:
        """Create a detailed system prompt with portfolio context"""
        return f"""
You are an EXPERT AI designer, UX specialist, and portfolio strategist helping a user create a WORLD-CLASS professional portfolio website.

User Information:
- Name: {user_data.get('name', 'Developer')}
- Title: {user_data.get('title', 'Full Stack Developer')}
- Bio: {user_data.get('summary', '')}
- Key Skills: {', '.join(user_data.get('skills', [])[:10])}
- Experience Level: {len(user_data.get('experience', []))} positions
- Education: {len(user_data.get('education', []))} degrees

Your EXTENSIVE Expertise Covers:
1. **Design Systems & Patterns**
   - Layout systems (Grid, Flexbox, CSS)
   - Component architecture and reusability
   - Responsive design for all devices
   - Accessibility (WCAG 2.1 AA+)
   - Performance optimization

2. **Advanced Styling Techniques**
   - Glassmorphism and modern effects
   - Advanced gradient combinations
   - Complex animations and transitions
   - SVG and CSS art techniques
   - Dark/light mode implementations
   - Custom typography systems

3. **User Experience Strategy**
   - Information architecture
   - Navigation patterns
   - Call-to-action optimization
   - User flow optimization
   - Conversion rate optimization
   - Color psychology and brand alignment

4. **Advanced CSS & Animations**
   - Keyframe animations
   - CSS Grid mastery
   - Flexbox advanced patterns
   - CSS custom properties
   - Backdrop filters and effects
   - Smooth scroll behaviors
   - Parallax and scroll effects

5. **Interactive Elements**
   - Form optimization
   - Interactive components
   - Micro-interactions
   - Loading states and feedback
   - Hover effects and transitions
   - Mobile gesture support

6. **Portfolio-Specific Strategies**
   - Showcase best projects prominently
   - Tell compelling career story
   - Optimize for recruiters/clients
   - Demonstrate technical skills
   - Show personality and unique brand
   - Include social proof

7. **Code Quality & Performance**
   - Clean, maintainable CSS
   - Performance optimization
   - Lazy loading strategies
   - Image optimization
   - Code splitting
   - Browser compatibility

8. **Advanced Features**
   - Dark mode implementation
   - Animations and interactions
   - Search functionality
   - Filtering and sorting
   - Analytics integration
   - SEO optimization

Your Approach:
- **COMPREHENSIVE**: Provide detailed, multi-faceted suggestions
- **STRATEGIC**: Think about career impact, not just aesthetics
- **PRACTICAL**: Always provide ready-to-implement code
- **EDUCATIONAL**: Explain the "why" behind recommendations
- **ADAPTIVE**: Suggest multiple options for user choice
- **AMBITIOUS**: Push for excellence, not just adequacy

When Suggesting Changes:
1. Analyze the current state
2. Identify 3-5 specific improvements
3. Explain the visual/UX impact
4. Provide complete, copy-paste code
5. Suggest advanced enhancements
6. Offer implementation tips
7. Explain why each change matters

Advanced Suggestion Patterns:
- Don't just change colors; suggest a cohesive color system
- Don't just adjust spacing; redesign the rhythm system
- Don't just add animation; create a motion design strategy
- Don't just fix one section; suggest how to improve the whole flow
- Don't just provide CSS; explain the design principles

You are not just a tool; you are a STRATEGIC DESIGN PARTNER helping create a portfolio that will:
✅ Impress top tech companies
✅ Attract high-quality clients
✅ Showcase unique expertise
✅ Get more interviews
✅ Command higher rates
✅ Build professional reputation
"""
    
    async def chat(self, user_message: str) -> Dict:
        """
        Process a user message and get AI response with suggestions
        
        Args:
            user_message: The user's message
        
        Returns:
            Dictionary with:
            - response: AI's conversational response
            - code_suggestions: Any specific code changes recommended
            - design_tips: Design principles explained
            - next_steps: Suggested next actions
        """
        
        # Add user message to history
        self.conversation_history.append(
            ChatMessage(role='user', content=user_message)
        )
        
        # Prepare messages for API
        messages = [
            {'role': 'system', 'content': self.system_prompt}
        ]
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append({'role': msg.role, 'content': msg.content})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=2000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append(
                ChatMessage(role='assistant', content=assistant_message)
            )
            
            # Parse response for code suggestions
            parsed = self._parse_response(assistant_message)
            
            return {
                'response': parsed['conversation'],
                'code_suggestions': parsed['code'],
                'design_tips': parsed['tips'],
                'next_steps': parsed['next_steps'],
                'full_response': assistant_message
            }
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return {
                'response': f"I encountered an error: {str(e)}",
                'code_suggestions': None,
                'design_tips': None,
                'next_steps': None
            }
    
    def _parse_response(self, response: str) -> Dict:
        """Parse AI response to extract different types of content"""
        
        result = {
            'conversation': response,
            'code': None,
            'tips': None,
            'next_steps': None
        }
        
        # Look for code blocks
        if '```' in response:
            import re
            code_blocks = re.findall(r'```(?:css|html|javascript|js)?\n(.*?)```', response, re.DOTALL)
            if code_blocks:
                result['code'] = code_blocks
        
        # Extract design tips if mentioned
        if 'tip' in response.lower() or 'suggest' in response.lower():
            result['tips'] = self._extract_tips(response)
        
        # Extract next steps
        if 'next' in response.lower() or 'try' in response.lower():
            result['next_steps'] = self._extract_next_steps(response)
        
        return result
    
    def _extract_tips(self, text: str) -> List[str]:
        """Extract design tips from response"""
        tips = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['tip:', 'suggestion:', '•', '-', '✓']):
                tips.append(line.strip())
        return tips[:5]  # Return top 5 tips
    
    def _extract_next_steps(self, text: str) -> List[str]:
        """Extract suggested next steps"""
        steps = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['next', 'try', 'consider', 'could', 'might']):
                steps.append(line.strip())
        return steps[:3]  # Return top 3 suggestions
    
    async def get_design_suggestions(self, focus_area: str) -> Dict:
        """
        Get specific design suggestions for a particular area
        
        Args:
            focus_area: Area to improve (e.g., 'hero section', 'colors', 'typography', 'animations')
        
        Returns:
            Specific suggestions with code examples
        """
        
        prompt = f"""
The user wants to improve the {focus_area} of their portfolio.

Provide:
1. Three specific, actionable improvements
2. CSS code examples for each
3. Before/after visual descriptions
4. Why each improvement matters

Format your response clearly with:
- **Improvement 1**: [title]
- **Why**: [reason]
- **Code**:
  ```css
  [complete CSS]
  ```
- **Visual Impact**: [description]

Then repeat for improvements 2 and 3.
"""
        
        message = ChatMessage(role='user', content=prompt)
        self.conversation_history.append(message)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.9,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            self.conversation_history.append(
                ChatMessage(role='assistant', content=content)
            )
            
            return {
                'suggestions': content,
                'focus_area': focus_area,
                'code_snippets': self._extract_code_blocks(content)
            }
            
        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return {'suggestions': f"Error: {str(e)}", 'code_snippets': []}
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract all code blocks from response"""
        import re
        pattern = r'```(?:css|html|javascript|js)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return [msg.to_dict() for msg in self.conversation_history]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def get_quick_tips(self) -> Dict:
        """Get quick portfolio improvement tips"""
        prompt = """
Give 5 quick, actionable tips to improve this portfolio in less than 2 minutes of CSS changes.
Focus on high-impact improvements that look premium.

Format as:
1. **[Title]**: [1 sentence description] 
   Quick CSS: [1-2 lines of code]

Keep it practical and implementable immediately.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                'tips': response.choices[0].message.content,
                'type': 'quick_wins'
            }
            
        except Exception as e:
            return {'tips': f"Error: {str(e)}", 'type': 'error'}
    
    async def get_advanced_code_generation(self, request: str) -> Dict:
        """Generate advanced, production-quality code"""
        prompt = f"""
The user wants: {request}

Generate ADVANCED, PRODUCTION-QUALITY code that includes:

1. **Complete Implementation**
   - Full working code (not snippets)
   - All necessary selectors and properties
   - Fallbacks for older browsers

2. **Advanced CSS Techniques**
   - CSS Grid/Flexbox mastery
   - CSS custom properties for theming
   - Advanced selectors and nesting
   - Keyframe animations
   - Media queries for all devices

3. **Performance Optimization**
   - Hardware-accelerated animations (transform, opacity)
   - Efficient selectors
   - Lazy loading patterns
   - Image optimization recommendations

4. **Accessibility**
   - WCAG 2.1 AA compliance
   - Proper contrast ratios
   - Focus states for keyboard navigation
   - Semantic HTML suggestions

5. **Cross-browser Compatibility**
   - Vendor prefixes where needed
   - Fallbacks for older browsers
   - Feature detection

Return as JSON:
{{
    "css": "/* Complete, production-ready CSS */",
    "html": "<!-- Updated HTML structure if needed -->",
    "javascript": "// Any interactive code needed",
    "explanation": "Why these choices, visual impact, benefits",
    "browser_support": "Which browsers this works on",
    "performance_tips": ["Optimization suggestions"],
    "accessibility_notes": ["WCAG compliance details"]
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {
                    'css': content,
                    'explanation': 'Generated code above',
                    'browser_support': 'Modern browsers'
                }
        
        except Exception as e:
            return {'error': str(e)}
    
    async def get_design_strategy(self) -> Dict:
        """Get comprehensive design strategy for the portfolio"""
        prompt = """
Provide a COMPREHENSIVE DESIGN STRATEGY for this portfolio that covers:

1. **Visual Hierarchy**
   - How to organize information
   - Typography scale
   - Color distribution

2. **Branding**
   - Color palette recommendations
   - Font pairing suggestions
   - Visual identity system

3. **User Experience**
   - Navigation flow
   - Call-to-action placement
   - Conversion optimization

4. **Layout Strategy**
   - Section ordering
   - Whitespace usage
   - Content grouping

5. **Advanced Features**
   - Interactive elements to add
   - Animations that enhance UX
   - Micro-interactions

6. **Performance & SEO**
   - Performance optimization
   - SEO best practices
   - Lighthouse score improvement

Return as JSON:
{{
    "color_strategy": "Detailed color approach",
    "typography": "Font recommendations and scale",
    "layout_approach": "How to structure sections",
    "interactive_elements": ["Elements to make interactive"],
    "animations": "Which animations to implement",
    "performance_checklist": ["Items to optimize"],
    "estimated_impact": "Expected results (interviews, visibility)"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.8,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {'strategy': content}
        
        except Exception as e:
            return {'error': str(e)}
    
    async def get_multiple_approaches(self, feature: str) -> Dict:
        """Generate multiple implementation approaches"""
        prompt = f"""
For: {feature}

Generate 3 DIFFERENT APPROACHES with varying complexity and impact:

APPROACH 1: SIMPLE (Quick to implement)
- Simple CSS changes
- Minimal code
- Good visual improvement
- Time: < 5 minutes

APPROACH 2: INTERMEDIATE (Better design)
- Moderate CSS complexity
- Animations included
- Professional appearance
- Time: 10-15 minutes

APPROACH 3: ADVANCED (Expert-level)
- Advanced CSS techniques
- Complex animations
- Accessibility features
- Performance optimized
- Time: 20-30 minutes

For each, provide:
- Complete code
- Visual description
- Implementation steps
- Browser support
- When to use it

Format as JSON with approaches array.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.8,
                max_tokens=3500
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {'approaches': content}
        
        except Exception as e:
            return {'error': str(e)}
