# Deployment Architecture

Wheel Winner is deployed as a public Google Cloud Run service. Terraform manages
the application infrastructure, and GitHub Actions deploys every push to `main`.

## Architecture

- Google Artifact Registry stores Docker images tagged with the Git commit SHA.
- Google Cloud Run runs the stateless FastAPI container and serves both the API
  and frontend.
- A dedicated Google service account is attached to the Cloud Run service.
- A bootstrap Terraform stack creates the Google Cloud Storage bucket used for
  remote state.
- GitHub Actions authenticates to Google Cloud with Workload Identity Federation
  and OpenID Connect (OIDC). No long-lived Google Cloud key is stored in GitHub.

## Infrastructure Lifecycle

Terraform is split into three roots:

- `infra/bootstrap` creates the state bucket, setup APIs, GitHub deployment
  identity, IAM grants, and OIDC provider. An operator applies it once locally.
- `infra/foundation` enables runtime APIs, creates the Artifact Registry Docker
  repository, and creates the Cloud Run runtime service account.
- `infra/application` reads foundation outputs from remote state and creates the
  public Cloud Run v2 service.

The foundation root is separate because Cloud Run cannot be created until a
container image exists, while the image cannot be pushed until Artifact
Registry exists. The deployment workflow applies `infra/foundation`, builds and
pushes the image, then applies `infra/application` with that image URI. This
keeps the initial deployment and later updates on the same workflow path without
special-case bootstrap logic.

The stacks use separate prefixes in the same state bucket:

```text
wheel-winner/foundation
wheel-winner/application
```

The bootstrap root intentionally keeps local operator state because it creates
the remote state bucket required by the other roots. Back up that local state
securely after bootstrap.

After the local bootstrap apply, the GitHub CLI configures the `production`
environment from Terraform outputs. The `Deployment` workflow is then the main
entry point for infrastructure and application updates. See
[deployment-setup.md](deployment-setup.md).

## CI/CD Flow

The `CI` workflow runs backend tests and validates all Terraform roots on pull
requests, pushes to `main`, and manual dispatches.

The separate `Deployment` workflow runs on pushes to `main` and manual
dispatches:

1. Authenticate to Google Cloud through GitHub OIDC.
2. Apply the foundation Terraform stack.
3. Build the repository Dockerfile and push a commit-SHA image to Artifact
   Registry.
4. Apply the application Terraform stack with that immutable image URI.
5. Request the deployed `/health` endpoint and fail the run if it is unhealthy.

The workflow uses the GitHub `production` environment and serializes deployment
runs so concurrent pushes cannot apply Terraform state at the same time.
