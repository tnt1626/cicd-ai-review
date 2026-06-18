import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from src.helper import mlflow_reviews_stats


def create_mock_run(latency, tokens, model_name, end_time):
    run = MagicMock()
    run.data.metrics = {
        'latency_seconds': latency,
        'token_count_output': tokens
    }
    run.data.params = {'model_name': model_name}
    run.info.end_time = end_time
    return run


@pytest.mark.asyncio
@patch('mlflow.MlflowClient')
async def test_get_reviews_stats_normal_response(mock_client_cls):
    mock_client = mock_client_cls.return_value

    mock_exp = MagicMock()
    mock_exp.experiment_id = "5"
    mock_client.get_experiment_by_name.return_value = mock_exp

    run1 = create_mock_run(5.2, 100, 'qwen3', 1781625280000)
    run2 = create_mock_run(7.3, 500, 'mistral', 1781625284000)


    mock_client.search_runs.return_value = [run1, run2]

    response = await mlflow_reviews_stats()

    assert response['total_reviews'] == 2
    assert response['avg_latency_seconds'] == 6.25      
    assert response['avg_token_count_output'] == 300.0 
    assert response['most_used_model'] == 'mistral'

    expected_time = datetime.fromtimestamp(1781625284000 / 1000.0).strftime("%d/%m/%Y %H:%M:%S")
    assert response['last_review_at'] == expected_time


@pytest.mark.asyncio
@patch('mlflow.MlflowClient')
async def test_get_reviews_stats_empty_run(mock_client_cls):
    mock_client = mock_client_cls.return_value

    mock_exp = MagicMock()
    mock_exp.experiment_id = "5"

    mock_client.get_experiment_by_name.return_value = mock_exp

    mock_client.search_runs.return_value = []

    response = await mlflow_reviews_stats()

    assert response['total_reviews'] == 0
    assert response['avg_latency_seconds'] == 0.0     
    assert response['avg_token_count_output'] == 0.0 
    assert response['most_used_model'] == 'N/A'


@pytest.mark.asyncio
@patch('mlflow.MlflowClient')
async def test_get_reviews_stats_empty_experiment(mock_client_cls):
    mock_client = mock_client_cls.return_value

    mock_client.get_experiment_by_name.return_value = None

    response = await mlflow_reviews_stats()

    assert response['total_reviews'] == 0
    assert response['avg_latency_seconds'] == 0.0     
    assert response['avg_token_count_output'] == 0.0 
    assert response['most_used_model'] == 'N/A'