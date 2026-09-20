# N1MOX30 AI Provider Failover

N1MOX30 uses a provider-neutral AI router so the creator workflow does not have to change when one AI backend is unavailable.

## Default route

```text
OpenClaw / OmniRoute
        |
        | request fails / unavailable / quota exhausted
        v
Amazon Bedrock
        |
        | request fails
        v
deterministic local fallback (when enabled)
```

The route is controlled by:

```env
AI_PROVIDER=auto
AI_PRIMARY_PROVIDER=openclaw
AI_FALLBACK_PROVIDER=bedrock
AI_ENABLE_DEMO_FALLBACK=true
```

To reverse the order:

```env
AI_PRIMARY_PROVIDER=bedrock
AI_FALLBACK_PROVIDER=openclaw
```

### What "credits stopped" means

N1MOX30 does not rely on a private OpenClaw balance endpoint. It detects an unsuccessful OpenClaw inference (including CLI failure, timeout, unavailable provider/model, or an error returned by the OpenClaw/OmniRoute stack) and immediately tries the fallback provider.

The same behavior works in reverse: if Bedrock returns an error such as throttling, access denial, quota/limit exhaustion, or another inference failure, the router tries OpenClaw.

This is per-request failover. It does not silently transfer an existing request halfway through a model response.

## AWS Bedrock setup

The ZIP intentionally contains **no real AWS credentials**.

Use one of the supported AWS credential mechanisms:

1. Environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN` (only for temporary credentials)

2. AWS CLI/profile:
   - `AWS_PROFILE=your-profile`

3. Bedrock API key:
   - `AWS_BEARER_TOKEN_BEDROCK=...`

4. IAM role when deployed on AWS.

For production, AWS recommends IAM roles or temporary credentials rather than long-lived keys.

Set:

```env
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
BEDROCK_ENABLED=true
```

The selected Bedrock model must be available to the AWS account/region and support the Converse API. Amazon Nova Lite supports Converse.

**Never paste secret credentials into chat, source code, or Git. Put them in `backend/.env` or use the AWS credential chain.**
