output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "app_url" {
  value = "http://${aws_lb.main.dns_name}"
}

output "swagger_url" {
  value = "http://${aws_lb.main.dns_name}/docs"
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}
