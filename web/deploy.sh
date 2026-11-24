#!/usr/bin/env bash
# Deploys the Training Ground to Cloud Run. Run it from Google Cloud Shell:
#   git clone https://github.com/jordicusidoroura-stack/design_innovation_course
#   cd design_innovation_course/web && bash deploy.sh
# The first time, gcloud asks to enable some APIs and create an image repository: answer Y.
set -euo pipefail
SERVICE="${SERVICE:-venture-arena}"
REGION="${REGION:-europe-southwest1}"   # Madrid
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 256Mi --cpu 1 \
  --min-instances 0 --max-instances 2 \
  --concurrency 80
