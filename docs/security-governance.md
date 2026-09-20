# Security and Governance Baseline

## Identity and Access

- least-privilege AWS IAM roles by environment
- Databricks permissions separated by workspace and service principal
- no human long-lived keys for production deployment pipelines

## Secrets and Encryption

- AWS Secrets Manager or Databricks secret scopes for credentials
- TLS in transit for service-to-service calls
- KMS-backed encryption at rest for artifacts, logs, and state

## Network and Endpoint Controls

- private VPC networking for serving workloads
- API Gateway/ALB authentication and rate limiting
- tenant isolation boundaries for shared endpoints

## Responsible AI Controls

- prompt injection scanning and content-safety filtering
- PII redaction and sensitive payload logging restrictions
- model lineage and approval record retention

## Auditability

- promotion events with approver and evidence URI
- deployment records with code, model, config, and prompt versions
- incident timeline and rollback traceability
