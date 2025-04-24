#!/usr/bin/env python3
"""
Run script for the Reloading App
Provides a convenient way to start the application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import PyQt6
        import matplotlib
        import pandas
        import numpy
        import yaml
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    print("Dependencies installed successfully.")

def run_app():
    """Run the application"""
    # Add the parent directory to the path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import and run the main function
    from pyqt_app.main import main
    main()

if __name__ == "__main__":
    # Check if dependencies are installed
    if not check_dependencies():
        # Ask the user if they want to install dependencies
        response = input("Some dependencies are missing. Do you want to install them now? (y/n): ")
        if response.lower() == "y":
            install_dependencies()
        else:
            print("Cannot run the application without required dependencies.")
            sys.exit(1)
    
    # Run the application
    run_app()
