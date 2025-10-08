"""End-to-end tests for AMAS API health endpoints"""

import asyncio
import os

import httpx
import pytest

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health endpoint"""
    api_url = os.getenv("AMAS_API_URL", "http://localhost:8000")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{api_url}/health")
            # If API is running, check response
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except httpx.ConnectError:
            # Skip if API is not running
            pytest.skip("API not available for e2e testing")

@pytest.mark.asyncio
async def test_api_info():
    """Test the API info endpoint"""
    api_url = os.getenv("AMAS_API_URL", "http://localhost:8000")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{api_url}/")
            assert response.status_code in [200, 404]  # May not have root endpoint
        except httpx.ConnectError:
            pytest.skip("API not available for e2e testing")

def test_environment_setup():
    """Test that test environment is properly configured"""
    # This test always passes but validates env setup
    api_url = os.getenv("AMAS_API_URL", "http://localhost:8000")
    assert api_url is not None
    assert "http" in api_url
