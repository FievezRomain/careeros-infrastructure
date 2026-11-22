# Keycloak local foundation

CareerOS uses a dedicated `careeros` realm. The same realm contract can live in an existing trusted Keycloak installation or in a separate CareerOS installation. The services depend on the configured issuer, audience and claims, not on the physical host choice.

## Origin of the pattern

This setup adapts the proven Vasco Admin principle:

- Keycloak and its database are isolated from business databases;
- local ports bind only to loopback;
- secrets are generated locally and ignored by Git;
- the realm import initializes an empty installation;
- an explicit provisioning script safely completes or refreshes an existing realm;
- test identities are synthetic and stored only in an ignored local file.

No Vasco realm, role, account, domain, secret or personal data is copied.

## Local start

Prerequisites: Docker Desktop, PowerShell and a current Node.js runtime.

```powershell
./scripts/init-local-keycloak.ps1
docker compose --env-file infra/keycloak/.env -f infra/keycloak/compose.local.yml config --quiet
docker compose --env-file infra/keycloak/.env -f infra/keycloak/compose.local.yml up -d
node scripts/provision-local-keycloak.mjs
```

The first command is idempotent and never replaces an existing `.env`. The generated file and the synthetic fixture in `.local/` must never be printed in CI, attached to an issue or committed.

Local endpoints:

- Keycloak: `http://localhost:8081`
- Mailpit: `http://localhost:8025`

Both are local-development conveniences, not production exposure rules.

## Reuse decision later

When deployment is selected, choose one of these without changing business services:

1. create the `careeros` realm in the already operated Keycloak instance, with separate clients, roles, keys and administrators; or
2. deploy a dedicated Keycloak instance and import the same realm contract.

Before reusing an instance, verify administrative separation, backup/restore, upgrade ownership, capacity, hostname/TLS, email delivery, audit retention and incident blast radius. Never reuse a Vasco client secret or user database as CareerOS configuration.

## Production differences

`start-dev`, loopback callbacks, Mailpit, the bootstrap administrator and synthetic users are local only. Production requires TLS, a stable hostname, secrets from an approved secret store, restricted administration, backups, recovery rehearsal, monitoring and a reviewed account-recovery process.

## Validation

Configuration-only checks do not start containers or create accounts:

```powershell
node --test tests/keycloak-config.test.mjs
node --check scripts/provision-local-keycloak.mjs
```
