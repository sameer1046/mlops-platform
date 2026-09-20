# Terraform Layout

- `modules/ml-serving`: shared serving baseline resources
- `envs/dev`: development environment overlay
- `envs/staging`: staging environment overlay
- `envs/prod`: production environment overlay

Expand with:

- EKS/ECS modules
- SageMaker endpoint modules
- Databricks workspace bindings
- API Gateway and ALB modules
- IAM and policy modules
- observability and alerting modules
