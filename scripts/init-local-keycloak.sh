#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$script_dir/.." && pwd)
target="$root/infra/keycloak/.env"
example="$root/infra/keycloak/.env.example"

if [ -f "$target" ]; then
  printf '%s\n' 'Keycloak local configuration already exists; nothing was overwritten.'
  exit 0
fi

if [ ! -f "$example" ]; then
  printf '%s\n' 'Missing infra/keycloak/.env.example.' >&2
  exit 1
fi

if ! command -v openssl >/dev/null 2>&1; then
  printf '%s\n' 'OpenSSL is required to generate local secrets.' >&2
  exit 1
fi

umask 077
db_password=$(openssl rand -hex 32)
admin_password=$(openssl rand -hex 32)

{
  printf '%s\n' '# Generated locally. Never commit or share this file.'
  printf 'KEYCLOAK_DB_PASSWORD=%s\n' "$db_password"
  printf '%s\n' 'KEYCLOAK_BOOTSTRAP_USERNAME=careeros-local-admin'
  printf 'KEYCLOAK_BOOTSTRAP_PASSWORD=%s\n' "$admin_password"
} > "$target"

chmod 600 "$target"
printf '%s\n' 'Created ignored infra/keycloak/.env with independent random secrets.'
