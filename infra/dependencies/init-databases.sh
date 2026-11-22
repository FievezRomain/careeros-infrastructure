#!/usr/bin/env sh
set -eu

create_service_database() {
  database_name="$1"
  role_name="$2"
  role_password="$3"

  psql --set=ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=database_name="$database_name" \
    --set=role_name="$role_name" \
    --set=role_password="$role_password" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN', :'role_name')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'role_name') \gexec
SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'role_name', :'role_password') \gexec
SELECT format('CREATE DATABASE %I OWNER %I', :'database_name', :'role_name')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'database_name') \gexec
SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', :'database_name') \gexec
SELECT format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I', :'database_name', :'role_name') \gexec
SQL
}

create_service_database careeros_identity identity_service "$IDENTITY_DB_PASSWORD"
create_service_database careeros_profile profile_service "$PROFILE_DB_PASSWORD"
create_service_database careeros_job job_service "$JOB_DB_PASSWORD"
create_service_database careeros_matching matching_service "$MATCHING_DB_PASSWORD"
create_service_database careeros_resume resume_service "$RESUME_DB_PASSWORD"
create_service_database careeros_ats ats_service "$ATS_DB_PASSWORD"
create_service_database careeros_application application_service "$APPLICATION_DB_PASSWORD"
create_service_database careeros_communication communication_service "$COMMUNICATION_DB_PASSWORD"
create_service_database careeros_analytics analytics_service "$ANALYTICS_DB_PASSWORD"
create_service_database careeros_ai_gateway ai_gateway_service "$AI_GATEWAY_DB_PASSWORD"
