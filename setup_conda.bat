@echo off
echo Setting up conda environment for McDonald's McNuggets project...

REM Check if conda is installed
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Conda is not installed or not in PATH
    echo Please install Anaconda or Miniconda first
    pause
    exit /b 1
)

REM Create the conda environment
echo Creating conda environment from environment.yml...
conda env create -f environment.yml

if %errorlevel% neq 0 (
    echo Error: Failed to create conda environment
    pause
    exit /b 1
)

REM Activate the environment
echo Activating environment...
call conda activate mcdonalds-mcnuggets

REM Install the environment as a Jupyter kernel
echo Installing as Jupyter kernel...
python -m ipykernel install --user --name mcdonalds-mcnuggets --display-name "McDonald's McNuggets"

echo.
echo Setup complete! 
echo.
echo To activate the environment manually, run:
echo   conda activate mcdonalds-mcnuggets
echo.
echo To run the FastAPI backend:
echo   cd FileWizardAI/backend
echo   python -m app.server
echo.
echo To run the Flask backend:
echo   python nas_client.py
echo.
pause

