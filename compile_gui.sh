#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

VENV="${VENV:-.venv-build}"
WIN_PY="${WIN_PY:-python}"
export WINEDEBUG="${WINEDEBUG:--all}"
export PYTHONUTF8=1

if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --quiet --disable-pip-version-check \
  pyinstaller customtkinter

mkdir -p build/linux/work build/windows/work dist/linux dist/windows

"$VENV/bin/pyinstaller" --noconfirm --clean --onefile --windowed \
  --name PIA_GUI --collect-all customtkinter \
  --workpath build/linux/work --distpath dist/linux --specpath build/linux \
  src/gui_app.py

if ! command -v wine >/dev/null 2>&1; then
  echo "Error: wine no está instalado; no se puede compilar PIA_GUI.exe." >&2
  exit 1
fi

if ! wine "$WIN_PY" -c "import customtkinter, PyInstaller" >/dev/null 2>&1; then
  wine "$WIN_PY" -m pip install --disable-pip-version-check \
    customtkinter pyinstaller
fi

wine "$WIN_PY" -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name PIA_GUI --collect-all customtkinter \
  --workpath build/windows/work --distpath dist/windows --specpath build/windows \
  src/gui_app.py

mkdir -p attachables
install -m 755 dist/linux/PIA_GUI attachables/PIA_GUI
install -m 755 dist/windows/PIA_GUI.exe attachables/PIA_GUI.exe

echo "Listo: attachables/PIA_GUI y attachables/PIA_GUI.exe"