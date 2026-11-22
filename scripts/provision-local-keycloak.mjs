import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';

const root = new URL('../', import.meta.url);
const envPath = new URL('../infra/keycloak/.env', import.meta.url);
const fixturePath = new URL('../.local/keycloak-test-user.json', import.meta.url);
const base = 'http://localhost:8081';

if (!existsSync(envPath)) throw new Error('Run scripts/init-local-keycloak.ps1 first.');
const values = Object.fromEntries(readFileSync(envPath, 'utf8').split(/\r?\n/)
  .filter((line) => line && !line.startsWith('#')).map((line) => {
    const separator = line.indexOf('=');
    return [line.slice(0, separator), line.slice(separator + 1)];
  }));

const tokenResponse = await fetch(`${base}/realms/master/protocol/openid-connect/token`, {
  method: 'POST',
  body: new URLSearchParams({
    client_id: 'admin-cli', grant_type: 'password',
    username: values.KEYCLOAK_BOOTSTRAP_USERNAME,
    password: values.KEYCLOAK_BOOTSTRAP_PASSWORD,
  }),
});
if (!tokenResponse.ok) throw new Error(`Local bootstrap rejected (${tokenResponse.status}).`);
const { access_token: token } = await tokenResponse.json();

async function api(path, method = 'GET', body) {
  const response = await fetch(`${base}/admin/realms/careeros/${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`Provisioning failed (${response.status}, ${method}, ${path}).`);
  return response.status === 201 || response.status === 204 ? null : response.json();
}

await api('', 'PUT', {
  smtpServer: {
    host: 'mailpit', port: '1025', from: 'notifications@example.invalid',
    fromDisplayName: 'CareerOS local only', auth: 'false', ssl: 'false', starttls: 'false',
  },
  registrationAllowed: false,
  resetPasswordAllowed: false,
  bruteForceProtected: true,
});

const username = 'local-test-user';
const existing = await api(`users?username=${username}&exact=true`);
let fixture = existsSync(fixturePath) ? JSON.parse(readFileSync(fixturePath, 'utf8')) : null;
if (!fixture && existing.length) throw new Error('Unknown local fixture exists; credentials will not be overwritten.');
if (!fixture) {
  fixture = { username, password: randomBytes(24).toString('hex') };
  mkdirSync(new URL('../.local/', import.meta.url), { recursive: true });
  writeFileSync(fixturePath, JSON.stringify(fixture, null, 2), { mode: 0o600 });
}
if (!existing.length) {
  await api('users', 'POST', {
    username,
    enabled: true,
    firstName: 'Test',
    lastName: 'CareerOS',
    email: 'local-test-user@example.invalid',
    emailVerified: true,
    credentials: [{ type: 'password', value: fixture.password, temporary: false }],
    realmRoles: ['user'],
  });
}
console.log('Local CareerOS fixture provisioned. Credentials remain in ignored .local/keycloak-test-user.json.');
