from enum import Enum
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
import random

class TemplateStyle(Enum):
    MINIMAL = "minimal"
    MODERN = "modern"
    GRADIENT = "gradient"
    DARK = "dark"
    COLORFUL = "colorful"

class TemplateLayout(Enum):
    SINGLE_PAGE = "single_page"
    MULTI_SECTION = "multi_section"

@dataclass
class TemplateMetadata:
    name: str
    style: TemplateStyle
    layout: TemplateLayout
    description: str
    animation_level: int
    features: List[str]
    supported_stacks: List[str]
    color_schemes: List[Tuple[str, str]]

class TemplateRegistry:
    def __init__(self):
        self.templates: Dict[str, TemplateMetadata] = {
            "modern-gradient": TemplateMetadata(
                name="Modern Gradient",
                style=TemplateStyle.GRADIENT,
                layout=TemplateLayout.SINGLE_PAGE,
                description="Modern portfolio with gradient backgrounds",
                animation_level=2,
                features=["Smooth scrolling", "Gradient hero", "Card layouts"],
                supported_stacks=["react", "nextjs", "vue", "svelte"],
                color_schemes=[
                    ('#667eea', '#764ba2'),
                    ('#4facfe', '#00f2fe'),
                    ('#43e97b', '#38f9d7'),
                ]
            )
        }
    
    def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        return self.templates.get(template_id)
    
    def get_random_template(self, stack: Optional[str] = None, style: Optional[TemplateStyle] = None) -> Tuple[str, TemplateMetadata]:
        filtered = self.templates
        if stack:
            filtered = {k: v for k, v in filtered.items() if stack in v.supported_stacks}
        if style:
            filtered = {k: v for k, v in filtered.items() if v.style == style}
        
        if not filtered:
            template_id = "modern-gradient"
            return template_id, self.templates[template_id]
        
        template_id = random.choice(list(filtered.keys()))
        return template_id, filtered[template_id]
    
    def get_random_color_scheme(self, template_id: str) -> Tuple[str, str]:
        template = self.templates.get(template_id)
        if not template or not template.color_schemes:
            return ('#667eea', '#764ba2')
        return random.choice(template.color_schemes)
    
    def list_templates(self, stack: Optional[str] = None, style: Optional[TemplateStyle] = None) -> Dict[str, TemplateMetadata]:
        filtered = self.templates
        if stack:
            filtered = {k: v for k, v in filtered.items() if stack in v.supported_stacks}
        if style:
            filtered = {k: v for k, v in filtered.items() if v.style == style}
        return filtered
    
    def suggest_template(self, prompt: str, stack: Optional[str] = None) -> Tuple[str, TemplateMetadata]:
        # Simple keyword matching for now
        prompt_lower = prompt.lower()
        if "minimal" in prompt_lower:
            return self.get_random_template(stack, TemplateStyle.MINIMAL)
        elif "dark" in prompt_lower:
            return self.get_random_template(stack, TemplateStyle.DARK)
        else:
            return self.get_random_template(stack)

template_registry = TemplateRegistry()
