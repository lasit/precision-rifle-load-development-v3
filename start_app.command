#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Kill any running instances of the application
echo "Checking for running instances..."
./kill_app.sh

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install Python 3 and pip3 first."
    echo "Press Enter to close this window..."
    read
    exit 1
fi

# Check if the requirements are installed
echo "Checking dependencies..."
MISSING_DEPS=false

# Read requirements.txt and check if each package is installed
while read -r package; do
    # Skip empty lines and comments
    if [[ -z "$package" || "$package" == \#* ]]; then
        continue
    fi
    
    # Extract package name (remove version specifier)
    pkg_name=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
    
    # Check if package is installed
    if ! pip3 list | grep -i "^$pkg_name " &> /dev/null; then
        echo "Missing dependency: $pkg_name"
        MISSING_DEPS=true
    fi
done < requirements.txt

# Install dependencies if any are missing
if [ "$MISSING_DEPS" = true ]; then
    echo "Installing missing dependencies..."
    pip3 install -r requirements.txt
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies. Please try running 'pip3 install -r requirements.txt' manually."
        echo "Press Enter to close this window..."
        read
        exit 1
    fi
    echo "Dependencies installed successfully."
else
    echo "All dependencies are already installed."
fi

# Run the application
echo "Starting the application..."
python3 run.py

# Keep the terminal window open after the application exits
echo "Application closed. Press Enter to close this window..."
read
