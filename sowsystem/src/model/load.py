from strands.models import BedrockModel

# Use Claude 3.5 Sonnet which supports on-demand throughput
# Or use an inference profile ARN if you have one configured
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

def load_model() -> BedrockModel:
    """
    Get Bedrock model client.
    Uses IAM authentication via the execution role.
    
    Note: If you get an on-demand throughput error, you need to either:
    1. Use a model that supports on-demand in your region
    2. Use an inference profile ARN instead
    3. Set up provisioned throughput for the model
    """
    return BedrockModel(model_id=MODEL_ID)