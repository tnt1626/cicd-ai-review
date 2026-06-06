import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.mark.asyncio
async def test_health_check_response():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(f"/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == "healthy"

@pytest.mark.asyncio
async def test_read_message_response():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        day = 1
        response = await client.get(f"/message/{day}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Test Work flow"
        assert data["day"] == day
