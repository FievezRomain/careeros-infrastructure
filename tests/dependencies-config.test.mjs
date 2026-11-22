import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const compose = readFileSync(new URL('../infra/dependencies/compose.local.yml', import.meta.url), 'utf8');
const envExample = readFileSync(new URL('../infra/dependencies/.env.example', import.meta.url), 'utf8');
const initScript = readFileSync(new URL('../infra/dependencies/init-databases.sh', import.meta.url), 'utf8');

const requiredVariables = [
  'POSTGRES_ADMIN_PASSWORD',
  'IDENTITY_DB_PASSWORD',
  'PROFILE_DB_PASSWORD',
  'JOB_DB_PASSWORD',
  'MATCHING_DB_PASSWORD',
  'RESUME_DB_PASSWORD',
  'ATS_DB_PASSWORD',
  'APPLICATION_DB_PASSWORD',
  'COMMUNICATION_DB_PASSWORD',
  'ANALYTICS_DB_PASSWORD',
  'AI_GATEWAY_DB_PASSWORD',
  'RABBITMQ_USERNAME',
  'RABBITMQ_PASSWORD',
  'S3_ACCESS_KEY',
  'S3_SECRET_KEY',
];

test('dependency images are pinned and services expose health checks', () => {
  assert.match(compose, /image: postgres:16\.15/);
  assert.match(compose, /image: rabbitmq:4\.4\.1-management/);
  assert.match(compose, /image: chrislusf\/seaweedfs:4\.53/);
  assert.doesNotMatch(compose, /:latest\b/);
  assert.equal((compose.match(/healthcheck:/g) ?? []).length, 3);
});

test('all published dependency ports are loopback-bound', () => {
  const mappings = [...compose.matchAll(/- "([^"]+:[^"]+)"/g)].map((match) => match[1]);
  assert.deepEqual(mappings, [
    '127.0.0.1:5432:5432',
    '127.0.0.1:5672:5672',
    '127.0.0.1:15672:15672',
    '127.0.0.1:8333:8333',
  ]);
});

test('public environment template contains placeholders only and all are required', () => {
  const assignments = envExample
    .split(/\r?\n/)
    .filter((line) => line && !line.startsWith('#'));
  assert.deepEqual(assignments.map((line) => line.slice(0, line.indexOf('='))), requiredVariables);
  for (const line of assignments) assert.match(line, /^[A-Z0-9_]+=$/);
  for (const name of requiredVariables) assert.ok(compose.includes(`\${${name}:?`), `${name} must be required`);
});

test('service databases have distinct owners and deny public access', () => {
  const databases = [...initScript.matchAll(/create_service_database (careeros_[a-z_]+) ([a-z_]+) "\$([A-Z0-9_]+)"/g)];
  assert.equal(databases.length, 10);
  assert.equal(new Set(databases.map((entry) => entry[1])).size, 10);
  assert.equal(new Set(databases.map((entry) => entry[2])).size, 10);
  assert.equal(new Set(databases.map((entry) => entry[3])).size, 10);
  assert.match(initScript, /REVOKE ALL ON DATABASE %I FROM PUBLIC/);
  assert.doesNotMatch(initScript, /password\s*=\s*[^"$]/i);
});

test('broker and object storage require authentication', () => {
  assert.match(compose, /RABBITMQ_DEFAULT_USER: \$\{RABBITMQ_USERNAME:\?/);
  assert.match(compose, /RABBITMQ_DEFAULT_PASS: \$\{RABBITMQ_PASSWORD:\?/);
  assert.match(compose, /AWS_ACCESS_KEY_ID: \$\{S3_ACCESS_KEY:\?/);
  assert.match(compose, /AWS_SECRET_ACCESS_KEY: \$\{S3_SECRET_KEY:\?/);
  assert.doesNotMatch(compose, /\bguest\b|allow.?all/i);
});
