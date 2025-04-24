# Precision Rifle Load Development - PyQt Implementation

A cross-platform desktop application for precision rifle load development, built with PyQt6.

## Overview

This application is a PyQt6-based implementation of the Precision Rifle Load Development tool, designed to work on both macOS and Windows. It provides a user-friendly interface for:

1. Creating and managing load development tests
2. Analyzing test data with advanced filtering and visualization
3. Managing components and configurations

## Project Structure

```
pyqt_app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── modules/                # Application modules
│   ├── data_analysis.py    # Data analysis module
│   ├── create_test.py      # Test creation module (to be implemented)
│   └── admin.py            # Admin module (to be implemented)
├── utils/                  # Utility functions (to be implemented)
└── resources/              # Application resources (to be implemented)
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- PyQt6
- Matplotlib
- Pandas
- Other dependencies listed in requirements.txt

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r pyqt_app/requirements.txt
   ```

4. Run the application:
   ```
   python pyqt_app/main.py
   ```

## Features

### Data Analysis

- Filter tests by various criteria (caliber, rifle, bullet, powder, etc.)
- View test data in a sortable table
- Visualize test results with interactive plots
- Compare multiple tests to identify trends and optimal loads

### Test Creation (Coming Soon)

- Create new load development tests
- Record all relevant test parameters
- Import chronograph data
- Capture and analyze target images

### Admin Interface (Coming Soon)

- Manage component lists (rifles, bullets, powders, etc.)
- Configure application settings
- Backup and restore data

## Building Standalone Executables

### macOS

```
pyinstaller --windowed --name "Precision Rifle Load Development" --icon=resources/icon.icns pyqt_app/main.py
```

### Windows

```
pyinstaller --windowed --name "Precision Rifle Load Development" --icon=resources/icon.ico pyqt_app/main.py
```

## License

[License information to be added]

## Acknowledgments

- Original Streamlit implementation by [Author]
- PyQt6 and Qt for providing the cross-platform framework
- Matplotlib for data visualization capabilities
