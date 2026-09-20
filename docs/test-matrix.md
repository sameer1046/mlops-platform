# Deployment Lifecycle Test Matrix

| Stage | Required Tests |
|---|---|
| Pull Request | Unit tests, lint, static security scan, contract validation |
| Merge to Main | Integration tests, API tests, model validation, regression tests |
| Pre-Prod | Performance/load tests, DAST, canary/shadow simulation |
| Production | Progressive rollout checks, runtime health checks, rollback drills |

## Categories

- Unit testing
- Integration testing
- Model validation
- Data contract validation
- API and endpoint testing
- Security testing
- Performance and load testing
- Regression testing

## Exit Criteria

- No critical security findings
- SLO compliance for latency and error rate
- Model quality and drift thresholds satisfied
- Promotion and deployment audit records generated
