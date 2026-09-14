param(
    [Parameter(Mandatory = $true)][string]$Profile,
    [Parameter(Mandatory = $true)][string]$Region,
    [string]$CaBundle
)

$ErrorActionPreference = 'Stop'
if ($CaBundle) {
    $env:AWS_CA_BUNDLE = (Resolve-Path -LiteralPath $CaBundle).Path
}

$identityJson = & aws sts get-caller-identity --profile $Profile --region $Region --output json
if ($LASTEXITCODE -ne 0) {
    throw 'AWS identity verification failed; no deployment should proceed.'
}
$identity = $identityJson | ConvertFrom-Json
if ($identity.Arn -match ':root$') {
    throw "Profile '$Profile' resolves to the AWS root identity. Use a delegated IAM/SSO role for deployment."
}
if ($identity.Arn -notmatch ':assumed-role/IntelligentCmsDay1DeployRole/') {
    throw "Profile '$Profile' is not using the expected IntelligentCmsDay1DeployRole."
}

Write-Output "Verified profile=$Profile region=$Region account=$($identity.Account) principal=$($identity.Arn)"
