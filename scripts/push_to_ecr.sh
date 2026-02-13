#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/push_to_ecr.sh <aws_account_id> <region> <repo_name> <tag>
#
# Example:
#   ./scripts/push_to_ecr.sh 123456789012 us-east-1 opsvault-backend latest

AWS_ACCOUNT_ID="${1:-}"
AWS_REGION="${2:-}"
REPO_NAME="${3:-}"
TAG="${4:-latest}"

if [[ -z "$AWS_ACCOUNT_ID" || -z "$AWS_REGION" || -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <aws_account_id> <region> <repo_name> <tag>"
  exit 1
fi

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_URI}/${REPO_NAME}:${TAG}"

echo "Building image..."
docker build -t "${REPO_NAME}:${TAG}" -f backend/Dockerfile backend

echo "Ensuring ECR repo exists..."
aws ecr describe-repositories --repository-names "${REPO_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "${REPO_NAME}" --region "${AWS_REGION}" >/dev/null

echo "Logging into ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_URI}"

echo "Tagging + pushing..."
docker tag "${REPO_NAME}:${TAG}" "${IMAGE_URI}"
docker push "${IMAGE_URI}"

echo "✅ Pushed: ${IMAGE_URI}"