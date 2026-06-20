import sys
from mlflow import MlflowClient

version = sys.argv[1] if len(sys.argv) > 1 else "1"

client = MlflowClient()
client.set_prompt_alias(
    name='ai-review-prompt',
    alias='production',
    version=int(version)
)
print(f"Promoted version {version} to production")