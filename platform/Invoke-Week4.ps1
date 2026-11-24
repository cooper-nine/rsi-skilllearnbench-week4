param([string]$Backend = 'http://127.0.0.1:39911')

$ErrorActionPreference = 'Stop'
if (-not $env:RSI_WEEK4_TOKEN) { throw 'Set RSI_WEEK4_TOKEN for this terminal.' }
$params = @{ campaignId = 'week4'; token = $env:RSI_WEEK4_TOKEN }
$body = @{ flowId = 'RSI_WEEK4_RESUME'; params = $params } | ConvertTo-Json -Compress
$response = Invoke-RestMethod -Uri "$Backend/api/engine/flow" -Method Post -ContentType 'application/json' -Body $body
$launch = $response.data.value
if ($response.status -ne 200 -or $launch.launchStatus -notin @('started', 'already_running') -or -not $launch.platformRunId) {
    throw 'The RSI engine returned no Week 4 run identifier.'
}
$response | ConvertTo-Json -Depth 6
