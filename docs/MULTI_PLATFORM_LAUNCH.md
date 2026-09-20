# N1MOX30 Multi-Platform Launch

## Supported platform adapters
- YouTube: OAuth + upload/publish provider.
- Instagram: Meta OAuth + professional-account media container/publish flow.
- TikTok: OAuth + Content Posting API Direct Post flow.
- X: OAuth 2 + post creation, with optional pre-uploaded media IDs.

## Required external configuration
The source package cannot contain third-party client secrets, user OAuth tokens, verified domains, app approvals, or Apple/Google signing credentials. These are bound to the owner accounts and must be configured in the deployment environment.

## Media delivery
Instagram and TikTok URL-based video publishing require a publicly reachable media URL. TikTok's current Direct Post documentation also requires a verified URL prefix/domain for `PULL_FROM_URL` and approved `video.publish` access.

## Mobile
The `mobile/` Expo project provides Android/iOS/web client foundations using the same backend API. Store release still requires the developer's package identifiers, signing keys, privacy/legal metadata, and store accounts.
