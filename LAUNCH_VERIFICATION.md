# N1MOX30 Launch Verification — Test4

## Code-level status
- [x] Backend compiles
- [x] Smoke tests run
- [x] Voice provider boundary replaced with real TTS adapters
- [x] OpenClaw adapter connected to the OpenClaw provider
- [x] X media upload implemented for video
- [x] X OAuth requests media.write
- [x] Automatic public media URL mapping
- [x] Static media serving
- [x] Publishing and Daily routes registered

## Before public production
These are external prerequisites, not source-code TODOs:
1. Configure production secrets in the deployment environment.
2. Register OAuth redirect URLs with each platform.
3. Configure HTTPS and a public media domain.
4. Complete platform approvals/audits where required.
5. Re-authorize X accounts after adding media.write.
6. Use PostgreSQL/object storage/monitoring for multi-user production.
7. Sign Android/iOS releases and configure store accounts.

## Current platform notes
TikTok Direct Post requires the video.publish scope and verified URL ownership when using PULL_FROM_URL; unaudited clients are restricted to private visibility.
YouTube videos.insert can upload videos, but affected unverified API projects are restricted to private viewing until audit requirements are satisfied.
