# Emirates Agent Gatekeeper - Launch Script (PowerShell)
# Project: Emirates Agent Gatekeeper (College MBA Project)
# Student Enrolment No: PGD202566060

Write-Host "=====================================================================" -ForegroundColor Red
Write-Host "      EMIRATES AGENT GATEKEEPER - MBA COLLEGE PROJECT" -ForegroundColor Yellow
Write-Host "            Student Enrolment No: PGD202566060" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Red
Write-Host ""

$pythonCmd = $null

# Check standard PATH
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Test-Path "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe") {
    $pythonCmd = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
} else {
    $localPy = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python" -Filter "python.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($localPy) {
        $pythonCmd = $localPy
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python was not found on your system." -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/ and check 'Add Python to PATH'." -ForegroundColor Yellow
    Exit 1
}

Write-Host "[INFO] Using Python: $pythonCmd" -ForegroundColor Cyan
Write-Host "[1/2] Checking dependencies..." -ForegroundColor Green
& $pythonCmd -m pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "[2/2] Launching Streamlit web application..." -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host " Open your browser at: http://127.0.0.1:8501 or http://localhost:8501" -ForegroundColor Cyan
Write-Host " (Keep this window open while using the application)" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host ""

& $pythonCmd -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
