param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('plan', 'apply', 'output', 'destroy')]
    [string]$Action,
    [string]$Profile = 'cms-deploy',
    [string]$Region = 'ca-central-1',
    [string]$CaBundle
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$localTerraform = Join-Path $repositoryRoot '.tools\terraform\terraform.exe'
$terraform = if (Test-Path -LiteralPath $localTerraform) {
    $localTerraform
} else {
    (Get-Command terraform -ErrorAction Stop).Source
}

if ($CaBundle) {
    $env:AWS_CA_BUNDLE = (Resolve-Path -LiteralPath $CaBundle).Path
}

$roleArn = aws configure get role_arn --profile $Profile
$sourceProfile = aws configure get source_profile --profile $Profile
if ($roleArn -and $sourceProfile) {
    $sessionName = "terraform-day1-$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
    $assumed = (& aws sts assume-role --profile $sourceProfile --role-arn $roleArn `
            --role-session-name $sessionName --duration-seconds 3600) | ConvertFrom-Json
    $credentials = $assumed.Credentials
} else {
    $credentials = (& aws configure export-credentials --profile $Profile --format process) | ConvertFrom-Json
}
if ($LASTEXITCODE -ne 0 -or -not $credentials.AccessKeyId) {
    throw "Could not obtain fresh temporary credentials from profile '$Profile'."
}
$env:AWS_ACCESS_KEY_ID = $credentials.AccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $credentials.SecretAccessKey
$env:AWS_SESSION_TOKEN = $credentials.SessionToken
$env:AWS_REGION = $Region
$env:TF_VAR_aws_region = $Region
Remove-Item Env:TF_VAR_aws_profile -ErrorAction SilentlyContinue

$directoryArgument = '-chdir=infra/day1'
Push-Location $repositoryRoot
try {
    switch ($Action) {
        'plan' { & $terraform $directoryArgument 'plan' '-input=false' '-out=day1.tfplan' '-no-color' }
        'apply' { & $terraform $directoryArgument 'apply' '-input=false' '-auto-approve' 'day1.tfplan' '-no-color' }
        'output' { & $terraform $directoryArgument 'output' '-no-color' }
        'destroy' { & $terraform $directoryArgument 'destroy' '-input=false' '-no-color' }
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Terraform $Action failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
    Remove-Item Env:AWS_ACCESS_KEY_ID,Env:AWS_SECRET_ACCESS_KEY,Env:AWS_SESSION_TOKEN -ErrorAction SilentlyContinue
}
