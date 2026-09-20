# N1MOX30 Production Security & Billing

## Security baseline
- Server-side validation for every request.
- Argon2/bcrypt password hashing.
- Generic login/reset errors to prevent account enumeration.
- Rate limiting and brute-force protection.
- Secure cookies/tokens in production.
- Strict CORS with the deployed frontend origin.
- CSRF protection where cookie-authenticated state-changing requests are used.
- OAuth state validation and server-side token handling.
- Webhook signature verification before changing billing state.
- Never trust client-supplied plan price, payment status or entitlement.
- Secrets only in environment/secret management, never in source.
- Audit security-sensitive actions.
- PostgreSQL + Redis before horizontal scaling.
- Backups and tested recovery.
- HTTPS/HSTS at the edge.
- Dependency and container security scanning.

## Billing
Plans:
- Creator: $19/month
- Pro: $49/month
- Studio: $129/month

USD is the reference currency. Local currency and payment methods depend on the selected payment provider, country and legal/tax configuration.

Live checkout is intentionally not enabled by this foundation until a payment provider account, business identity, webhook signing secret, refund policy and country availability are configured and verified.

## Compliance
Do not claim universal legal compliance. Configure privacy, tax, consumer, payments, KYC/KYB, AML/fraud and data-transfer requirements for the actual operating entity and countries served.