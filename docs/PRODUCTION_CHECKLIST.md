# Production Checklist

The application code is shipped with development/demo defaults. Before exposing it publicly:

1. Create a strong random `SECRET_KEY`.
2. Set `ENVIRONMENT=production`.
3. Use HTTPS and a production domain.
4. Move SQLite to PostgreSQL for multi-user production workloads.
5. Configure a persistent object store for generated media.
6. Add Google/YouTube OAuth credentials and verify redirect URIs.
7. Add the AI provider credentials you actually intend to use.
8. Configure real publishing adapters only for accounts you own/control.
9. Configure backups and restore drills.
10. Configure centralized logs, metrics and alerting.
11. Run the complete test suite in CI/CD.
12. Review OAuth scopes, CORS origins and secret storage.

No archive can safely contain private production credentials. Those are the only meaningful manual additions left for a real deployment.
