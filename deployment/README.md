# N1MOX30 Deployment

N1MOX30 is shipped with a production-oriented container configuration.

Required production services:
- HTTPS reverse proxy
- FastAPI backend
- React/Vite static frontend
- PostgreSQL or another managed SQL database for multi-instance production
- S3-compatible media storage for generated video/thumbnail assets
- Secret manager/environment variables
- Monitoring and backups

The included Docker Compose file is a baseline. Replace development secrets and bind mounts with managed infrastructure before public launch.
