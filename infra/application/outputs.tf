output "service_url" {
  description = "Public Cloud Run service URL."
  value       = google_cloud_run_v2_service.app.uri
}
