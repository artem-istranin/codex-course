variable "project_id" {
  description = "Existing billed Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "Google Cloud region for deployment resources."
  type        = string
  default     = "europe-west1"
}

variable "github_owner" {
  description = "GitHub repository owner or organization."
  type        = string
}

variable "github_repository" {
  description = "GitHub repository name."
  type        = string
  default     = "wheel-winner"
}

variable "app_name" {
  description = "Application name used for resource IDs."
  type        = string
  default     = "wheel-winner"
}

variable "state_bucket_name" {
  description = "Globally unique GCS bucket name for Terraform remote state. Defaults to <project_id>-<app_name>-tfstate."
  type        = string
  default     = null
}
