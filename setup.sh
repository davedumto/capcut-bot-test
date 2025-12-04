#!/bin/bash

# CapCut Bot Test Environment Setup Script
# This script sets up the entire Playwright testing environment

echo "Setting up CapCut Bot Test Environment..."

# Create and activate virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Playwright
echo "Installing Playwright..."
pip install playwright --timeout 60

# Install Chromium browser
echo "Installing Chromium browser..."
playwright install chromium

echo "Setup completed!"
echo ""
echo "To run the test:"
echo "1. cd capcut-bot-test"
echo "2. source venv/bin/activate"
echo "3. python test_capcut.py"