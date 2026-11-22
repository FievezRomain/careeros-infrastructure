$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root 'infra/keycloak/.env'
$example = Join-Path $root 'infra/keycloak/.env.example'

if (Test-Path -LiteralPath $target) {
    Write-Host 'Keycloak local configuration already exists; nothing was overwritten.'
    exit 0
}

if (-not (Test-Path -LiteralPath $example)) {
    throw 'Missing infra/keycloak/.env.example.'
}

function New-Secret {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes)
}

$username = 'careeros-local-admin'
$content = @(
    '# Generated locally. Never commit or share this file.'
    "KEYCLOAK_DB_PASSWORD=$(New-Secret)"
    "KEYCLOAK_BOOTSTRAP_USERNAME=$username"
    "KEYCLOAK_BOOTSTRAP_PASSWORD=$(New-Secret)"
) -join [Environment]::NewLine

[System.IO.File]::WriteAllText($target, $content + [Environment]::NewLine)
Write-Host 'Created ignored infra/keycloak/.env with independent random secrets.'
