import sys
from mlflow import MlflowClient


def main():
    """Promote an MLflow prompt version to the 'production' alias.

    Usage: uv run src/promote_prompt.py <version_number>
    """
    if len(sys.argv) < 2:
        print("Usage: promote_prompt.py <version_number>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]

    client = MlflowClient()
    client.set_prompt_alias(
        name='ai-review-prompt',
        alias='production',
        version=int(version)
    )
    print(f"Promoted version {version} to production")

if __name__ == '__main__':
    main()