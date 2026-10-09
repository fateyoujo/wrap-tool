@echo off
setlocal
cd /d "%~dp0"

rem Launch the fixed-width wrap GUI (no console window).
set "DSHPY=C:\Users\28404\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\pythonw.exe"
if exist "%DSHPY%" (
    start "" "%DSHPY%" "%~dp0wrap_tool.py"
    goto :done
)

where pythonw >nul 2>nul
if not errorlevel 1 (
    start "" pythonw "%~dp0wrap_tool.py"
    goto :done
)

echo Python not found. Please install Python 3.8+ and try again.
pause

:done
