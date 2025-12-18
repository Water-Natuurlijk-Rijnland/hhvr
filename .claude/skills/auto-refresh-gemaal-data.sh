#!/bin/bash
# Wrapper script voor auto-refresh-gemaal-data skill
# Ververst gemaal data automatisch elke 30 minuten

set -e

# Determine the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Try to find Python with requests installed
PYTHON_CMD=""

# Option 1: Check for skills venv
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    if "$SCRIPT_DIR/venv/bin/python3" -c "import requests" 2>/dev/null; then
        PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
    fi
fi

# Option 2: Check for venv in peilbesluiten
if [ -z "$PYTHON_CMD" ] && [ -f "$PROJECT_ROOT/peilbesluiten/venv/bin/python3" ]; then
    if "$PROJECT_ROOT/peilbesluiten/venv/bin/python3" -c "import requests" 2>/dev/null; then
        PYTHON_CMD="$PROJECT_ROOT/peilbesluiten/venv/bin/python3"
    fi
fi

# Option 3: Try system python3
if [ -z "$PYTHON_CMD" ]; then
    if python3 -c "import requests" 2>/dev/null; then
        PYTHON_CMD="python3"
    fi
fi

# Option 4: Error if not found
if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python with 'requests' module not found" >&2
    echo "Please run: cd '$SCRIPT_DIR' && python3 -m venv venv && venv/bin/pip install requests" >&2
    exit 1
fi

# Execute the skill
cd "$PROJECT_ROOT/peilbesluiten"
exec "$PYTHON_CMD" "$PROJECT_ROOT/peilbesluiten/skills/auto_refresh_gemaal_data.py" "$@"
