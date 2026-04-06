#!/usr/bin/env bash
# entrypoint.sh — Build and run tests for this M2T sample.
# Usage: ./entrypoint.sh [results_dir]
#   results_dir : where to write report.json (default: <this_dir>/results)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${1:-${SCRIPT_DIR}/results}"

mkdir -p "${RESULTS_DIR}"

IMAGE_TAG="m2t-test-$(basename "${SCRIPT_DIR}")-$$"

cleanup() {
    docker rmi "${IMAGE_TAG}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "==> Building image ${IMAGE_TAG}..."
if ! docker build -t "${IMAGE_TAG}" "${SCRIPT_DIR}"; then
    echo "ERROR: Docker build failed" >&2
    exit 1
fi

echo "==> Running tests..."
docker run --rm \
    --network none \
    -v "${RESULTS_DIR}:/results" \
    "${IMAGE_TAG}"
TEST_EXIT=$?

if [ -f "${RESULTS_DIR}/report.json" ]; then
    echo "==> Report: ${RESULTS_DIR}/report.json"
else
    echo "WARNING: report.json not found" >&2
fi

exit ${TEST_EXIT}
