# CareerOS Infrastructure

Provide local development and deployment configuration for containers, routing and observability.

## Scope

- **Owns:** Deployable configuration templates, environment contracts and operational runbooks.
- **Inputs:** Versioned service artifacts and environment-specific secret references.
- **Outputs:** Reproducible environments without embedded credentials.
- **Dependencies:** container runtime, ingress and observability providers.

## Safety baseline

This public repository must never contain secrets, real resumes, real applications or personal data. External communication and application submission always require explicit user approval.

## Documentation

See:

- [Service overview](docs/overview.md)
- [Local platform dependencies](docs/dependencies.md)
- [Local Keycloak foundation](docs/keycloak.md)
- [Central CareerOS workspace](https://github.com/FievezRomain/careeros-workspace)

## Status

Local Keycloak and core dependency stacks are available with tests and placeholder-only configuration. Routing, observability and deployment automation remain incremental.

## License

Apache-2.0.
