#!/bin/bash
# Setup script for Construction Lead Generation System

echo "=================================="
echo "Construction Lead Generation Setup"
echo "=================================="
echo

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo
    echo "IMPORTANT: Edit .env file and add your API keys:"
    echo "  - ANTHROPIC_API_KEY (required)"
    echo "  - SERPER_API_KEY (optional but recommended)"
fi

# Create necessary directories
echo
echo "Creating directories..."
mkdir -p output
mkdir -p logs

echo
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the system:"
echo "   python main.py --max-leads 10"
echo
echo "See QUICKSTART.md for more information"
echo
