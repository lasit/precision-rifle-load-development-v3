# Precision Rifle Load Development Requirements

This document outlines the dependency requirements and installation instructions for the Precision Rifle Load Development application.

## System Requirements

### Operating Systems

The application is designed to run on the following operating systems:

- **Windows**: Windows 10 or later
- **macOS**: macOS 10.15 (Catalina) or later
- **Linux**: Ubuntu 20.04 or later, or other modern Linux distributions

### Hardware Requirements

- **Processor**: 1.6 GHz or faster processor
- **RAM**: 4 GB or more
- **Disk Space**: 100 MB for the application, plus additional space for test data
- **Display**: 1280 x 720 or higher resolution

## Software Dependencies

### Python

The application requires Python 3.9 or higher. You can download Python from the [official website](https://www.python.org/downloads/).

### Python Packages

The application depends on the following Python packages:

#### Core Dependencies

- **PyQt6**: Version 6.5.0 or higher
  - The main GUI framework used by the application
  - Provides widgets, layouts, and event handling

- **matplotlib**: Version 3.9.0 or higher
  - Used for generating charts and visualizations
  - Provides plotting capabilities for data analysis

- **pandas**: Version 2.0.0 or higher
  - Used for data manipulation and analysis
  - Provides data structures for storing and analyzing test data

- **numpy**: Version 1.24.0 or higher
  - Used for numerical computations
  - Provides array operations and mathematical functions

- **pyyaml**: Version 6.0.0 or higher
  - Used for reading and writing YAML files
  - Provides YAML parsing and serialization

#### Optional Dependencies

- **plotly**: Version 5.14.0 or higher
  - Used for interactive visualizations
  - Provides additional plotting capabilities

- **pyqtgraph**: Version 0.13.3 or higher
  - Used for real-time plotting
  - Provides fast plotting capabilities for large datasets

- **pillow**: Version 9.5.0 or higher
  - Used for image handling
  - Provides image processing capabilities

#### Packaging Tools

- **pyinstaller**: Version 5.10.0 or higher
  - Used for creating standalone executables
  - Provides packaging capabilities for distribution

## Installation

### Using the Launcher Scripts

The easiest way to install the application is to use the provided launcher scripts, which will automatically check for and install any missing dependencies:

#### Windows

1. Double-click `start_app.bat`
2. The script will check for Python and required packages
3. If any dependencies are missing, the script will install them
4. The application will start automatically

#### macOS

1. Double-click `start_app.command`
2. If prompted, allow the script to execute
3. The script will check for Python and required packages
4. If any dependencies are missing, the script will install them
5. The application will start automatically

#### Linux

1. Open a terminal in the application directory
2. Make the script executable: `chmod +x start_app.sh`
3. Run the script: `./start_app.sh`
4. The script will check for Python and required packages
5. If any dependencies are missing, the script will install them
6. The application will start automatically

### Manual Installation

If you prefer to install the dependencies manually:

1. Ensure Python 3.9 or higher is installed
2. Create a virtual environment (optional but recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```

## Google Drive Integration

For Google Drive integration, you need to install the Google Drive desktop client:

- **Windows/macOS**: [Google Drive for Desktop](https://www.google.com/drive/download/)
- **Linux**: [Insync](https://www.insynchq.com/) or another Google Drive client

See [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) for detailed instructions on setting up Google Drive integration.

## Development Dependencies

If you're developing the application, you may want to install additional packages:

- **pytest**: For running tests
- **pylint**: For code linting
- **black**: For code formatting
- **sphinx**: For generating documentation

You can install these packages with:

```bash
pip install pytest pylint black sphinx
```

## Troubleshooting

### Common Issues

#### Missing Dependencies

If you encounter errors about missing dependencies, try:

```bash
pip install -r requirements.txt
```

#### PyQt6 Installation Issues

If you have issues installing PyQt6:

- **Windows**: Ensure you have the latest pip version: `python -m pip install --upgrade pip`
- **macOS**: You may need to install additional dependencies: `brew install qt`
- **Linux**: You may need to install additional dependencies: `sudo apt-get install python3-pyqt6`

#### Permission Issues

If you encounter permission issues:

- **Windows**: Run the command prompt as administrator
- **macOS/Linux**: Use `sudo` for system-wide installation, or use a virtual environment

### Getting Help

If you encounter issues not covered here, please:

1. Check the [GitHub repository](https://github.com/lasit/precision-rifle-load-development-v3) for known issues
2. Create a new issue if your problem is not already reported

## Conclusion

This document outlines the requirements and installation instructions for the Precision Rifle Load Development application. By following these instructions, you should be able to install and run the application on your system.
