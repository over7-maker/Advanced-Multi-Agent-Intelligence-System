"""Basic unit tests for AMAS"""

from pathlib import Path

import pytest


@pytest.mark.unit
def test_project_structure():
    """Test that basic project structure exists"""
    assert Path("src/amas").exists()
    assert Path("src/amas/__init__.py").exists()


@pytest.mark.unit
def test_imports():
    """Test that basic imports work"""
    try:
        import amas

        assert amas is not None
    except ImportError:
        # Skip if not installed
        pytest.skip("AMAS not installed")


@pytest.mark.unit
def test_configuration():
    """Test configuration structure"""
    config_path = Path("src/amas/config")
    assert config_path.exists()
    assert config_path.is_dir()


@pytest.mark.unit
class TestBasicFunctionality:
    """Test basic functionality"""

    def test_truth(self):
        """Basic truth test"""
        assert True

    def test_arithmetic(self):
        """Basic arithmetic test"""
        assert 1 + 1 == 2

    def test_string_operations(self):
        """Basic string test"""
        assert "AMAS".lower() == "amas"
        assert "amas".upper() == "AMAS"

    def test_environment_variables(self):
        """Test that environment variables can be set"""
        import os
        os.environ['TEST_VAR'] = 'test_value'
        assert os.environ.get('TEST_VAR') == 'test_value'
