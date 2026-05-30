provider "google" {
  project = var.project_id
  region  = var.region
}

data "terraform_remote_state" "foundation" {
  backend = "gcs"

  config = {
    bucket = var.state_bucket
    prefix = "wheel-winner/foundation"
  }
}

resource "google_cloud_run_v2_service" "app" {
  project             = var.project_id
  name                = var.app_name
  location            = var.region
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = data.terraform_remote_state.foundation.outputs.runtime_service_account_email

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = var.image_uri

      ports {
        container_port = 8000
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  project  = google_cloud_run_v2_service.app.project
  location = google_cloud_run_v2_service.app.location
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
