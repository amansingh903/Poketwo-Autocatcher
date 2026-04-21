# setup.ps1 — Windows setup script for Poketwo Autocatcher
# Run with:  powershell -ExecutionPolicy Bypass -File setup.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── 1. Locate a Python 3.12 interpreter ──────────────────────────────────────
function Find-Python312 {
    $candidates = @("py", "python", "python3")
    foreach ($cmd in $candidates) {
        try {
            $info = & $cmd -c "import sys; print(sys.version_info[:2])" 2>$null
            if ($info -eq "(3, 12)") { return $cmd }
        } catch {}
    }

    # Try the Windows py launcher with explicit version tag
    try {
        $info = & py -3.12 -c "import sys; print(sys.version_info[:2])" 2>$null
        if ($info -eq "(3, 12)") { return "py -3.12" }
    } catch {}

    return $null
}

$PYTHON = Find-Python312
if (-not $PYTHON) {
    Write-Error @"
ERROR: Python 3.12 not found.
Install it from https://www.python.org/downloads/ and ensure it is on PATH,
or install the 'py' launcher (included with the official Windows installer).
"@
    exit 1
}

Write-Host "Using interpreter: $PYTHON"

# ── 2. Create / reuse virtual environment ────────────────────────────────────
$VENV_DIR = ".venv"

if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment in $VENV_DIR ..."
    if ($PYTHON -eq "py -3.12") {
        & py -3.12 -m venv $VENV_DIR
    } else {
        & $PYTHON -m venv $VENV_DIR
    }
} else {
    Write-Host "Virtual environment already exists, skipping creation."
}

# ── 3. Activate ───────────────────────────────────────────────────────────────
$activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Could not find activation script at $activateScript"
    exit 1
}
. $activateScript

# ── 4. Install dependencies ───────────────────────────────────────────────────
Write-Host "Upgrading pip ..."
python -m pip install --upgrade pip --quiet

Write-Host "Installing dependencies from bot/main/requirements.txt ..."
pip install -r bot/main/requirements.txt

Write-Host ""
Write-Host "✅  Setup complete."
Write-Host "   Activate the environment any time with:"
Write-Host "     .\.venv\Scripts\Activate.ps1"
Write-Host "   Then launch with:"
Write-Host "     python bot/main/main.py"
