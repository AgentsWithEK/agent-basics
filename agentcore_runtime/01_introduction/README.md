# Amazon Bedrock AgentCore Runtime - Managed Deployment

A simple agent with calculator and weather tools demonstrating Amazon Bedrock AgentCore Runtime managed deployment.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- AWS Account with Amazon Bedrock AgentCore access

## Local Development

### 1. Setup Environment

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 2. Run Server Locally

```bash
# Start FastAPI server
uv run main.py

# Server runs at http://localhost:8080
```

### 3. Test Locally

```bash
# Health check
curl http://localhost:8080/ping

# Invoke agent
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "What is 5 + 8?"}}'
```

## AWS Deployment

This creates a deployment package compatible with AWS Bedrock AgentCore Runtime (Linux ARM64).

### Step 1: Create Deployment Paackage

```bash
# Install dependencies for Linux ARM64
mkdir -p .package
uv pip install \
  --target .package \
  --python-version 3.12 \
  --python-platform aarch64-manylinux2014 \
  --only-binary :all: \
  -r requirements.txt

# Copy source code to package directory
cp *.py .package/
cp -r tools .package/

# Create deployment package
cd .package && zip -r ../deployment.zip . && cd ..
```

### Step 2: Deploy AgentCore Runtime using console

Follow console [instructions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy.html#:~:text=Custom%20zip%20%2B%20boto3-,console,-You%20can%20deploy).

### Step 3: Cleanup

```bash
rm -rf .package deployment.zip
```
