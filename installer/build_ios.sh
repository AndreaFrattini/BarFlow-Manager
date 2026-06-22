#!/usr/bin/env bash
set -euo pipefail

# Script di supporto per preparare il build iOS tramite Briefcase.
# Richiede un ambiente macOS con Xcode e provisioning Apple configurati.

if ! command -v uv >/dev/null 2>&1; then
  echo "uv non trovato. Installa uv prima di continuare."
  exit 1
fi

if ! command -v briefcase >/dev/null 2>&1; then
  echo "briefcase non trovato. Esegui: uv sync"
  exit 1
fi

echo "Sincronizzazione dipendenze..."
uv sync

echo "Preparazione build iOS..."
uv run briefcase create iOS
uv run briefcase build iOS

echo "Build iOS completato."
echo "Per distribuire l'app su iPad, utilizzare TestFlight, App Store o distribuzione ad hoc con provisioning Apple."
