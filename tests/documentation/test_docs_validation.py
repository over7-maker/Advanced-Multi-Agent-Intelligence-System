"""
Documentation validation tests.
"""
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import project_root
from tests.utils.validation_helpers import MarkdownValidator


@pytest.mark.documentation
class TestDocsValidation:
    """Test suite for documentation validation."""
    
    @pytest.fixture
    def doc_files(self, project_root: Path):
        """Get all documentation files."""
        docs_dir = project_root / "docs"
        if not docs_dir.exists():
            return []
        
        return list(docs_dir.glob("*.md"))
    
    def test_docs_exist(self, project_root: Path):
        """Test that required documentation exists."""
        docs_dir = project_root / "docs"
        
        required_docs = [
            "SECURITY.md",
            "PERFORMANCE.md",
            "SCALING.md",
            "PRODUCTION_CHECKLIST.md",
        ]
        
        for doc in required_docs:
            doc_path = docs_dir / doc
            assert doc_path.exists(), f"Required documentation {doc} not found"
    
    def test_markdown_syntax(self, doc_files):
        """Test markdown files have valid syntax."""
        for doc_file in doc_files:
            valid, error = MarkdownValidator.validate_syntax(doc_file)
            assert valid, f"{doc_file.name} has syntax errors: {error}"
    
    def test_code_blocks_balanced(self, doc_files):
        """Test that code blocks are balanced."""
        for doc_file in doc_files:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            code_block_count = content.count('```')
            assert code_block_count % 2 == 0, \
                f"{doc_file.name} has unbalanced code blocks"
    
    def test_required_sections(self, project_root: Path):
        """Test that documentation has required sections."""
        docs_dir = project_root / "docs"
        
        doc_sections = {
            "SECURITY.md": ["Authentication", "API Security", "Database Security"],
            "PERFORMANCE.md": ["Database Optimization", "API Performance"],
            "SCALING.md": ["Horizontal Scaling", "Vertical Scaling"],
            "PRODUCTION_CHECKLIST.md": ["Pre-Deployment", "Deployment Day"],
        }
        
        for doc_name, required_sections in doc_sections.items():
            doc_path = docs_dir / doc_name
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for section in required_sections:
                    assert section in content, \
                        f"{doc_name} missing required section: {section}"

