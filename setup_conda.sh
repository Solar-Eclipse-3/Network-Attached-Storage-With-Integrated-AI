#!/bin/bash

echo "Setting up conda environment for McDonald's McNuggets project..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

# Create the conda environment
echo "Creating conda environment from environment.yml..."
conda env create -f environment.yml

if [ $? -ne 0 ]; then
    echo "Error: Failed to create conda environment"
    exit 1
fi

# Activate the environment
echo "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcdonalds-mcnuggets

# Install the environment as a Jupyter kernel
echo "Installing as Jupyter kernel..."
python -m ipykernel install --user --name mcdonalds-mcnuggets --display-name "McDonald's McNuggets"

echo ""
echo "Setup complete!"
echo ""
echo "To activate the environment manually, run:"
echo "  conda activate mcdonalds-mcnuggets"
echo ""
echo "To run the FastAPI backend:"
echo "  cd FileWizardAI/backend"
echo "  python -m app.server"
echo ""
echo "To run the Flask backend:"
echo "  python nas_client.py"
echo ""

