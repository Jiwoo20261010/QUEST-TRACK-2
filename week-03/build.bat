@echo off
rem Build pet.py into dist\pet.exe. Run from the week-03 folder (or double-click).
cd /d "%~dp0"
.venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name pet ^
  --add-data "art\frames;art\frames" ^
  --add-data "art\tak.wav;art" ^
  pet.py
echo.
echo done: dist\pet.exe
