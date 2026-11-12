# Northgate eKYC and Document Chaser

The application has a Python/FastAPI KYC API and UI, a TypeScript document-chaser API, and PostgreSQL. The cloud deployment target in this guide is a Google Cloud Compute Engine VM, Cloud SQL for PostgreSQL, and a private Cloud Storage bucket. GitHub Actions builds and publishes Docker images to GHCR, then deploys them to the VM over SSH.

The GitHub workflow does **not** create Google Cloud resources. A cloud administrator must provision the resources and secrets below first. Do not load real customer data until the required security, privacy, and compliance reviews are complete.

## Local development with Docker

1. Install Docker Desktop and start it.
2. From this `backend` directory, run `docker compose up --build`.
3. Open the dashboard directly at `http://127.0.0.1:8000/` (or `/ui`), KYC API docs at `http://127.0.0.1:8000/docs`, and the TypeScript API health check at `http://127.0.0.1:8001/health`.
4. Register a local Reviewer, Analyst, or Admin account at `POST /api/v1/auth/register`, then sign in through the UI.

This local-only Compose file starts PostgreSQL and seeds illustrative chaser cases. It is not the production Compose file.

## Google Cloud resources to provision

Ask your Google Cloud team to create:

1. A production project with Compute Engine, Cloud SQL, and Cloud Storage APIs enabled.
2. A Linux Compute Engine VM (Ubuntu 24.04, initially at least 2 vCPU and 8 GB RAM) with Docker Engine and the Docker Compose plugin installed. Assign a dedicated VM service account; grant it **Cloud SQL Client** and **Storage Object Creator** for the chaser database and document bucket. Do not install a service-account JSON key on the VM.
3. A Cloud SQL for PostgreSQL instance on a **private IP** in the VM's VPC, a production database, and a database user for the app. Keep SQL off the public internet. The Cloud SQL Auth Proxy runs as a container in the production Compose stack.
4. A private Cloud Storage bucket in an approved region. Enable uniform bucket-level access and public access prevention; set retention, versioning, and encryption according to your compliance requirements.
5. A DNS A record pointing your app hostname to the VM's external IP. Allow inbound TCP 80/443 for Caddy HTTPS certificate issuance and web traffic. Restrict SSH to an approved deployment runner/network; do not expose PostgreSQL.
6. A verified SSH host-key fingerprint for the VM, a deployment SSH account with Docker access, and a GHCR pull token with read-only package access.

The current KYC upload service uses Cloud Storage when `GCS_BUCKET_NAME` is configured. In production the API refuses to start without this setting. Uploaded objects are private by default; configure bucket IAM and retention before accepting documents.

## Configure GitHub Actions

Push this project to GitHub. Create a GitHub **production environment** and, preferably, enable required reviewer approval. Configure the following environment secrets there:

| Secret | Value |
|---|---|
| `CLOUD_VM_HOST` | VM public IP or DNS name |
| `CLOUD_VM_USER` | SSH deployment username |
| `CLOUD_VM_SSH_PRIVATE_KEY` | Private SSH key for that deployment user |
| `CLOUD_VM_KNOWN_HOSTS` | Verified `known_hosts` entry for the VM |
| `APP_DOMAIN` | Public application hostname, without `https://` |
| `CLOUD_SQL_INSTANCE` | Cloud SQL connection name: `project:region:instance` |
| `KYC_DATABASE_URL` | SQLAlchemy URL using host `cloud-sql-proxy`, e.g. `postgresql+psycopg://user:URL_ENCODED_PASSWORD@cloud-sql-proxy:5432/northgate_ekyc?sslmode=disable` |
| `CHASER_DATABASE_URL` | Node `pg` URL using the same private proxy, e.g. `postgres://user:URL_ENCODED_PASSWORD@cloud-sql-proxy:5432/northgate_ekyc?sslmode=disable` |
| `SECRET_KEY` | Long random signing secret shared by both APIs; generate with `openssl rand -hex 32` |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID |
| `GCS_BUCKET_NAME` | Private document bucket name |
| `GHCR_USERNAME` | GitHub account that can read the published packages |
| `GHCR_READ_TOKEN` | GitHub personal access token with `read:packages` only |

URL-encode any special characters in the database username/password. Keep secrets in the GitHub environment and cloud secret manager; never commit them or put them in the image.

The workflow at `../.github/workflows/deploy.yml`:

- Runs Python tests and TypeScript build/API tests for pull requests and pushes.
- Builds and smoke-tests the complete local Docker Compose stack.
- On pushes to `main`, publishes immutable commit-tagged images and deploys them to the VM.
- Uses the production environment approval gate if configured, waits for service health, and checks both public HTTPS health endpoints.
- Restores the previous deployment configuration if the container rollout fails.

The deployment uses a GitHub-hosted runner and SSH. Restrict VM SSH access to an approved GitHub Actions egress strategy or adapt the workflow to a self-hosted runner inside your cloud network. The SSH deployment account has Docker access, which is effectively root access on the VM.

## First deployment and account setup

After the first successful deployment, create an initial administrator interactively on the VM:

```sh
cd ~/northgate
docker compose --env-file .env -f compose.production.yaml exec kyc-api python -m app.bootstrap_user
```

Public account registration is disabled in production. Run this command again for each approved operator account, selecting the required role. The initial Python schema is applied with Alembic; the TypeScript chaser schema is applied through a versioned SQL migration. Back up Cloud SQL before applying schema changes.

Open `https://APP_DOMAIN/` after the DNS record resolves. The dashboard loads directly; sign in using an approved operator account to load and change protected case data. Caddy obtains and renews HTTPS certificates automatically. The chaser API is served behind the same HTTPS hostname at `/chaser-api`; it is not exposed as a separate public port.

## TypeScript service outside Docker

From `backend/chaser-ts`, run `npm ci`, configure `DATABASE_URL` and `SECRET_KEY`, then run `npm test` and `npm start`. Demo-case seeding is opt-in using `SEED_DEMO_DATA=true`; leave it off for production.

## Operational notes

- Production Compose is `compose.production.yaml`; it uses published container images, Cloud SQL Auth Proxy, and Caddy. It does not publish database/API ports to the internet.
- The production images run as non-root where supported and use read-only application filesystems.
- Real email is never sent by the chaser; the RM reviews and sends each request manually.
- Document authenticity, sanctions, and PEP decisions remain human-led.
- Configure Cloud SQL backups/point-in-time recovery, bucket lifecycle/retention, monitoring, alerting, and incident-response ownership with your cloud team.
- CI validates code and deployment health, but this repository does not provision infrastructure or automatically create the GCP project, VM, Cloud SQL instance, bucket, DNS, IAM, or firewall rules.
