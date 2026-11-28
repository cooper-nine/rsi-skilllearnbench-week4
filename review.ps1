param(
    [switch]$Live,
    [string]$BenchmarkHome = '',
    [int]$Port = 3020
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$work = Join-Path $root '.review'
New-Item -ItemType Directory -Path $work -Force | Out-Null
$python = (Get-Command python.exe).Source
$npm = (Get-Command npm.cmd).Source
Get-Command git.exe, node.exe | Out-Null

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command failed with exit code $LASTEXITCODE" }
}

foreach ($project in @(@('rsi-data-visual', 'rsi-flow-visual'), @('rsi-data-platform', 'rsi-data-platform'))) {
    $folder = Join-Path $work $project[1]
    if (!(Test-Path -LiteralPath (Join-Path $folder '.git'))) {
        Invoke-Checked git.exe @('clone', '--depth', '1', '--branch', 'main', "https://github.com/cooper-nine/$($project[0]).git", $folder)
    }
}

$env:RSI_WEEK4_EVIDENCE_HOME = $root
$env:RSI_WEEK4_REVIEW_PYTHON = $python
$env:npm_config_cache = Join-Path $work 'npm-cache'
$env:RSI_WEEK4_LOCAL_RUN = '0'
Remove-Item Env:RSI_WEEK4_TOKEN -ErrorAction SilentlyContinue
if ($Live) {
    if (!$env:DASHSCOPE_API_KEY) { throw 'Set DASHSCOPE_API_KEY to your own DashScope key before starting live mode.' }
    Invoke-Checked docker.exe @('info', '--format', '{{.ServerVersion}}')
    if (!$BenchmarkHome) { $BenchmarkHome = Join-Path $work 'upstream-sparse' }
    $BenchmarkHome = [System.IO.Path]::GetFullPath($BenchmarkHome)
    if (!(Test-Path -LiteralPath (Join-Path $BenchmarkHome 'qwen/run_canvas_campaign.py'))) {
        Invoke-Checked $python @((Join-Path $root 'prepare.py'), '--workspace', $BenchmarkHome, '--install', '--build-images')
    }
    $env:RSI_WEEK4_BENCHMARK_HOME = $BenchmarkHome
    $env:RSI_WEEK4_LOCAL_RUN = '1'
}

Push-Location (Join-Path $work 'rsi-data-platform')
try {
    $pnpm = @('exec', '--yes', '--package=pnpm@10.34.9', '--', 'pnpm')
    Invoke-Checked $npm ($pnpm + @('install', '--frozen-lockfile', '--store-dir', (Join-Path $work 'pnpm-store')))
    Write-Host "Open http://127.0.0.1:$Port/test/week4"
    Invoke-Checked $npm ($pnpm + @('dev', '--hostname', '127.0.0.1', '--port', "$Port"))
} finally {
    Pop-Location
}
