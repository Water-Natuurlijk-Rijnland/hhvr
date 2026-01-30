#!/bin/bash
# Dit script schoont de projectstructuur op door documentatie en testbestanden te verplaatsen.

# Stop on error
set -e

echo "--- Opschonen van de root-directory ---"
mkdir -p docs
find . -maxdepth 1 -type f -name "*.md" ! -name "README.md" -exec mv -v {} docs/ \;
echo "Root-directory opgeschoond."

# --- Opschonen van de peilbesluiten map ---
echo ""
echo "--- Opschonen van de 'peilbesluiten' map ---"
mkdir -p docs/peilbesluiten
find peilbesluiten -maxdepth 1 -type f -name "*.md" ! -name "README.md" -exec mv -v {} docs/peilbesluiten/ \;
mkdir -p peilbesluiten/tests
find peilbesluiten -maxdepth 1 -type f -name "test_*.py" -exec mv -v {} peilbesluiten/tests/ \;
echo "Verwijderen van test-artefacten in 'peilbesluiten'..."
rm -f peilbesluiten/gemaal_*.png
rm -f peilbesluiten/test_sliding_window_real_output.json
echo "'peilbesluiten' opschonen voltooid."

# --- Opschonen van de simulatie-peilbeheer map ---
echo ""
echo "--- Opschonen van de 'simulatie-peilbeheer' map ---"
mkdir -p docs/simulatie-peilbeheer
find simulatie-peilbeheer -maxdepth 1 -type f -name "*.md" ! -name "README.md" -exec mv -v {} docs/simulatie-peilbeheer/ \;
mkdir -p simulatie-peilbeheer/tests
echo "Verplaatsen van test-scripts in 'simulatie-peilbeheer'..."
# Gebruik een for-loop om 'no match' fouten te voorkomen als een type bestand niet bestaat
for f in simulatie-peilbeheer/test_*.js; do [ -e "$f" ] && mv -v "$f" simulatie-peilbeheer/tests/ || true; done
for f in simulatie-peilbeheer/test_*.cjs; do [ -e "$f" ] && mv -v "$f" simulatie-peilbeheer/tests/ || true; done
for f in simulatie-peilbeheer/test_*.html; do [ -e "$f" ] && mv -v "$f" simulatie-peilbeheer/tests/ || true; done
echo "'simulatie-peilbeheer' opschonen voltooid."

echo ""
echo "Alle opschoonacties zijn voltooid."
