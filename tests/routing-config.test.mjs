import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const routingCompose = readFileSync(new URL('../infra/routing/compose.local.yml', import.meta.url), 'utf8');
const routing = readFileSync(new URL('../infra/routing/dynamic/readiness.yml', import.meta.url), 'utf8');
const dependenciesCompose = readFileSync(new URL('../infra/dependencies/compose.local.yml', import.meta.url), 'utf8');
const documentation = readFileSync(new URL('../docs/routing.md', import.meta.url), 'utf8');

test('gateway is pinned, hardened and loopback-bound', () => {
  assert.match(routingCompose, /image: traefik:v3\.7\.19/);
  assert.match(routingCompose, /127\.0\.0\.1:8080:8080/);
  assert.match(routingCompose, /read_only: true/);
  assert.match(routingCompose, /no-new-privileges:true/);
  assert.match(routingCompose, /accesslog\.fields\.headers\.defaultmode=drop/);
  assert.doesNotMatch(routingCompose, /docker\.sock|providers\.docker|:latest\b/);
});

test('routing uses a file provider and exposes only the readiness route', () => {
  assert.match(routingCompose, /providers\.file\.directory=\/etc\/traefik\/dynamic/);
  assert.match(routingCompose, /api\.dashboard=false/);
  assert.match(routing, /Host\(`health\.careeros\.localhost`\) && Path\(`\/ready`\)/);
  assert.match(routing, /service: ping@internal/);
  assert.match(routing, /contentTypeNosniff: true/);
  assert.match(routing, /frameDeny: true/);
});

test('edge, service and data networks have stable names and service isolation', () => {
  assert.match(routingCompose, /name: careeros-edge/);
  assert.match(routingCompose, /name: careeros-services[\s\S]*?internal: true/);
  assert.match(dependenciesCompose, /name: careeros-data\r?\n\s+driver: bridge/);
  assert.equal((dependenciesCompose.match(/networks:\r?\n\s+- data/g) ?? []).length, 3);
});

test('gateway liveness is distinct from routed readiness', () => {
  assert.match(routingCompose, /entrypoints\.health\.address=:8082/);
  assert.match(routingCompose, /ping\.entrypoint=health/);
  assert.match(routingCompose, /traefik, healthcheck, --ping/);
  assert.match(documentation, /`GET \/health\/live`/);
  assert.match(documentation, /`GET \/health\/ready`/);
  assert.match(documentation, /must not contain secrets, personal data, stack traces or dependency credentials/i);
});
