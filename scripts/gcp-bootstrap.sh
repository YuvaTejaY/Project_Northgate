#!/usr/bin/env bash
set -euo pipefail

# Provisions GCP resources for Northgate eKYC + Document Chaser (staging or production)
# and outputs the GitHub Environment secrets required by .github/workflows/deploy.yml.
#
# Usage (from Google Cloud Shell or a machine with gcloud authenticated):
#   bash scripts/gcp-bootstrap.sh staging
#   bash scripts/gcp-bootstrap.sh production

ENV_NAME="${1:-staging}"
if [[ "$ENV_NAME" != "staging" && "$ENV_NAME" != "production" ]]; then
  echo "Usage: $0 [staging|production]" >&2
  exit 1
fi

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || true)}"
if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "(unset)" ]]; then
  echo "No GCP project selected. Run: gcloud config set project YOUR_PROJECT_ID" >&2
  exit 1
fi

REGION="${REGION:-us-central1}"
ZONE="${ZONE:-us-central1-a}"
VM_NAME="northgate-${ENV_NAME}-vm"
SA_NAME="northgate-${ENV_NAME}-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
IP_NAME="northgate-${ENV_NAME}-ip"
SQL_INSTANCE="northgate-${ENV_NAME}-pg"
DB_NAME="northgate_ekyc"
DB_USER="northgate_app"
BUCKET_NAME="${GCS_BUCKET_NAME:-$(printf '%s-northgate-%s-docs' "$PROJECT_ID" "$ENV_NAME" | tr '[:upper:]_' '[:lower:]-' | cut -c1-63)}"
SSH_USER="northgate"
KEY_PATH="${HOME}/.ssh/northgate_${ENV_NAME}_deploy"

echo "==> Project: $PROJECT_ID | Environment: $ENV_NAME | Region: $REGION | Zone: $ZONE"

echo "==> Enabling required Google Cloud APIs..."
gcloud services enable \
  compute.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  servicenetworking.googleapis.com \
  --project "$PROJECT_ID"

echo "==> Creating service account $SA_EMAIL..."
if ! gcloud iam service-accounts describe "$SA_EMAIL" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name "Northgate ${ENV_NAME} VM Service Account" \
    --project "$PROJECT_ID"
fi

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SA_EMAIL}" \
  --role "roles/cloudsql.client" \
  --quiet >/dev/null

echo "==> Creating private GCS bucket gs://${BUCKET_NAME}..."
if ! gcloud storage buckets describe "gs://${BUCKET_NAME}" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --project "$PROJECT_ID" \
    --location "$REGION" \
    --uniform-bucket-level-access \
    --public-access-prevention
fi

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
  --member "serviceAccount:${SA_EMAIL}" \
  --role "roles/storage.objectCreator" \
  --quiet >/dev/null

echo "==> Reserving static external IP $IP_NAME..."
if ! gcloud compute addresses describe "$IP_NAME" --region "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute addresses create "$IP_NAME" --region "$REGION" --project "$PROJECT_ID"
fi
VM_IP="$(gcloud compute addresses describe "$IP_NAME" --region "$REGION" --project "$PROJECT_ID" --format='value(address)')"
APP_DOMAIN="${APP_DOMAIN:-${VM_IP}.nip.io}"

echo "==> Ensuring firewall rules for HTTP (80), HTTPS (443), and SSH (22)..."
if ! gcloud compute firewall-rules describe northgate-allow-web --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute firewall-rules create northgate-allow-web \
    --project "$PROJECT_ID" \
    --allow tcp:80,tcp:443 \
    --target-tags northgate-web \
    --source-ranges 0.0.0.0/0
fi
if ! gcloud compute firewall-rules describe northgate-allow-ssh --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute firewall-rules create northgate-allow-ssh \
    --project "$PROJECT_ID" \
    --allow tcp:22 \
    --target-tags northgate-web \
    --source-ranges 0.0.0.0/0
fi

echo "==> Configuring private VPC peering for Cloud SQL..."
if ! gcloud compute addresses describe google-managed-services-default --global --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute addresses create google-managed-services-default \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=16 \
    --network=default \
    --project "$PROJECT_ID"
fi
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges=google-managed-services-default \
  --network=default \
  --project "$PROJECT_ID" >/dev/null 2>&1 || true

echo "==> Provisioning private-IP Cloud SQL PostgreSQL instance $SQL_INSTANCE (this can take several minutes)..."
if ! gcloud sql instances describe "$SQL_INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud sql instances create "$SQL_INSTANCE" \
    --project "$PROJECT_ID" \
    --database-version=POSTGRES_16 \
    --tier=db-f1-micro \
    --region="$REGION" \
    --network=default \
    --no-assign-ip
fi

