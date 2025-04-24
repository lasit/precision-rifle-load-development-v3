#!/usr/bin/env python3
"""
Run script for the Precision Rifle Load Development App (PyQt)
This is a convenience script to start the application from the root directory
"""

import os
import sys
import subprocess

def main():
    """Run the PyQt application"""
    # Get the path to the pyqt_app/run.py script
    pyqt_run_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pyqt_app",
        "run.py"
    )
    
    # Execute the script
    try:
        subprocess.run([sys.executable, pyqt_run_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
