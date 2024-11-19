

"Run the below in Mac terminal"

# sudo rm /usr/local/bin/aws
# curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
# sudo installer -pkg AWSCLIV2.pkg -target /
# AWS configure
# AWS Access Key ID
# AWS Secret Access Key
# Region (e.g., us-east-1 where Bedrock is available)

# Configure: 
      # export AWS_ACCESS_KEY_ID=your-access-key-id
      # export AWS_SECRET_ACCESS_KEY=your-secret-access-key
      # export AWS_REGION=us-east-1


"Orginal code"

import boto3, requests

# Initialize Bedrock client
client = boto3.client("bedrock", region_name="us-east-1")

# Specify the model and input prompt
model_id = "anthropic.claude-v2"  # Replace with your chosen model
response = client.invoke_model(
    modelId=model_id,
    body={
        "inputText": "Write a poem about technology and nature."
    },
    contentType="application/json"
)

# Parse and display the result
result = response["body"].read().decode("utf-8")
print("Model Response:", result)