if ! gcloud sql databases describe "$DB_NAME" --instance="$SQL_INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud sql databases create "$DB_NAME" --instance="$SQL_INSTANCE" --project "$PROJECT_ID"
fi

DB_PASSWORD="$(openssl rand -hex 20)"
if gcloud sql users list --instance="$SQL_INSTANCE" --project "$PROJECT_ID" --format='value(name)' | grep -qx "$DB_USER"; then
  gcloud sql users set-password "$DB_USER" --instance="$SQL_INSTANCE" --password="$DB_PASSWORD" --project "$PROJECT_ID"
else
  gcloud sql users create "$DB_USER" --instance="$SQL_INSTANCE" --password="$DB_PASSWORD" --project "$PROJECT_ID"
fi

CLOUD_SQL_INSTANCE="$(gcloud sql instances describe "$SQL_INSTANCE" --project "$PROJECT_ID" --format='value(connectionName)')"
SECRET_KEY="$(openssl rand -hex 32)"

echo "==> Generating SSH deployment key at $KEY_PATH..."
mkdir -p "${HOME}/.ssh"
chmod 700 "${HOME}/.ssh"
if [[ ! -f "$KEY_PATH" ]]; then
  ssh-keygen -t ed25519 -N "" -C "northgate-${ENV_NAME}-deploy" -f "$KEY_PATH" >/dev/null
fi
PUB_KEY="$(cat "${KEY_PATH}.pub")"

STARTUP_FILE="$(mktemp)"
trap 'rm -f "$STARTUP_FILE"' EXIT
cat <<'EOF' > "$STARTUP_FILE"
#!/usr/bin/env bash
set -euo pipefail
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
usermod -aG docker northgate || true
systemctl enable docker && systemctl start docker
EOF

echo "==> Creating Compute Engine VM $VM_NAME..."
if ! gcloud compute instances describe "$VM_NAME" --zone "$ZONE" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute instances create "$VM_NAME" \
    --project "$PROJECT_ID" \
    --zone "$ZONE" \
    --machine-type=e2-medium \
    --address="$VM_IP" \
    --image-family=ubuntu-2404-lts-amd64 \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --service-account="$SA_EMAIL" \
    --scopes=cloud-platform \
    --tags=northgate-web \
    --metadata="enable-oslogin=FALSE,ssh-keys=${SSH_USER}:${PUB_KEY}" \
    --metadata-from-file="startup-script=${STARTUP_FILE}"
else
  gcloud compute instances add-metadata "$VM_NAME" \
    --zone "$ZONE" \
    --project "$PROJECT_ID" \
    --metadata="enable-oslogin=FALSE,ssh-keys=${SSH_USER}:${PUB_KEY}"
fi

echo "==> Waiting for SSH and Docker on $VM_IP..."
KNOWN_HOSTS=""
for attempt in $(seq 1 30); do
  if KNOWN_HOSTS="$(ssh-keyscan -T 5 -H "$VM_IP" 2>/dev/null)" && [[ -n "$KNOWN_HOSTS" ]]; then
    if ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "${SSH_USER}@${VM_IP}" \
      "sudo usermod -aG docker ${SSH_USER} >/dev/null 2>&1 || true; docker compose version" >/dev/null 2>&1; then
      break
    fi
  fi
  sleep 10
done

if [[ -z "$KNOWN_HOSTS" ]]; then
  echo "Warning: Could not scan SSH host key yet. Re-run: ssh-keyscan -H $VM_IP" >&2
fi

cat <<EOF

================================================================================
GCP provisioning complete for environment: ${ENV_NAME}
App URL (after GitHub Actions deploy): https://${APP_DOMAIN}

Add these Secrets to GitHub -> Settings -> Environments -> ${ENV_NAME}:
--------------------------------------------------------------------------------
CLOUD_VM_HOST=${VM_IP}
CLOUD_VM_USER=${SSH_USER}
CLOUD_VM_KNOWN_HOSTS=${KNOWN_HOSTS}
APP_DOMAIN=${APP_DOMAIN}
CLOUD_SQL_INSTANCE=${CLOUD_SQL_INSTANCE}
KYC_DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@cloud-sql-proxy:5432/${DB_NAME}?sslmode=disable
CHASER_DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@cloud-sql-proxy:5432/${DB_NAME}?sslmode=disable
SECRET_KEY=${SECRET_KEY}
GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
GCS_BUCKET_NAME=${BUCKET_NAME}
GHCR_USERNAME=YuvaTejaY
GHCR_READ_TOKEN=<GitHub PAT with read:packages scope>
CLOUD_VM_SSH_PRIVATE_KEY (contents of ${KEY_PATH}):
$(cat "$KEY_PATH")
================================================================================
EOF
