import mlflow

def test_review_logs_to_mlflow():
    client = mlflow.MlflowClient()

    CI_EXPERIMENT_NAME = 'pr-reviews-prod'
    exp = client.get_experiment_by_name(CI_EXPERIMENT_NAME)
    assert exp is not None, f"Experiment '{CI_EXPERIMENT_NAME}' not found!"

    runs = client.search_runs(
        experiment_ids=[exp.experiment_id],
        max_results=1,
        order_by=["attributes.start_time DESC"]
    )

    assert len(runs) > 0, "Not found run experiment"
    latest = runs[0]

    assert 'model_name' in latest.data.params
    assert 'prompt_version' in latest.data.params
    assert 'truncated' in latest.data.params

    assert 'diff_size_chars' in latest.data.metrics
    assert 'token_count_input' in latest.data.metrics
    assert 'token_count_output' in latest.data.metrics
    assert 'latency_seconds' in latest.data.metrics
    assert 'token_per_second' in latest.data.metrics

    assert 'status' in latest.data.tags
    assert latest.data.tags['status'] == 'success'

