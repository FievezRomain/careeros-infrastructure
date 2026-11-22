# CareerOS Infrastructure â€” service overview

## Responsibility

Provide local development and deployment configuration for containers, routing and observability.

## Data ownership

Deployable configuration templates, environment contracts and operational runbooks.

## Interfaces

- Inputs: Versioned service artifacts and environment-specific secret references.
- Outputs: Reproducible environments without embedded credentials.
- Dependencies: container runtime, ingress and observability providers.

## Contract rules

- APIs and events are versioned.
- Consumers must be idempotent where retries are possible.
- Correlation identifiers are propagated without logging sensitive payloads.
- Authorization and ownership are checked at the service boundary.

## Non-goals

This service does not absorb responsibilities owned by another CareerOS service. Cross-service workflows are coordinated through explicit contracts rather than shared databases.

## Security and privacy

Persist the minimum data required, record provenance, define retention, redact logs and use synthetic examples in this public repository.