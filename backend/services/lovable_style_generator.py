import os
import json
import re
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from groq import Groq
from .prompts import (
    get_code_mode_prompt,
    get_design_mode_prompt,
    get_advanced_code_mode_prompt,
    get_strategy_mode_prompt,
    get_approaches_mode_prompt
)

logger = logging.getLogger(__name__)

# Constants
MAX_FILES = 60
REQUIRED_CORE_FILES = [
    "package.json",
    "app/layout.tsx",
    "app/page.tsx",
    "tsconfig.json",
    "tailwind.config.ts",
]


class PortfolioGenerator:
    """Lightweight portfolio generator wrapper using Groq.

    This file provides two main async methods used by the app:
    - refine_portfolio(...): runs a blocking refinement and returns a dict
    - stream_refine_portfolio(...): async generator yielding SSE-style events

    The implementations are defensive: if the Groq client is not configured
    (missing `GROQ_API_KEY`), they return a helpful error structure instead
    of raising at import time.
    """

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            logger.info("✅ Groq client initialized")
        else:
            self.client = None
            logger.warning("⚠️  GROQ_API_KEY not found. LLM calls will fail.")

    def _get_system_prompt(self, mode: str = "code") -> str:
        """Get appropriate system prompt for the mode.
        
        Args:
            mode: One of 'code', 'design', 'advanced-code', 'strategy', 'approaches'
        
        Returns:
            Complete system prompt for the mode
        """
        prompts = {
            "code": get_code_mode_prompt,
            "design": get_design_mode_prompt,
            "advanced-code": get_advanced_code_mode_prompt,
            "strategy": get_strategy_mode_prompt,
            "approaches": get_approaches_mode_prompt
        }
        
        prompt_func = prompts.get(mode, get_code_mode_prompt)
        return prompt_func()

    def _extract_json(self, text: str) -> Dict:
        """Try to extract a JSON object from `text`.

        Supports raw JSON or JSON enclosed in markdown code fences.
        Raises ValueError if parsing fails.
        """
        # Try direct JSON parse
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try to find a fenced code block containing JSON
        pattern = r"```(?:json)?\\s*\\n(.*?)\\n```"
        m = re.search(pattern, text, re.DOTALL)
        if m:
            candidate = m.group(1).strip()
            try:
                return json.loads(candidate)
            except Exception:
                pass

        raise ValueError("No valid JSON found in LLM response")

    def _detect_initial_generation(self, current_files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Detect if this is initial generation or incomplete generation.
        
        Returns:
            (is_initial_generation, missing_core_files)
        """
        missing_core_files = [f for f in REQUIRED_CORE_FILES if f not in current_files]
        is_initial = len(current_files) == 0 or bool(missing_core_files)
        return is_initial, missing_core_files

    def _validate_generated_files(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate that generated files meet requirements.
        
        Returns:
            (is_valid, problems_list)
        """
        problems = []
        
        # Check required core files exist
        for required_file in REQUIRED_CORE_FILES:
            if required_file not in files:
                problems.append(f"Missing required file: {required_file}")
        
        # Check file count limit
        if len(files) > MAX_FILES:
            problems.append(f"Too many files generated ({len(files)} > {MAX_FILES})")
        
        # Check app/page.tsx for undefined component imports
        page_content = files.get("app/page.tsx", "")
        if page_content:
            # Find all component imports: import Component from '@/components/Component'
            import_pattern = r"from\\s+['\"]@/components/([\\w/]+)['\"]"
            imports = re.findall(import_pattern, page_content)
            
            for comp_name in imports:
                # Check if component file exists
                comp_file = f"components/{comp_name}.tsx"
                if comp_file not in files:
                    problems.append(f"Component '{comp_name}' imported in app/page.tsx but {comp_file} not created")
        
        is_valid = len(problems) == 0
        return is_valid, problems

    def _build_user_message(
        self,
        refinement_request: str,
        resume_data: Dict,
        source_files: Dict[str, str],
        is_initial_generation: bool,
        missing_core_files: List[str] = None
    ) -> str:
        """Build appropriate user message based on generation type."""
        
        if is_initial_generation:
            missing_files_str = ", ".join(missing_core_files) if missing_core_files else "all files"
            return (
                f"⚠️  IMPORTANT: Generate a COMPLETE Next.js 15 portfolio from scratch.\\n\\n"
                f"Missing files: {missing_files_str}\\n\\n"
                f"REQUIREMENTS:\\n"
                f"1. Create ALL mandatory files: package.json, tsconfig.json, tailwind.config.ts, "
                f"next.config.ts, app/layout.tsx, app/page.tsx, lib/utils.ts, styles/globals.css\\n"
                f"2. Create SEPARATE component files for every section:\\n"
                f"   - components/Hero.tsx\\n"
                f"   - components/About.tsx\\n"
                f"   - components/Projects.tsx\\n"
                f"   - components/Skills.tsx\\n"
                f"   - components/Contact.tsx\\n"
                f"   - components/Footer.tsx\\n"
                f"3. app/page.tsx MUST ONLY import and compose components (NO inline definitions)\\n"
                f"4. EVERY component used in app/page.tsx MUST have its own file created\\n"
                f"5. Use @/ path alias for all imports\\n\\n"
                f"User Request: {refinement_request}\\n\\n"
                f"Resume Data: {json.dumps(resume_data)[:2000]}\\n"
            )
        else:
            return (
                f"Request: {refinement_request}\\n"
                f"Resume: {json.dumps(resume_data)[:2000]}\\n"
                f"Current Files: {json.dumps(list(source_files.keys()))}\\n"
            )

    async def refine_portfolio(
        self,
        refinement_request: str,
        current_files: Dict[str, str],
        resume_data: Dict,
        mode: str = "code",
        auto_retry: bool = True
    ) -> Dict:
        """Synchronous-style refinement call (awaitable).

        Returns a structured dict with keys: success, files, refined_files,
        thought, thought_time, tools_used, edits_made, summary, error.
        """
        start_time = time.time()

        if not self.client:
            return {
                "success": False,
                "files": current_files,
                "refined_files": {},
                "thought": "",
                "thought_time": 0,
                "tools_used": [],
                "edits_made": [],
                "summary": "Groq client not configured (GROQ_API_KEY missing)",
                "error": "missing_groq_key",
            }

        tools_used = []

        try:
            # Simple analysis step
            t0 = time.time()
            source_files = {
                k: v for k, v in current_files.items()
                if k.endswith(('.tsx', '.ts', '.css', '.json', '.js'))
                and not k.startswith('package-lock')
            }
            
            # Detect if this is initial or incomplete generation
            is_initial_generation, missing_core_files = self._detect_initial_generation(current_files)
            
            logger.info(f"🔍 Generation type: {'INITIAL' if is_initial_generation else 'REFINEMENT'}")
            if is_initial_generation and missing_core_files:
                logger.info(f"📋 Missing core files: {', '.join(missing_core_files)}")
            
            tools_used.append({
                "name": "analyze_request",
                "duration": round(time.time() - t0, 2),
                "status": "success",
                "output_summary": f"Filtered to {len(source_files)} files. "
                                 f"{'Initial generation' if is_initial_generation else 'Refinement'}"
            })

            # Get mode-specific system prompt
            system_prompt = self._get_system_prompt(mode=mode)

            # Build user message based on generation type
            user_message = self._build_user_message(
                refinement_request,
                resume_data,
                source_files,
                is_initial_generation,
                missing_core_files
            )

            # Call Groq (with potential retry)
            max_attempts = 2 if auto_retry else 1
            attempt = 0
            validation_passed = False
            refined_files = {}
            thought = ""
            summary = ""
            validation_problems = []

            while attempt < max_attempts and not validation_passed:
                attempt += 1
                logger.info(f"🤖 LLM call attempt {attempt}/{max_attempts}")
                
                # Add validation failure context on retry
                if attempt > 1:
                    user_message += (
                        f"\\n\\n⚠️  VALIDATION FAILED ON PREVIOUS ATTEMPT:\\n"
                        f"Problems: {json.dumps(validation_problems)}\\n"
                        f"CRITICAL: Fix all validation errors. Ensure ALL imported components have files created.\\n"
                    )
                
                t1 = time.time()
                model_name = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
                
                completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    model=model_name,
                    temperature=0.2,
                    max_tokens=8000,  # Increased for complete projects
                    response_format={"type": "json_object"},
                )

                gen_time = round(time.time() - t1, 2)
                tools_used.append({
                    "name": f"generate_code_attempt_{attempt}",
                    "duration": gen_time,
                    "status": "success"
                })

                response_content = completion.choices[0].message.content
                result = self._extract_json(response_content)

                refined_files = result.get("files", {})
                thought = result.get("thought", "")
                summary = result.get("summary", "")

                # Validate generated files if this is initial generation
                if is_initial_generation:
                    # Merge with current files for validation
                    merged_for_validation = current_files.copy()
                    merged_for_validation.update(refined_files)
                    
                    validation_passed, validation_problems = self._validate_generated_files(merged_for_validation)
                    
                    if not validation_passed:
                        logger.warning(f"❌ Validation failed (attempt {attempt}):")
                        for problem in validation_problems:
                            logger.warning(f"   - {problem}")
                    else:
                        logger.info("✅ Validation passed!")
                else:
                    # Skip validation for refinements
                    validation_passed = True

            # If validation still failed after retries, return error
            if not validation_passed and is_initial_generation:
                logger.error("❌ Validation failed after all retry attempts")
                return {
                    "success": False,
                    "files": current_files,
                    "refined_files": refined_files,
                    "thought": f"Validation failed: {'; '.join(validation_problems)}",
                    "thought_time": round(time.time() - start_time, 1),
                    "tools_used": tools_used,
                    "edits_made": [],
                    "summary": "Portfolio generation failed validation checks",
                    "error": "validation_failed",
                    "validation_problems": validation_problems
                }

            # Compute edits
            edits_made = []
            for fn, new_content in refined_files.items():
                old_content = current_files.get(fn, "")
                old_lines = old_content.split("\\n") if old_content else []
                new_lines = new_content.split("\\n")

                edits_made.append({
                    "file": fn,
                    "lines_added": max(0, len(new_lines) - len(old_lines)),
                    "lines_removed": max(0, len(old_lines) - len(new_lines)),
                    "total_lines": len(new_lines),
                    "old_content": old_content,
                    "new_content": new_content
                })

            # Merge files
            merged = current_files.copy()
            merged.update(refined_files)

            total_time = round(time.time() - start_time, 1)

            logger.info(f"✅ Portfolio generation completed in {total_time}s")
            logger.info(f"📁 Generated {len(refined_files)} files ({len(merged)} total)")

            return {
                "success": True,
                "files": merged,
                "refined_files": refined_files,
                "thought": thought,
                "thought_time": total_time,
                "tools_used": tools_used,
                "edits_made": edits_made,
                "summary": summary,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error in refine_portfolio: {str(e)}", exc_info=True)
            total_time = round(time.time() - start_time, 1)
            return {
                "success": False,
                "files": current_files,
                "refined_files": {},
                "thought": f"Error: {str(e)}",
                "thought_time": total_time,
                "tools_used": tools_used,
                "edits_made": [],
                "summary": "",
                "error": str(e)
            }

    async def stream_refine_portfolio(
        self,
        refinement_request: str,
        current_files: Dict[str, str],
        resume_data: Dict,
        mode: str = "code"
    ):
        """Async generator yielding simple SSE-style events (dicts).

        Consumers iterate and format for SSE (e.g. `data: <json>\\n\\n`).
        """
        start_time = time.time()

        # Analysis
        yield {
            "type": "tool",
            "data": {
                "name": "analyze_request",
                "status": "running",
                "message": "Analyzing files..."
            }
        }

        files = {
            k: v for k, v in current_files.items()
            if k.endswith(('.tsx', '.ts', '.css', '.json', '.js'))
            and not k.startswith('package-lock')
        }

        yield {
            "type": "tool",
            "data": {
                "name": "analyze_request",
                "status": "success",
                "output_summary": f"Found {len(files)} files"
            }
        }

        if not self.client:
            yield {
                "type": "result",
                "data": {
                    "success": False,
                    "files": current_files,
                    "refined_files": {},
                    "thought": "Groq client not configured",
                    "error": "missing_groq_key"
                }
            }
            return

        try:
            # Get mode-specific prompt
            system_prompt = self._get_system_prompt(mode=mode)

            user_message = (
                f"Request: {refinement_request}\\n"
                f"Files: {json.dumps(list(files.keys()))}"
            )

            yield {
                "type": "tool",
                "data": {
                    "name": "generate_code",
                    "status": "running"
                }
            }

            model_name = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
            
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model=model_name,
                temperature=0.2,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            response_content = completion.choices[0].message.content

            yield {
                "type": "tool",
                "data": {
                    "name": "generate_code",
                    "status": "success"
                }
            }

            result = self._extract_json(response_content)

            refined_files = result.get("files", {})
            thought = result.get("thought", "")
            summary = result.get("summary", "")

            # Compute edits
            edits_made = []
            for fn, new_content in refined_files.items():
                old_content = current_files.get(fn, "")
                old_lines = old_content.split("\\n") if old_content else []
                new_lines = new_content.split("\\n")

                edits_made.append({
                    "file": fn,
                    "lines_added": max(0, len(new_lines) - len(old_lines)),
                    "lines_removed": max(0, len(old_lines) - len(new_lines)),
                    "total_lines": len(new_lines),
                    "old_content": old_content,
                    "new_content": new_content
                })

            merged = current_files.copy()
            merged.update(refined_files)

            yield {
                "type": "result",
                "data": {
                    "success": True,
                    "files": merged,
                    "refined_files": refined_files,
                    "thought": thought,
                    "edits_made": edits_made,
                    "summary": summary,
                    "error": None
                }
            }

        except Exception as e:
            logger.error(f"Error in stream_refine_portfolio: {str(e)}", exc_info=True)
            yield {
                "type": "result",
                "data": {
                    "success": False,
                    "files": current_files,
                    "refined_files": {},
                    "thought": f"Error: {str(e)}",
                    "edits_made": [],
                    "summary": "",
                    "error": str(e)
                }
            }
