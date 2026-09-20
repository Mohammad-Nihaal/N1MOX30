# N1MOX30 — Creator Operating System — Final Test3

N1MOX30 is the unified creator workspace for research, strategy, AI production, automation, analytics and multi-platform publishing.

## Included in this package

### Platforms
- YouTube — OAuth, channel data, analytics, resumable video upload, scheduling and thumbnails.
- Instagram — Meta OAuth and professional-account media publishing (Reels, Feed image, Stories path).
- TikTok — OAuth, creator info, Direct Post video flow and analytics.
- X — OAuth 2, post publishing, thread publishing and optional pre-uploaded media IDs.
- Unified multi-platform Publishing Center.

### AI creator stack
Research, trends, hooks, scripts, captions, hashtags, metadata, thumbnail generation, subtitles, voice, visuals, rendering, quality review and creator recommendations.

### Creator intelligence
Profile, preferences, long-term memory, personalization, growth score, growth recommendations and analytics-driven insights.

### Voice
Wake word, speech-to-text interface, voice understanding, natural responses, voice actions and workflow control.

### Workflow
Projects, automation, central orchestration, approvals, completion confirmation, versioning, retries, recovery and activity logs.

### Idea → publish
Idea → research → strategy → hooks → script → voice → visuals → timeline → captions → thumbnail → quality control → scheduling → publishing.

### Workspace
Content calendar/scheduling, drafts, publishing queue, notifications, daily command center, weekly goals and momentum/streak tracking.

### Clients
- React + Vite web application
- PWA manifest
- Expo/React Native Android + iOS + web foundation

### Operations
- SQLite local persistence with migration utilities
- FastAPI backend
- JWT authentication
- provider abstraction
- structured logging
- backup script
- Docker production baseline
- PowerShell setup/start helpers

## Start on Windows

From the extracted folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\start_n1mox30.ps1
```

Web:
- http://127.0.0.1:5173
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

The setup script creates the Python environment, installs backend dependencies, creates `.env` from `.env.example`, initializes the database and installs/builds the frontend.

## Mobile

```powershell
cd mobile
npm install
npx expo start
```

The mobile client uses the same backend architecture. Store submission still requires the owner's Android/iOS signing and store accounts.

## AI provider failover

N1MOX30 supports automatic two-way provider failover:

- `AI_PROVIDER=auto`
- `AI_PRIMARY_PROVIDER=openclaw`
- `AI_FALLBACK_PROVIDER=bedrock`

Each request tries the primary provider first. If it fails because the provider is unavailable, exhausted, times out, or returns an error, N1MOX30 automatically tries the fallback provider. You can reverse the order by setting Bedrock as primary and OpenClaw as fallback.

This does not read a proprietary OpenClaw credit balance in advance; it detects an unsuccessful OpenClaw inference and fails over. Likewise, Bedrock API failures/limit errors trigger the OpenClaw fallback.

### AWS Bedrock credentials

AWS credentials are **not included** in this ZIP. Do not paste secret keys into chat or commit them to Git.

Use one of boto3's normal credential mechanisms:
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (+ optional `AWS_SESSION_TOKEN`) in `backend/.env`
- an AWS CLI profile via `AWS_PROFILE`
- an IAM role when deployed on AWS

Set `AWS_REGION`, `BEDROCK_MODEL_ID`, and `BEDROCK_ENABLED=true`.

## External platform activation

The source code is packaged and does not require code changes to activate external providers. However, third-party platform credentials and approvals cannot legally or technically be embedded in a ZIP. The deployment owner must supply:
- Google/YouTube OAuth credentials
- Meta/Instagram app credentials and eligible professional account
- TikTok app credentials and required Content Posting API permissions/audit
- X developer credentials and requested OAuth scopes
- HTTPS/public media hosting for production URL-based media delivery
- production secrets, domain and infrastructure configuration

Until those are supplied, N1MOX30 still runs locally with its provider-neutral/demo-capable architecture.

## Launch standard

This archive is a **source launch package**: the application code, workflows, adapters, web client, mobile client, setup scripts and deployment baseline are included. Production launch additionally depends on the external accounts, credentials, domains, app approvals, infrastructure and store signing controlled by the owner.

## Demo account

The existing seed script can create:
- Email: `demo@n1mox30.local`
- Password: `N1MOX30-Demo-2026!`

Change the password before any non-local use.
