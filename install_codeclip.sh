#!/bin/bash
# Installation script for codeclip

# Define installation directory
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="codeclip"

# Check if script exists in current directory
if [ ! -f "codeclip.py" ]; then
    echo "Error: codeclip.py not found in current directory."
    exit 1
fi

# Make script executable
chmod +x codeclip.py

# Check if installation directory exists and is writable
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating directory $INSTALL_DIR..."
    sudo mkdir -p "$INSTALL_DIR"
fi

if [ ! -w "$INSTALL_DIR" ]; then
    echo "Installing to $INSTALL_DIR (requires sudo)..."
    sudo cp codeclip.py "$INSTALL_DIR/$SCRIPT_NAME"
else
    echo "Installing to $INSTALL_DIR..."
    cp codeclip.py "$INSTALL_DIR/$SCRIPT_NAME"
fi

# Verify installation
if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo "Installation successful! You can now use 'codeclip' from anywhere."
    echo ""
    echo "Usage examples:"
    echo "  codeclip ~/projects/myapp --extensions py,js,html"
    echo "  codeclip . --exclude node_modules,venv --max-size 100"
    echo "  codeclip ~/project --max-depth 2"
else
    echo "Installation failed."
    exit 1
fi
