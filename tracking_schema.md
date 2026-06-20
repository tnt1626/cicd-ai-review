# MLflow Tracking Schema: Code Review Model

This documentation defines the schema for values that need to log (tracking) 
through MFflow when running script `review.py`

## 1. Parameters (Configuration Variables)
*These are the input values or static configurations for each Run. Use `mlflow.log_param()` or `mlflow.log_params()` to log these values.*

| Parameter Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `model_name` | String | The name or version of the LLM used for the code review. | `"gpt-4-turbo"`, `"claude-3-opus"` |
| `prompt_version` | String | The version identifier of the system prompt or template used. | `1`, `3` |
| `truncated` | Boolean | A flag indicating whether the diff content was truncated due to exceeding the context window limit. | `True`, `False` |


## 2. Metrics (Performance & Results)
*These are numerical output values that may vary or can be measured after the model returns its response. Use `mlflow.log_metric()` or `mlflow.log_metrics()` to log these values.*

| Metric Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `diff_size_chars` | Integer | The total number of characters in the code diff passed into the prompt. | `1540`, `523` |
| `token_count_input` | Integer | The number of tokens consumed for the input (prompt + diff). | `450`, `890` |
| `token_count_output` | Integer | The number of tokens generated in the review output. | `210`, `35` |
| `latency_seconds` | Float | The API response time (in seconds) from sending the request to fully receiving the response. | `2.45`, `15.3` |
| `token_per_second` | Float | The number of token that AI generate per second | `22.2`, `15.3` |


## 3. Text
| Text Name       | Data Type | Description           | Example |
|:----------------|:----------|:----------------------|:--------|
| `system_prompt` | String    | System prompt.        |         |
| `diff`          | String    | The code that change. |         |
| `review_text`   | String    | Output of AI model    |         |


## 4. Tag
| Tag Name | Data Type | Description                  |
|:---------|:----------|:-----------------------------|
| `status` | String    | The status of the experiment |
| `error`  | String    | The detail of the experiment |
