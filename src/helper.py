import mlflow
import asyncio
import pandas as pd
from datetime import datetime

EMPTY_STATS = {
    'total_reviews': 0,
    'avg_latency_seconds': 0.0,
    'avg_token_count_output': 0.0,
    'most_used_model': 'N/A',
    'last_review_at': 'N/A'
}

async def mlflow_reviews_stats():
    client = mlflow.MlflowClient()
    experiment = await asyncio.to_thread(client.get_experiment_by_name, 'pr-reviews-prod')
    if not experiment:
        return EMPTY_STATS

    experiment_id = experiment.experiment_id
    runs = await asyncio.to_thread(client.search_runs, experiment_ids=[experiment_id])
    if not runs:
        return EMPTY_STATS
    
    data = []
    for run in runs:
        metrics = run.data.metrics
        params = run.data.params

        latency_seconds = metrics.get('latency_seconds', 0.0)
        token_count_output = metrics.get('token_count_output', 0)
        model = params.get('model_name', 'unknown')
        run_at = run.info.end_time

        data.append({
            'latency_seconds': latency_seconds,
            'token_count_output': token_count_output,
            'model': model,
            'run_at': run_at
        })

    df = pd.DataFrame(data)

    if df.empty or df['run_at'].isnull().all():
        return EMPTY_STATS

    modes = df['model'].mode()
    most_used_model = modes[0] if not modes.empty else 'unknown'

    response = {
        'total_reviews': int(df.shape[0]),
        'avg_latency_seconds': float(df['latency_seconds'].mean() or 0.0),
        'avg_token_count_output': float(df['token_count_output'].mean() or 0.0),
        'most_used_model': most_used_model,
        'last_review_at': datetime.fromtimestamp(df['run_at'].max() / 1000.0).strftime("%d/%m/%Y %H:%M:%S")
    }

    return response