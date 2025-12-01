"""Unit tests for portfolio generation validation."""

import pytest
import re
from services.lovable_style_generator import PortfolioGenerator


class TestPortfolioGeneration:
    """Test suite for portfolio generation completeness and validation."""

    @pytest.mark.asyncio
    async def test_initial_generation_creates_all_required_files(self):
        """Test that initial generation creates complete project structure with all required files."""
        generator = PortfolioGenerator()
        
        # Skip test if GROQ API key not configured
        if not generator.client:
            pytest.skip("GROQ_API_KEY not configured")
        
        result = await generator.refine_portfolio(
            refinement_request="Create a modern portfolio with dark theme and vibrant colors",
            current_files={},  # Empty - initial generation
            resume_data={
                "name": "Test User",
                "email": "test@example.com",
                "title": "Software Engineer",
                "skills": ["Python", "React", "TypeScript"]
            },
            mode="code"
        )
        
        assert result["success"] is True, f"Generation failed: {result.get('error')}"
        
        files = result.get("files", {})
        assert len(files) > 0, "No files were generated"
        
        # Check required core files exist
        required_files = [
            "package.json",
            "app/layout.tsx",
            "app/page.tsx",
            "tsconfig.json",
            "tailwind.config.ts",
        ]
        
        for required_file in required_files:
            assert required_file in files, f"Missing required file: {required_file}"
        
        print(f"✅ Generated {len(files)} files")
        print(f"📁 Files: {list(files.keys())}")

    @pytest.mark.asyncio
    async def test_component_imports_have_corresponding_files(self):
        """Test that all components imported in app/page.tsx have corresponding component files."""
        generator = PortfolioGenerator()
        
        if not generator.client:
            pytest.skip("GROQ_API_KEY not configured")
        
        result = await generator.refine_portfolio(
            refinement_request="Create a portfolio with Hero, About, Projects, and Contact sections",
            current_files={},
            resume_data={"name": "Test User", "email": "test@example.com"},
            mode="code"
        )
        
        assert result["success"] is True, f"Generation failed: {result.get('error')}"
        
        files = result.get("files", {})
        page_content = files.get("app/page.tsx", "")
        
        assert page_content, "app/page.tsx was not generated"
        
        # Find all component imports
        import_pattern = r"from\\s+['\"]@/components/([\\w/]+)['\"]"
        component_imports = re.findall(import_pattern, page_content)
        
        print(f"🔍 Found {len(component_imports)} component imports: {component_imports}")
        
        # Check each imported component has a corresponding file
        for comp_name in component_imports:
            comp_file = f"components/{comp_name}.tsx"
            assert comp_file in files, (
                f"Component '{comp_name}' is imported in app/page.tsx "
                f"but {comp_file} was not created. Available files: {list(files.keys())}"
            )
            print(f"✅ {comp_file} exists")

    @pytest.mark.asyncio
    async def test_validation_detects_missing_files(self):
        """Test that validation correctly detects missing required files."""
        generator = PortfolioGenerator()
        
        # Test detection logic
        is_initial, missing = generator._detect_initial_generation({})
        assert is_initial is True, "Should detect empty dict as initial generation"
        assert len(missing) > 0, "Should report missing core files"
        
        # Test incomplete generation
        incomplete_files = {
            "app/page.tsx": "export default function Home() { return <div>Test</div> }"
        }
        is_initial, missing = generator._detect_initial_generation(incomplete_files)
        assert is_initial is True, "Should detect incomplete files as initial generation"
        assert "package.json" in missing, "Should detect missing package.json"
        assert "tsconfig.json" in missing, "Should detect missing tsconfig.json"
        
        print(f"✅ Detected missing files: {missing}")

    @pytest.mark.asyncio
    async def test_validation_detects_missing_component_files(self):
        """Test that validation detects when imported components don't have files."""
        generator = PortfolioGenerator()
        
        # Create files with missing component
        test_files = {
            "package.json": "{}",
            "app/layout.tsx": "export default function Layout() {}",
            "app/page.tsx": "import Hero from '@/components/Hero'\\nimport Missing from '@/components/Missing'\\nexport default function Home() { return <><Hero /><Missing /></> }",
            "tsconfig.json": "{}",
            "tailwind.config.ts": "export default {}",
            "components/Hero.tsx": "export default function Hero() { return <div>Hero</div> }",
            # Missing: components/Missing.tsx
        }
        
        is_valid, problems = generator._validate_generated_files(test_files)
        
        assert is_valid is False, "Validation should fail for missing component files"
        assert any("Missing" in problem for problem in problems), (
            f"Should detect missing component file. Problems: {problems}"
        )
        
        print(f"✅ Detected validation problems: {problems}")

    def test_file_limit_enforcement(self):
        """Test that file limit is enforced."""
        generator = PortfolioGenerator()
        
        # Create too many files
        too_many_files = {f"file{i}.tsx": "" for i in range(65)}
        too_many_files.update({
            "package.json": "{}",
            "app/layout.tsx": "",
            "app/page.tsx": "",
            "tsconfig.json": "{}",
            "tailwind.config.ts": "{}",
        })
        
        is_valid, problems = generator._validate_generated_files(too_many_files)
        
        assert is_valid is False, "Should reject files exceeding limit"
        assert any("Too many files" in problem for problem in problems), (
            f"Should detect file limit exceeded. Problems: {problems}"
        )
        
        print(f"✅ File limit enforcement working: {problems}")


if __name__ == "__main__":
    # Run tests with: pytest backend/tests/test_portfolio_generation.py -v -s
    pytest.main([__file__, "-v", "-s"])
