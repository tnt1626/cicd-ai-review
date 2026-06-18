import pytest
from unittest.mock import patch, AsyncMock
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
        assert data["message"] == "Test Workflow"
        assert data["day"] == day

@pytest.mark.asyncio
@patch('src.main.mlflow_reviews_stats', new_callable=AsyncMock)
async def test_get_get_reviews_stats(mock_stats_func):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
    
        mock_stats_func.return_value = {
            'total_reviews': 5,
            'avg_latency_seconds': 1.2,
            'avg_token_count_output': 120.0,
            'most_used_model': 'llama-3',
            'last_review_at': '18/06/2026 14:54:43'
        }

        response = await client.get('/reviews/stats')
        
        assert response.status_code == 200

        json_data = response.json()
        assert json_data['total_reviews'] == 5
        assert json_data['most_used_model'] == 'llama-3'