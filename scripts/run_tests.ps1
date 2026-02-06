Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Activate-Venv {
    $candidates = @(
        ".\.venv\Scripts\Activate.ps1",
        ".\venv\Scripts\Activate.ps1",
        ".\env\Scripts\Activate.ps1",
        ".\.venv\bin\activate",   
        ".\venv\bin\activate",
        ".\env\bin\activate"
    )

    foreach ($path in $candidates) {
        if (Test-Path $path) {
            try {
                if ($path -like "*.ps1") {
                    Write-Host "Activating virtual environment: $path"
                    & $path
                } else {
                    Write-Host "Found non-PowerShell venv activation script: $path (PowerShell cannot 'source' it)."
                }
                return $true
            } catch {
                 Write-Warning ("Failed to activate venv at {0}: {1}" -f $path, $_)
            }
        }
    }

    Write-Warning "No virtual environment activation script found in .venv, venv, or env."
    return $false
}

function Ensure-Python {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "python is not available on PATH. Install Python or ensure it's on PATH."
        exit 1
    }
}

function Ensure-TestDeps {
    try {
        & python -m pytest --version > $null 2>&1
        return
    } catch {
        Write-Host "pytest not found in the active environment. Attempting to install test dependencies..."
        if (Test-Path "requirements.txt") {
            & python -m pip install -r requirements.txt
        } else {
            & python -m pip install pytest selenium webdriver-manager requests
        }
    }
}

try {
    Write-Host "Running test runner script..."

    Ensure-Python

    Activate-Venv | Out-Null

    Ensure-TestDeps

    Write-Host "Executing test suite (pytest)..."
    & python -m pytest -q
    $rc = $LASTEXITCODE

    if ($rc -eq 0) {
        Write-Host "All tests passed."
        exit 0
    } else {
        Write-Host "Some tests failed. Exit code: $rc"
        exit 1
    }
} catch {
    Write-Error "An error occurred while running tests: $_"
    exit 1
}
