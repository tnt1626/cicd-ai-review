import mlflow

mlflow.set_experiment("test_experiment_1")

with mlflow.start_run():
    mlflow.log_param('model', 'llama-3.3-70b-versatile')
    mlflow.log_param('latency', 1.06)