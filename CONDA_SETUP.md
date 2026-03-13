# Conda Environment Setup for McDonald's McNuggets

This guide will help you set up a conda environment for the McDonald's McNuggets project.

## Prerequisites

1. **Install Conda**: If you don't have conda installed, download and install either:
   - [Anaconda](https://www.anaconda.com/products/distribution) (full distribution)
   - [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (minimal distribution)

2. **Verify Installation**: Open a terminal/command prompt and run:
   ```bash
   conda --version
   ```

## Quick Setup

### Windows
Run the setup script:
```cmd
setup_conda.bat
```

### macOS/Linux
Run the setup script:
```bash
./setup_conda.sh
```

### Manual Setup
If you prefer to set up manually:

1. **Create the environment**:
   ```bash
   conda env create -f environment.yml
   ```

2. **Activate the environment**:
   ```bash
   conda activate mcdonalds-mcnuggets
   ```

3. **Install as Jupyter kernel** (optional):
   ```bash
   python -m ipykernel install --user --name mcdonalds-mcnuggets --display-name "McDonald's McNuggets"
   ```

## Using the Environment

### Activating the Environment
```bash
conda activate mcdonalds-mcnuggets
```

### Running the Backend Services

**FastAPI Backend** (FileWizardAI):
```bash
cd FileWizardAI/backend
python -m app.server
```

**Flask Backend** (NAS Client):
```bash
python nas_client.py
```

### Deactivating the Environment
```bash
conda deactivate
```

## Environment Details

The conda environment includes:

- **Python 3.11**
- **FastAPI dependencies**: fastapi, uvicorn, openai, llama-index, etc.
- **Flask dependencies**: flask, werkzeug, python-dotenv, etc.
- **Additional tools**: jupyter, pandas, numpy, matplotlib

## Cursor Integration

1. **Select the conda environment in Cursor**:
   - Open Command Palette (`Ctrl + Shift + P`)
   - Type "Python: Select Interpreter"
   - Choose the `mcdonalds-mcnuggets` environment

2. **Terminal activation**: The environment should auto-activate in Cursor's terminal, but if not, manually run:
   ```bash
   conda activate mcdonalds-mcnuggets
   ```

## Troubleshooting

### Environment not found
If Cursor can't find the conda environment:
1. Make sure conda is in your system PATH
2. Restart Cursor after creating the environment
3. Manually specify the Python interpreter path

### Package conflicts
If you encounter package conflicts:
1. Update the environment: `conda env update -f environment.yml`
2. Or recreate it: `conda env remove -n mcdonalds-mcnuggets` then `conda env create -f environment.yml`

### Terminal not activating environment
If the terminal doesn't auto-activate the environment:
1. Manually activate: `conda activate mcdonalds-mcnuggets`
2. Check Cursor's Python extension settings
3. Ensure the correct interpreter is selected

## Managing Dependencies

### Adding new packages
```bash
conda activate mcdonalds-mcnuggets
conda install package_name
# or
pip install package_name
```

### Updating environment.yml
After installing new packages, update the environment file:
```bash
conda env export > environment.yml
```

### Sharing the environment
The `environment.yml` file can be shared with others to recreate the exact same environment.

