# N1MOX30 Launch Candidate

This package is the repaired launch candidate built from Final Test3.

## Repaired blockers
- Real ElevenLabs/OpenAI TTS adapters replace the demo-only voice boundary.
- OpenClaw workflow adapter now invokes the installed OpenClaw CLI provider.
- X OAuth requests `media.write` in addition to posting scopes.
- Local rendered media can automatically map to `/media/...` when `PUBLIC_MEDIA_BASE_URL` is configured.
- Publishing Center and Daily Workspace routes are registered.
- Backend smoke tests are included.

## External activation still required
Platform developer credentials, OAuth approvals/audits, HTTPS, public media domain, and app-store signing cannot be bundled into source code.

TikTok currently requires `video.publish` approval for Direct Post and verified URL ownership when using `PULL_FROM_URL`; unaudited clients are restricted to private visibility.
YouTube requires an audited API project for public uploads from affected unverified projects.


Test4 repair: duplicate App.jsx imports were removed and setup.ps1 now fails fast if npm install or the frontend production build fails.
