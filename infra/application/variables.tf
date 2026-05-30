variable "project_id" {
  description = "Existing Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "Google Cloud region for deployment resources."
  type        = string
  default     = "europe-west1"
}

variable "app_name" {
  description = "Application name used for resource IDs."
  type        = string
  default     = "wheel-winner"
}

variable "image_uri" {
  description = "Artifact Registry URI for the container image to deploy."
  type        = string
}

variable "state_bucket" {
  description = "GCS bucket containing Terraform remote state."
  type        = string
}
