

```bash
zip -r ../agent.zip . -x ".env/*"
```

```bash
aws s3 cp agent.zip s3://agent-stack-codebuild-agent-source-407296935140/agent.zip --metadata "version=1.0"
```