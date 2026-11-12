# Northgate eKYC & Document Chaser

An institutional corporate KYC onboarding, verification, and 3-day SLA document-chaser platform.

## Architecture

- **KYC API & Web UI (`backend/app`)**: Python / FastAPI service providing customer onboarding, authentication, document upload/review, risk scoring, analyst decisions, audit logs, and the served web dashboard (`/` and `/ui`).
- **Document Chaser API (`backend/chaser-ts`)**: TypeScript / Express service managing client document gap tracking, AI-assisted chaser drafts, manual send confirmations, and SLA turnaround monitoring.
- **Database & Storage**: PostgreSQL (local Docker PostgreSQL in development; Cloud SQL via Cloud SQL Auth Proxy + private Google Cloud Storage bucket in staging/production).
- **Reverse Proxy**: Caddy (`backend/Caddyfile`) serving TLS/HTTPS for the dashboard (`/`) and routing `/chaser-api/*` to the TypeScript API.
- **UI Design Prototypes (`extracted/stitch_kyc_document_chaser`)**: Product requirements and screen mockups for the compliance workspace, chase queue, AI drafter, client upload portal, and SLA analytics.

## Quick Local Start (Docker)

```bash
cd backend
docker compose up --build
```

- Dashboard UI: `http://127.0.0.1:8000/`
- KYC Swagger API Docs: `http://127.0.0.1:8000/docs`
- Document Chaser Health: `http://127.0.0.1:8001/health`

Register an initial local operator account via `POST /api/v1/auth/register` or the UI sign-up flow.

## GitHub Branches & GCP Environments

The CI/CD pipeline in `.github/workflows/deploy.yml` supports both **Staging** and **Production** deployments to Google Cloud Platform:

| Branch | GitHub Environment | Container Tags | Behavior |
|---|---|---|---|
| `staging` | `staging` | `:staging`, `:staging-<sha>` | Runs Python, TypeScript, and Docker Compose integration tests, publishes staging images to GHCR, and deploys to your GCP staging VM. Optional environment variables `ALLOW_PUBLIC_REGISTRATION` and `SEED_DEMO_DATA` can be set to `"true"` in the `staging` environment for demo showcasing. |
| `main` | `production` | `:latest`, `:<sha>` | Runs full CI checks, publishes production images to GHCR, and deploys to your GCP production VM with public registration and demo seeding disabled. |

See [backend/README.md](backend/README.md) for the complete GCP resource checklist (Compute Engine VM, private-IP Cloud SQL, GCS bucket, DNS, and GitHub Environment secrets).
