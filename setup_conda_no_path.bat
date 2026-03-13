@echo off
echo Setting up conda environment for McDonald's McNuggets project...
echo Using full paths - no PATH modification needed

REM Try to find conda in common locations
set CONDA_PATH=
if exist "C:\Users\%USERNAME%\miniconda3\Scripts\conda.exe" (
    set CONDA_PATH=C:\Users\%USERNAME%\miniconda3\Scripts\conda.exe
    echo Found Miniconda at: %CONDA_PATH%
) else if exist "C:\Users\%USERNAME%\anaconda3\Scripts\conda.exe" (
    set CONDA_PATH=C:\Users\%USERNAME%\anaconda3\Scripts\conda.exe
    echo Found Anaconda at: %CONDA_PATH%
) else if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" (
    set CONDA_PATH=C:\ProgramData\miniconda3\Scripts\conda.exe
    echo Found Miniconda at: %CONDA_PATH%
) else (
    echo Error: Could not find conda installation
    echo Please install Miniconda or Anaconda first
    echo Common locations checked:
    echo   - C:\Users\%USERNAME%\miniconda3\Scripts\conda.exe
    echo   - C:\Users\%USERNAME%\anaconda3\Scripts\conda.exe
    echo   - C:\ProgramData\miniconda3\Scripts\conda.exe
    pause
    exit /b 1
)

REM Check if conda is working
echo Testing conda installation...
%CONDA_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Conda is not working properly
    echo Please reinstall Miniconda/Anaconda
    pause
    exit /b 1
)

REM Create the conda environment
echo Creating conda environment from environment.yml...
%CONDA_PATH% env create -f environment.yml

if %errorlevel% neq 0 (
    echo Error: Failed to create conda environment
    echo This might be because the environment already exists
    echo Trying to update instead...
    %CONDA_PATH% env update -f environment.yml
    if %errorlevel% neq 0 (
        echo Error: Failed to update conda environment
        pause
        exit /b 1
    )
)

REM Initialize conda for this session
echo Initializing conda...
call %CONDA_PATH% init cmd.exe

REM Activate the environment
echo Activating environment...
call %CONDA_PATH% activate mcdonalds-mcnuggets

REM Install the environment as a Jupyter kernel
echo Installing as Jupyter kernel...
python -m ipykernel install --user --name mcdonalds-mcnuggets --display-name "McDonald's McNuggets"

echo.
echo Setup complete! 
echo.
echo To use this environment in the future:
echo 1. Open Anaconda Prompt from Start menu, OR
echo 2. Use this command in any terminal:
echo    %CONDA_PATH% activate mcdonalds-mcnuggets
echo.
echo To run the FastAPI backend:
echo    cd FileWizardAI/backend
echo    python -m app.server
echo.
echo To run the Flask backend:
echo    python nas_client.py
echo.
pause

