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

See [docs/overview.md](docs/overview.md) and the central [CareerOS workspace](https://github.com/FievezRomain/careeros-workspace).

## Status

Architecture and security baseline. Functional implementation will be added incrementally with tests and versioned contracts.

## License

Apache-2.0.