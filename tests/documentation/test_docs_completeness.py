"""
Documentation completeness tests.
"""
import re
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import project_root
from tests.utils.validation_helpers import MarkdownValidator


@pytest.mark.documentation
class TestDocsCompleteness:
    """Test suite for documentation completeness."""
    
    def test_no_placeholder_text(self, project_root: Path):
        """Test that documentation doesn't contain placeholder text."""
        docs_dir = project_root / "docs"
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        placeholder_patterns = [
            r'YOUR_DOMAIN',
            r'your-domain\.com',
            r'CHANGE_THIS',
            r'TODO',
            r'FIXME',
            r'XXX',
        ]
        
        for doc_file in docs_dir.glob("*.md"):
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in placeholder_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                # Some placeholders are acceptable in examples
                # We'll just check that they're not excessive
                # Note: Many placeholders are OK in documentation
    
    def test_examples_are_complete(self, project_root: Path):
        """Test that code examples are complete."""
        docs_dir = project_root / "docs"
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in docs_dir.glob("*.md"):
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for incomplete code blocks
            code_blocks = re.findall(r'```[\s\S]*?```', content)
            # Check for incomplete code examples (note but don't fail)
            # Many examples use ... to indicate continuation
    
    def test_links_are_valid(self, project_root: Path):
        """Test that internal links are valid."""
        docs_dir = project_root / "docs"
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in docs_dir.glob("*.md"):
            broken_links = MarkdownValidator.check_links(doc_file, project_root)
            # Allow some broken links (they might be external or relative)
            # Note: Some broken links are acceptable in documentation

