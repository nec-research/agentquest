#!/bin/bash
# Required for downloading multimodal files from GAIA's huggingface repo
set -e

# Ensure Hugging Face CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "Error: Hugging Face CLI is not installed. Please install it and try again."
    exit 1
fi

# Login to Hugging Face
echo "Logging into Hugging Face..."
huggingface-cli login # Add the token as git credential

# Clone the GAIA dataset
if [ ! -d "GAIA" ]; then
    echo "Cloning the GAIA dataset..."
    git clone https://huggingface.co/datasets/gaia-benchmark/GAIA
else
    echo "GAIA dataset already cloned. Skipping..."
fi

rm GAIA/GAIA.py
rm GAIA/.gitattributes

echo "Setup completed successfully!"
