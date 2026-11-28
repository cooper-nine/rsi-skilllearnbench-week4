param(
    [Parameter(Mandatory=$true)][string]$FrontendCases,
    [Parameter(Mandatory=$true)][string]$BenchmarkHome,
    [ValidateRange(1,10)][int[]]$CaseNumber = (1..10),
    [string]$FrontendUrl = 'http://127.0.0.1:3020',
    [ValidateRange(60,7200)][int]$TimeoutSeconds = 1800
)

$ErrorActionPreference = 'Stop'
$FrontendCases = (Resolve-Path -LiteralPath $FrontendCases).Path
$BenchmarkHome = (Resolve-Path -LiteralPath $BenchmarkHome).Path
$origin = $FrontendUrl.TrimEnd('/')
$platform = Join-Path $BenchmarkHome 'output/qwen_rsi_flow/platform'
$results = foreach ($number in ($CaseNumber | Select-Object -Unique)) {
    $name = 'case{0:D2}' -f $number
    $body = Get-Content -LiteralPath (Join-Path $FrontendCases "$name.json") -Raw -Encoding utf8
    $case = $body | ConvertFrom-Json
    if ($case.mode -ne 'fresh' -or $case.target -isnot [string]) {
        throw "$name 必须是从原始输入发起的单题画布请求"
    }
    $reply = Invoke-RestMethod "$origin/test/week4/launch" -Method Post -TimeoutSec 30 `
        -Headers @{ Origin = $origin } -ContentType 'application/json; charset=utf-8' `
        -Body ([Text.Encoding]::UTF8.GetBytes($body))
    $launch = $reply.data.value
    if (!$launch.platformRunId -or $launch.runDirectory) {
        throw "$name 未收到 Spring Boot 的运行 ID。请核对前端令牌和后端地址。"
    }
    $id = $launch.platformRunId
    if ($id -notmatch '^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$') { throw '运行 ID 格式无效' }
    $folder = Join-Path $platform $id
    $canvas = Join-Path $folder 'canvas.json'
    if (!(Test-Path -LiteralPath $canvas) -or (Get-Content -LiteralPath $canvas -Raw -Encoding utf8) -ne $body) {
        throw "$name 的后端画布与提交内容不一致，请核对 BenchmarkHome"
    }
    Write-Host "$name $($case.target) · Spring Boot · $id"
    $verdict = Join-Path $folder 'results.json'
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $record = @()
    while (!$record.Count) {
        if (Test-Path -LiteralPath $verdict) {
            try { $record = @(Get-Content -LiteralPath $verdict -Raw -Encoding utf8 | ConvertFrom-Json) }
            catch { $record = @() }
        }
        if ($record.Count) { break }
        if ([DateTime]::UtcNow -ge $deadline) { throw "$name 未取得判分记录，请查看 $folder/runner.log" }
        Start-Sleep -Seconds 3
    }
    if ($record.Count -ne 1 -or "$($record[0].family)-$($record[0].instance)" -ne $case.target -or $record[0].platform_run_id -ne $id) {
        throw "$name 的逐题结果与提交的题目或运行 ID 不一致"
    }
    $row = $record[0]
    Write-Host "$name · $($row.status) · official_pass=$($row.treatment_passed)"
    [pscustomobject]@{ Case=$name; Task=$case.target; RunId=$id; Status=$row.status; Passed=$row.treatment_passed; Evidence=$verdict }
}
$results | Format-Table Case, Task, RunId, Status, Passed -AutoSize
if (@($results | Where-Object { $_.Status -ne 'valid' -or $_.Passed -ne $true }).Count) { exit 1 }
