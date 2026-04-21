#!/usr/bin/env bash
# setup.sh — Linux / macOS setup script for Poketwo Autocatcher
set -euo pipefail

# ── 1. Locate a Python 3.12 interpreter ──────────────────────────────────────
find_python312() {
    for cmd in python3.12 python3 python; do
        if command -v "$cmd" &>/dev/null; then
            ver=$("$cmd" -c 'import sys; print(sys.version_info[:2])' 2>/dev/null)
            if [ "$ver" = "(3, 12)" ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python312 || true)

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.12 not found."
    echo "Install it via your package manager, pyenv, or https://www.python.org/downloads/"
    exit 1
fi

echo "Using interpreter: $PYTHON ($($PYTHON --version))"

# ── 2. Create / reuse virtual environment ────────────────────────────────────
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR …"
    "$PYTHON" -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists, skipping creation."
fi

# ── 3. Activate and install dependencies ─────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip …"
python -m pip install --upgrade pip --quiet

echo "Installing dependencies from bot/main/requirements.txt …"
pip install -r bot/main/requirements.txt

echo ""
echo "✅  Setup complete."
echo "   Activate the environment any time with:"
echo "     source $VENV_DIR/bin/activate"
echo "   Then launch with:"
echo "     python bot/main/main.py"
