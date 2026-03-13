$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir "server.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "No PID file found."
    exit 0
}

$pidValue = Get-Content $pidFile -ErrorAction SilentlyContinue
if (-not $pidValue) {
    Remove-Item $pidFile -Force
    Write-Host "PID file was empty."
    exit 0
}

$process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $pidValue
    Write-Host "Stopped server PID $pidValue"
}
else {
    Write-Host "No running process found for PID $pidValue"
}

Remove-Item $pidFile -Force
