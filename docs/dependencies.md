# Local platform dependencies

The V1 local dependency stack provides PostgreSQL 16, RabbitMQ 4 and an S3-compatible SeaweedFS endpoint. It is single-node development infrastructure, not a production availability model.

## Configure

Prerequisites: Docker Engine with the Compose plugin.

```bash
cp infra/dependencies/.env.example infra/dependencies/.env
```

Fill every value in the ignored `.env` file with local-only credentials. Empty values fail Compose interpolation before any container starts. Never reuse these credentials outside local development.

## Start and verify

```bash
docker compose \
  --env-file infra/dependencies/.env \
  -f infra/dependencies/compose.local.yml \
  up -d --wait

docker compose \
  --env-file infra/dependencies/.env \
  -f infra/dependencies/compose.local.yml \
  ps
```

Published endpoints are restricted to loopback:

| Dependency | Local endpoint | Container endpoint |
| --- | --- | --- |
| PostgreSQL | `localhost:5432` | `postgres:5432` |
| RabbitMQ AMQP | `localhost:5672` | `rabbitmq:5672` |
| RabbitMQ management | `http://localhost:15672` | `http://rabbitmq:15672` |
| S3 API | `http://localhost:8333` | `http://object-storage:8333` |

PostgreSQL initializes one logical database, owner role and password per backend service. Public database access is revoked; no service may use the admin account or another service's role. The fixed database names are `careeros_identity`, `careeros_profile`, `careeros_job`, `careeros_matching`, `careeros_resume`, `careeros_ats`, `careeros_application`, `careeros_communication`, `careeros_analytics` and `careeros_ai_gateway`.

RabbitMQ creates the local `careeros` vhost. Exchanges, queues, policies and service-specific permissions are introduced with their owning event contracts. SeaweedFS creates the `careeros-resumes` bucket and requires S3 credentials.

## Stop

```bash
docker compose \
  --env-file infra/dependencies/.env \
  -f infra/dependencies/compose.local.yml \
  down
```

Named volumes preserve local state. Do not add `--volumes` unless intentionally discarding all synthetic local dependency data.

## Limits

- The stack has no high availability, public ingress or production TLS configuration.
- Local management and data ports must remain loopback-bound.
- Production credentials come from environment-specific secret stores.
- Backup and restore are delivered by V1-046; routing and service networks are delivered by V1-005.
