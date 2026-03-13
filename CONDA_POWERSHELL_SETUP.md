# Using Conda with PowerShell/Command Prompt (Without PATH)

You're right to be cautious about adding conda to your system PATH. Here are better alternatives:

## Option 1: Use Anaconda Prompt (Easiest)

The installer creates a special terminal that automatically has conda available:

1. **After installing Miniconda**, search for "Anaconda Prompt" in your Start menu
2. **Use this terminal** instead of regular PowerShell/Command Prompt
3. **Navigate to your project**:
   ```cmd
   cd C:\Users\KevSa\Documents\GitHub\McDonalds-McNuggets
   ```
4. **Run the setup**:
   ```cmd
   setup_conda.bat
   ```

## Option 2: Initialize PowerShell for Conda

You can configure PowerShell to work with conda without adding it to system PATH:

### For PowerShell:
1. **Open PowerShell as Administrator**
2. **Run this command** (replace with your actual Miniconda path):
   ```powershell
   C:\Users\KevSa\miniconda3\shell\condabin\conda-hook.ps1
   ```
3. **Or add this to your PowerShell profile**:
   ```powershell
   # Add to $PROFILE
   & "C:\Users\KevSa\miniconda3\shell\condabin\conda-hook.ps1"
   ```

### For Command Prompt:
1. **Open Command Prompt**
2. **Run this command** (replace with your actual Miniconda path):
   ```cmd
   C:\Users\KevSa\miniconda3\Scripts\conda.exe init cmd.exe
   ```

## Option 3: Use Full Paths (No PATH needed)

You can use conda by specifying the full path:

```cmd
# Instead of: conda --version
C:\Users\KevSa\miniconda3\Scripts\conda.exe --version

# Instead of: conda env create -f environment.yml
C:\Users\KevSa\miniconda3\Scripts\conda.exe env create -f environment.yml

# Instead of: conda activate mcdonalds-mcnuggets
C:\Users\KevSa\miniconda3\Scripts\conda.exe activate mcdonalds-mcnuggets
```

## Option 4: Create a Custom Setup Script

I'll create a script that uses full paths so you don't need to modify PATH:

```batch
@echo off
set CONDA_PATH=C:\Users\KevSa\miniconda3\Scripts\conda.exe

echo Setting up conda environment using full paths...

REM Create the conda environment
%CONDA_PATH% env create -f environment.yml

REM Activate the environment
call %CONDA_PATH% activate mcdonalds-mcnuggets

REM Install as Jupyter kernel
python -m ipykernel install --user --name mcdonalds-mcnuggets --display-name "McDonald's McNuggets"

echo Setup complete!
pause
```

## Recommended Approach

**I recommend Option 1 (Anaconda Prompt)** because:
- ✅ No PATH modification needed
- ✅ Works immediately after installation
- ✅ Conda is always available
- ✅ No system-wide changes
- ✅ Easy to use

## Installation Steps (Without PATH)

1. **Install Miniconda** - DON'T check "Add to PATH"
2. **Use Anaconda Prompt** from Start menu
3. **Navigate to your project**:
   ```cmd
   cd C:\Users\KevSa\Documents\GitHub\McDonalds-McNuggets
   ```
4. **Run setup**:
   ```cmd
   setup_conda.bat
   ```

## For Cursor Integration

Once your environment is created, Cursor will be able to find it even without conda in PATH because:
- Cursor scans for Python installations
- It will find the conda environment in the standard location
- You can manually point Cursor to the environment if needed

## Why the PATH Warning?

The installer warns about PATH because:
- It can conflict with other Python installations
- It might override system Python
- It can cause issues with other development tools
- Using Anaconda Prompt is cleaner and safer

Would you like me to create a custom setup script that uses full paths, or would you prefer to use the Anaconda Prompt approach?

