$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$pidFile = Join-Path $scriptDir "server.pid"
$stdoutFile = Join-Path $scriptDir "server.log"
$stderrFile = Join-Path $scriptDir "server.err.log"

if (Test-Path $pidFile) {
    $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($existingPid) {
        $existingProcess = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
        if ($existingProcess) {
            Write-Host "Server already running with PID $existingPid"
            exit 0
        }
    }
}

$python = (Get-Command python).Source
$process = Start-Process `
    -FilePath $python `
    -ArgumentList "realtime-agent/app.py" `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $stdoutFile `
    -RedirectStandardError $stderrFile `
    -PassThru

Set-Content -Path $pidFile -Value $process.Id
$health = $null
for ($attempt = 1; $attempt -le 10; $attempt++) {
    Start-Sleep -Seconds 1
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:8005/health"
        break
    }
    catch {
        Start-Sleep -Milliseconds 500
    }
}

if ($health) {
    Write-Host ("Server started on http://127.0.0.1:8005 with PID {0}" -f $process.Id)
    Write-Host ($health | ConvertTo-Json -Compress)
}
else {
    Write-Host "Server process started but health check failed."
    Write-Host "STDERR:"
    if (Test-Path $stderrFile) {
        Get-Content $stderrFile
    }
    exit 1
}
