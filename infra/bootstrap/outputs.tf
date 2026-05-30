output "github_environment_variables" {
  description = "Values to configure as GitHub production environment variables."
  value = {
    GCP_DEPLOY_SERVICE_ACCOUNT     = google_service_account.deployer.email
    GCP_PROJECT_ID                 = var.project_id
    GCP_REGION                     = var.region
    GCP_WORKLOAD_IDENTITY_PROVIDER = google_iam_workload_identity_pool_provider.github.name
    TF_STATE_BUCKET                = google_storage_bucket.terraform_state.name
  }
}

output "state_bucket" {
  description = "GCS bucket containing Terraform remote state."
  value       = google_storage_bucket.terraform_state.name
}
