# CareerOS Infrastructure â€” service overview

## Responsibility

Provide local development and deployment configuration for containers, routing and observability.

## Data ownership

Deployable configuration templates, environment contracts and operational runbooks.

## Interfaces

- Inputs: Versioned service artifacts and environment-specific secret references.
- Outputs: Reproducible environments without embedded credentials.
- Dependencies: container runtime, ingress and observability providers.

## Initial contents

The first useful layer is Docker Compose, service health checks, local networking, Traefik/reverse-proxy configuration and observability defaults. Idempotent bootstrap, migration, backup and restore scripts may be added as operational needs appear. Terraform, Ansible, Helm or Kubernetes belong here only when the deployment model justifies them.

Current local foundations:

- `infra/dependencies/compose.local.yml` provides isolated service databases, RabbitMQ and S3-compatible object storage.
- `infra/routing/compose.local.yml` provides the loopback gateway plus explicit edge and service networks.
- `infra/keycloak/compose.local.yml` provides the dedicated CareerOS realm and identity datastore.
- Every published development port is loopback-bound and every public environment file contains placeholders only.

## Contract rules

- APIs and events are versioned.
- Consumers must be idempotent where retries are possible.
- Correlation identifiers are propagated without logging sensitive payloads.
- Authorization and ownership are checked at the service boundary.

## Non-goals

This service does not absorb responsibilities owned by another CareerOS service. Cross-service workflows are coordinated through explicit contracts rather than shared databases.

## Security and privacy

Persist the minimum data required, record provenance, define retention, redact logs and use synthetic examples in this public repository.
