#!/bin/zsh
# Doppio click su questo file per avviare il formattatore.
# Installa automaticamente le dipendenze se mancanti.

cd "$(dirname "$0")"

echo "=== Formattatore Code → PNG ==="

# Verifica Python 3
if ! command -v python3 &>/dev/null; then
    echo "ERRORE: Python 3 non trovato. Installalo da https://python.org"
    read -r
    exit 1
fi

# Installa dipendenze (--break-system-packages necessario su macOS con Python system)
python3 -m pip install --quiet -r requirements.txt 2>/dev/null || \
python3 -m pip install --quiet --break-system-packages -r requirements.txt 2>/dev/null || true

# Avvia app
python3 formattatore.py
