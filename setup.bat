

echo Setting up environment...
rem setlocal makes any environment changes in this script local to the batch file, so they do not leak out into your shell session.
rem e.g. 
rem set MYVAR=global

rem echo Before: %MYVAR%
rem setlocal
rem set MYVAR=local
rem echo Inside script: %MYVAR%
rem endlocal

rem Before: global
rem Inside script: local
rem After: globalsetlocal
setlocal

rem The python -c ... find_spec('textgrid') line checks whether the Python module named textgrid is already installed and importable. If it is missing, the script goes into the install block; if it is present, it skips installation.
python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('textgrid') else 1)" >nul 2>&1
if errorlevel 1 (
    echo Installing textgrid...
    rem %~dp0 means “the directory where this .bat file lives"
    pushd "%~dp0textgrid-master"
    rem python -m pip install . installs the local package from that folder
    python -m pip install .
    if errorlevel 1 exit /b 1
    rem popd returns to the original directory
    popd
) else (
    echo textgrid is already installed, skipping install.
)

echo Installing graph-cli...
python -m pip install graph-cli
if errorlevel 1 (
    echo PyPI install failed, installing graph-cli from local source...
    pushd "%~dp0graph-cli-master\graph_cli"
    python -m pip install .
    if errorlevel 1 exit /b 1
    popd
)

echo Verifying imports...
python -c "import pandas as pd; import textgrid; import graph_cli; from pathlib import Path; print('Imports OK')"
if errorlevel 1 exit /b 1

echo Verifying graph command...
graph --help >nul 2>&1
if errorlevel 1 exit /b 1

echo Setup complete.