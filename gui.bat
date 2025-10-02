@echo off
:: Portable GUI Launcher
:: This batch file hides itself and runs the Python GUI
:: Works regardless of where the folder is moved

:: Check if running hidden, if not, hide and rerun
if "%1" == "HIDDEN" goto :run_hidden
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" HIDDEN",0)(window.close)&&exit

:run_hidden
:: Change to the directory where this batch file is located
cd /d "%~dp0"

:: Check if python executable exists
if not exist "python-3.12.4-embed-amd64\pythonw.exe" (
    mshta vbscript:msgbox("Python executable not found!",48,"Error"^)(window.close^)
    exit /b 1
)

:: Check if GUI script exists  
if not exist "gui.py" (
    mshta vbscript:msgbox("GUI script not found!",48,"Error"^)(window.close^)
    exit /b 1
)

:: Launch the GUI application
start "" "python-3.12.4-embed-amd64\pythonw.exe" "gui.py"
exit