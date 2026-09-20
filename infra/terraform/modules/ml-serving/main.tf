locals {
  name = "${var.service_name}-${var.environment}"
}

resource "aws_cloudwatch_log_group" "service" {
  name              = "/mlops/${local.name}"
  retention_in_days = 30
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.service.name
}
