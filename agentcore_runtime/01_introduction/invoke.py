import boto3
import json

client = boto3.client("bedrock-agentcore", region_name="us-west-2")

payload = json.dumps({"input": {"prompt": "What is 2 + 1?"}})

response = client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-west-2:407296935140:runtime/mainhh-Dg1PmQDS33",
    runtimeSessionId="dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshmt",  # Must be 33+ chars
    payload=payload,
    qualifier="DEFAULT",  # Optional
)
response_body = response["response"].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)
