# Deploy OpsVaultAI to AWS ECS Fargate (Runbook)

This is a console-first runbook (fastest path). You can later automate with Terraform.

## Prereqs
- AWS account + billing alerts
- AWS CLI configured:
  ```bash
  aws configure
  aws sts get-caller-identity
