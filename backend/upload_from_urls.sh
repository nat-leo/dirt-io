#!/bin/bash
set -euo pipefail

# usage: backend/upload_from_urls.sh area-symbol-urls.tsv

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <area-symbol-urls.tsv>"
  exit 1
fi

URL_FILE="$1"
MANIFEST="$(mktemp)"

cut -f2 "$URL_FILE" | tail -n +2 >"$MANIFEST"

if [[ ! -s "$MANIFEST" ]]; then
  echo "Manifest is empty; nothing to download."
  rm -f "$MANIFEST"
  exit 0
fi

echo "Authenticating with Google Cloud (if needed)..."
if ! gcloud auth application-default print-access-token >/dev/null 2>&1; then
  echo "Run 'gcloud auth application-default login' before continuing."
  rm -f "$MANIFEST"
  exit 1
fi

echo "Uploading packages from $URL_FILE to GCS bucket (root or GCS_BUCKET env if set)"
python -m pipelines.nrcs_to_google_cloud_storage --manifest "$MANIFEST"

rm -f "$MANIFEST"
