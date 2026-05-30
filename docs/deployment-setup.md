# Deployment Setup

This guide bootstraps production deployment for an existing billed Google Cloud
project. Terraform creates the deployment identity, remote state bucket, and
required Google Cloud resources. GitHub Actions is the normal entry point for
application deployments after bootstrap.

## Prerequisites

Install:

- Terraform
- Google Cloud CLI
- GitHub CLI
- `jq`

You also need:

- An existing billed Google Cloud project.
- Google Cloud permissions to create buckets, enable APIs, create service
  accounts, configure IAM, and configure Workload Identity Federation.
- GitHub repository admin access.
- The Service Usage API enabled in the project. It is enabled by default for
  most projects, but a project administrator must enable it if Terraform reports
  that it is unavailable.

Authenticate the CLIs:

```bash
gcloud auth application-default login
gh auth login
```

## Bootstrap Google Cloud

Create the local bootstrap variable file and edit its values:

```bash
cp infra/bootstrap/terraform.tfvars.example infra/bootstrap/terraform.tfvars
```

The default state bucket name is `<project_id>-wheel-winner-tfstate`. Set
`state_bucket_name` in `terraform.tfvars` if that globally unique name is
already taken.

Run the one-time bootstrap apply:

```bash
terraform -chdir=infra/bootstrap init
terraform -chdir=infra/bootstrap apply
```

This creates:

- Required Google Cloud APIs.
- A private, versioned GCS bucket for Terraform state.
- The GitHub Actions deployer service account and IAM grants.
- A repository-restricted GitHub OIDC Workload Identity provider.

The bootstrap root intentionally keeps local state because it creates the GCS
bucket used by the other Terraform roots. Preserve `infra/bootstrap/terraform.tfstate`
in a secure operator backup. Future bootstrap changes use the same local state:

```bash
terraform -chdir=infra/bootstrap apply
```

## Configure GitHub

Create the `production` GitHub environment and populate its Actions variables
from the Terraform output:

```bash
export GH_REPO="your-github-owner/wheel-winner"

gh api \
  --method PUT \
  "repos/$GH_REPO/environments/production"

terraform -chdir=infra/bootstrap output -json github_environment_variables |
  jq -r 'to_entries[] | [.key, .value] | @tsv' |
  while IFS=$'\t' read -r name value; do
    gh variable set "$name" --env production --body "$value" --repo "$GH_REPO"
  done
```

No GitHub secrets are required. Leave the `production` environment without
required reviewers if every push to `main` must deploy automatically.

Protect `main` and require the `Backend tests` and `Terraform validation` checks
before merging. The deployment workflow still runs after every direct push to
`main`, so branch protection is the control that prevents unvalidated changes.

## Run The First Deployment

Push the infrastructure files to `main`. That push automatically triggers the
first deployment through the same workflow used by future pushes.

To dispatch a deployment manually or retry a failed run:

```bash
gh workflow run deployment.yml --ref main --repo "$GH_REPO"
gh run watch --repo "$GH_REPO"
```

The workflow applies the foundation Terraform stack, builds and pushes the
container image, applies the Cloud Run stack, and smoke-tests `/health`.

## Validate Setup

Validate Terraform syntax locally:

```bash
terraform fmt -check -recursive infra
terraform -chdir=infra/bootstrap init
terraform -chdir=infra/bootstrap validate
terraform -chdir=infra/foundation init -backend=false
terraform -chdir=infra/foundation validate
terraform -chdir=infra/application init -backend=false
terraform -chdir=infra/application validate
```

After the deployment completes, read the deployed URL from Terraform and call
the health endpoint:

```bash
terraform -chdir=infra/application init \
  -backend-config="bucket=$TF_STATE_BUCKET" \
  -backend-config="prefix=wheel-winner/application"

SERVICE_URL="$(terraform -chdir=infra/application output -raw service_url)"
curl --fail --silent --show-error "$SERVICE_URL/health"
```

The expected response is:

```json
{"status":"ok"}
```

## Troubleshooting

- If bootstrap cannot enable APIs, verify that the Service Usage API is enabled
  and that your Google Cloud identity can manage project services.
- If deployment reports that Cloud Resource Manager API is disabled, update the
  repository, run `terraform -chdir=infra/bootstrap apply`, wait briefly for API
  activation to propagate, and retry the `Deployment` workflow.
- If Terraform cannot access state, verify the bucket name and the deployer
  service account bucket IAM binding.
- If OIDC authentication fails, verify `github_owner`, `github_repository`, and
  the GitHub environment variables.
- If public invocation fails, check whether an organization policy prevents
  granting `allUsers` the `roles/run.invoker` role.
- If the smoke test fails, inspect the Cloud Run revision logs and confirm the
  container listens on port `8000`.
