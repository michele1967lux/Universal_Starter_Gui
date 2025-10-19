#!/bin/bash
# Launch script for Universal Starter GUI

echo "Starting Universal Starter GUI..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if dependencies are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import customtkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements_STARTER_GUI.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

echo "Dependencies OK"
echo ""

# Run the application
echo "Launching application..."
$PYTHON_CMD universal_STARTER_GUI.py

exit $?
