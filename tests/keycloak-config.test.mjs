import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const compose = readFileSync(new URL('../infra/keycloak/compose.local.yml', import.meta.url), 'utf8');
const realm = JSON.parse(readFileSync(new URL('../infra/keycloak/realm/careeros-realm.json', import.meta.url), 'utf8'));
const envExample = readFileSync(new URL('../infra/keycloak/.env.example', import.meta.url), 'utf8');
const initScript = readFileSync(new URL('../scripts/init-local-keycloak.sh', import.meta.url), 'utf8');

test('local ports are bound to loopback', () => {
  for (const mapping of compose.matchAll(/- "([^"]+)"/g)) {
    if (mapping[1].includes(':')) assert.match(mapping[1], /^127\.0\.0\.1:/);
  }
});

test('realm applies the V1 security baseline', () => {
  assert.equal(realm.realm, 'careeros');
  assert.equal(realm.registrationAllowed, false);
  assert.equal(realm.bruteForceProtected, true);
  assert.equal(realm.revokeRefreshToken, true);
  assert.equal(realm.clients.find((client) => client.clientId === 'careeros-web').attributes['pkce.code.challenge.method'], 'S256');
  assert.equal(realm.clients.find((client) => client.clientId === 'careeros-api').bearerOnly, true);
});

test('public configuration contains no populated secret', () => {
  for (const line of envExample.split(/\r?\n/).filter((value) => value && !value.startsWith('#'))) {
    assert.match(line, /^[A-Z0-9_]+=$/);
  }
  assert.doesNotMatch(JSON.stringify(realm), /vasco|password\s*[:=]\s*[^}\"]+/i);
});

test('Linux initialization is fail-safe and creates a private file', () => {
  assert.match(initScript, /^#!\/usr\/bin\/env sh\n/);
  assert.match(initScript, /set -eu/);
  assert.match(initScript, /umask 077/);
  assert.match(initScript, /openssl rand -hex 32/);
  assert.match(initScript, /chmod 600/);
  assert.doesNotMatch(initScript, /powershell|\.ps1/i);
});
