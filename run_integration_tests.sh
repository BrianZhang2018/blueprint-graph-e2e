#!/bin/bash

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov docker

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration -v

# Deactivate virtual environment
deactivate 