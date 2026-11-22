# Local routing and health checks

Traefik provides the local HTTP entry point without access to the Docker socket. Routes are explicit files under `infra/routing/dynamic/`, so an unexpected container cannot publish itself.

## Start

Start the dependency stack first when services need persistence, messaging or object storage. Then start routing:

```bash
docker compose -f infra/routing/compose.local.yml up -d --wait
```

The gateway listens only on `127.0.0.1:8080`. Its routed readiness probe is:

```bash
curl --fail \
  --resolve health.careeros.localhost:8080:127.0.0.1 \
  http://health.careeros.localhost:8080/ready
```

Requests with an unknown host or route return `404`; the dashboard and Docker provider are disabled.

## Networks

| Network | Purpose | Boundary |
| --- | --- | --- |
| `careeros-edge` | Host-facing gateway traffic. | Only ingress components attach. |
| `careeros-services` | Gateway-to-service and service-to-service HTTP. | Internal Docker network. |
| `careeros-data` | PostgreSQL, RabbitMQ, S3 and services that use them. | Named Docker network; development ports remain loopback-bound and credentials enforce ownership. |

Service Compose files declare only the shared networks they need:

```yaml
networks:
  services:
    name: careeros-services
    external: true
  data:
    name: careeros-data
    external: true
```

Network attachment is not authorization. Every service still validates authentication, ownership and tenant context, and every dependency uses its scoped credentials.

## Service health contract

Every HTTP service exposes two unauthenticated, payload-free endpoints on its internal service port:

- `GET /health/live` checks only that the process can serve requests. It must not call dependencies.
- `GET /health/ready` checks the minimum dependencies required to serve traffic, each with a short timeout.

Both return `200` when healthy. Readiness returns `503` while starting, shutting down or unable to reach a required dependency. Liveness returns `503` only when the process should be restarted. Health responses may include service name, build version and coarse check names/statuses, but must not contain secrets, personal data, stack traces or dependency credentials.

Health endpoints never prove user authorization and must not trigger migrations, retries, external messages or other side effects. Service-specific checks and timeouts are documented beside the service implementation.

## Adding a route

Add a versioned host/path router and load-balancer target in a new file under `infra/routing/dynamic/`. The target uses the container DNS name on `careeros-services`. Route only public API surfaces; health, metrics and administration remain internal unless an explicit operational requirement says otherwise.

The file provider watches the mounted directory and reloads valid changes. Invalid configuration must fail CI before merge.

## Stop

```bash
docker compose -f infra/routing/compose.local.yml down
```

This removes the routing container and its empty networks when no service still uses them. It does not remove dependency data volumes.
