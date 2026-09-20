# Operational Runbooks

## Incident: Elevated Latency

1. Confirm API and model endpoint health.
2. Inspect P95/P99 latency and saturation metrics.
3. Reduce traffic to candidate deployment.
4. Roll back if SLO breach persists beyond 5 minutes.

## Incident: Model Quality Regression

1. Compare live prediction distribution against baseline.
2. Verify feature freshness and schema drift indicators.
3. Move traffic to prior approved model version.
4. Open defect and block further promotions.

## Disaster Recovery Drill

1. Restore model artifact and metadata from backup.
2. Restore IaC state and environment config.
3. Rehydrate vector index and prompt bundle versions.
4. Validate endpoint health and replay synthetic smoke checks.
