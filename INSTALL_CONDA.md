# Installing Conda on Windows

Since conda is not currently installed on your system, here are the steps to install it:

## Option 1: Miniconda (Recommended)

Miniconda is a minimal conda installer that's perfect for development projects.

### Download and Install:

1. **Download Miniconda**:
   - Go to: https://docs.conda.io/en/latest/miniconda.html
   - Download the **Windows 64-bit** installer (Python 3.11)
   - File will be named something like: `Miniconda3-latest-Windows-x86_64.exe`

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - **Important**: During installation, check the box that says:
     - ✅ "Add Miniconda3 to my PATH environment variable"
     - ✅ "Register Miniconda3 as my default Python 3.x"

3. **Verify Installation**:
   - Close and reopen your command prompt/PowerShell
   - Run: `conda --version`
   - You should see something like: `conda 23.x.x`

## Option 2: Anaconda (Full Distribution)

If you prefer the full Anaconda distribution with many pre-installed packages:

1. **Download Anaconda**:
   - Go to: https://www.anaconda.com/products/distribution
   - Download the **Windows 64-bit** installer

2. **Install**:
   - Run the installer
   - Make sure to check "Add Anaconda to PATH" during installation

## After Installation

Once conda is installed, you can proceed with setting up your project environment:

### Quick Setup:
```cmd
# Navigate to your project directory
cd C:\Users\KevSa\Documents\GitHub\McDonalds-McNuggets

# Run the setup script
setup_conda.bat
```

### Manual Setup:
```cmd
# Create the environment
conda env create -f environment.yml

# Activate the environment
conda activate mcdonalds-mcnuggets
```

## Troubleshooting

### If conda command is not recognized:
1. **Restart your terminal** after installation
2. **Check PATH**: Open System Properties → Environment Variables → System Variables → PATH
   - Look for entries like: `C:\Users\KevSa\miniconda3\Scripts` and `C:\Users\KevSa\miniconda3`
3. **Manual PATH addition**: If not found, add these paths manually to your PATH

### Alternative: Use Anaconda Prompt
- Search for "Anaconda Prompt" in your Start menu
- This terminal automatically has conda in its PATH
- Use this terminal to run conda commands

## Next Steps

After conda is installed and working:

1. **Test conda**: `conda --version`
2. **Create environment**: `conda env create -f environment.yml`
3. **Activate environment**: `conda activate mcdonalds-mcnuggets`
4. **Configure Cursor**: Select the conda environment as your Python interpreter

## Need Help?

If you encounter any issues:
1. Make sure you restarted your terminal after installation
2. Try using "Anaconda Prompt" instead of regular command prompt
3. Check that conda is in your system PATH
4. Verify the installation by running `conda info`

