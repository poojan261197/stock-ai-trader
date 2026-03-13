# Stock Prediction App - Start All Servers
# Run: powershell -ExecutionPolicy Bypass -File start-all.ps1

$root = "C:\Users\pooja\OneDrive\Desktop\Stock-Prediction-Models"
$backendPort = 8006
$frontendPort = 5173

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  StockAI - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if services already running
$backendRunning = $null -ne (Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue)
$frontendRunning = $null -ne (Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue)

if ($backendRunning) {
    Write-Host "Backend already running on port $backendPort" -ForegroundColor Green
} else {
    Write-Host "Starting Backend API on port $backendPort..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "$root\backend_api.py" -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

if ($frontendRunning) {
    Write-Host "Frontend already running on port $frontendPort" -ForegroundColor Green
} else {
    Write-Host "Starting Frontend on port $frontendPort..." -ForegroundColor Yellow
    Set-Location $root\frontend
    Start-Process -FilePath "npm" -ArgumentList "run dev" -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

# Wait and verify
Start-Sleep -Seconds 2
Write-Host ""
Write-Host "Checking services..." -ForegroundColor Cyan

$backendRunning = $null -ne (Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue)
$frontendRunning = $null -ne (Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue)

if ($backendRunning) {
    Write-Host "  Backend:  http://localhost:$backendPort/api/health" -ForegroundColor Green
} else {
    Write-Host "  Backend:  NOT RUNNING" -ForegroundColor Red
}

if ($frontendRunning) {
    Write-Host "  Frontend: http://localhost:$frontendPort" -ForegroundColor Green
} else {
    Write-Host "  Frontend: NOT RUNNING" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Open browser to: http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Start-Sleep -Seconds 1
# Open browser
Start-Process "http://localhost:$frontendPort"
