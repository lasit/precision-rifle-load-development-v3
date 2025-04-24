# AI Assistant Guide for Precision Rifle Load Development

This document provides guidance for AI assistants working with the Precision Rifle Load Development application codebase. It outlines the project structure, key components, and common tasks to help AI assistants provide effective assistance.

## Project Overview

The Precision Rifle Load Development application is a PyQt-based desktop application for tracking and analyzing precision rifle load development data. It allows users to:

- Create and manage test data for different rifle loads
- Track important parameters like platform details, ammunition components, and results
- Visualize and analyze test data
- Manage component lists
- Configure multiple test databases (local or Google Drive)

## Project Structure

- `pyqt_app/`: PyQt application directory
  - `main.py`: Main application window and tab management
  - `run.py`: Entry point script with dependency checking
  - `modules/`: Application modules
    - `view_test.py`: View and edit test data
    - `data_analysis.py`: Data analysis and visualization
    - `create_test.py`: Create new tests
    - `admin.py`: Component list management
    - `settings.py`: Settings dialog for database management
  - `utils/`: Utility functions
    - `data_loader.py`: Data loading and processing functions
    - `settings_manager.py`: Settings management with multiple database support
- `Component_List.yaml`: Dropdown list data
- `run.py`: Convenience script to start the application
- `start_app.command`: macOS script for easy application launch with dependency checking
- `start_app.bat`: Windows script for easy application launch with dependency checking
- `tests/`: Directory containing test data folders (can be configured to use Google Drive)
- `docs/`: Comprehensive documentation

## Key Components

### Main Window (`main.py`)

The main window is the entry point of the application. It:
- Creates the tab-based interface
- Sets up the menu bar with File and Help menus
- Manages the settings dialog
- Handles database switching and refreshing

### Settings Manager (`settings_manager.py`)

The settings manager handles application settings, including:
- Multiple database pointers (label and path)
- Active database selection
- Platform-specific configuration storage
- Settings migration from older versions

### Settings Dialog (`settings.py`)

The settings dialog allows users to:
- View and manage database pointers
- Add, update, and delete database pointers
- Set the active database
- Browse for test directories

### Data Loader (`data_loader.py`)

The data loader handles:
- Loading test data from the active database
- Parsing YAML files
- Validating test data
- Error handling for missing or invalid files

## Common Tasks

### Adding a New Feature

When adding a new feature:
1. Identify the appropriate module for the feature
2. Understand the existing code patterns
3. Implement the feature following the existing patterns
4. Update the UI as needed
5. Add appropriate error handling
6. Update documentation

### Fixing Bugs

When fixing bugs:
1. Understand the root cause of the bug
2. Identify the affected components
3. Make minimal changes to fix the issue
4. Add appropriate error handling
5. Test the fix thoroughly

### Working with Multiple Databases

The application supports multiple database pointers:
1. Each database has a label and a path
2. The active database is used for loading and saving test data
3. Database pointers are managed through the settings dialog
4. The active database is shown in the window title and status bar

## Best Practices

1. Follow the existing code patterns and style
2. Use PyQt6 for all UI components
3. Handle errors gracefully with appropriate user feedback
4. Keep the codebase clean and organized
5. Document all changes and new features
6. Test changes thoroughly before committing

## Documentation

The project includes comprehensive documentation in the `docs/` directory:
- `INDEX.md`: Entry point for documentation
- `ARCHITECTURE.md`: Technical architecture details
- `COMPONENTS.md`: Detailed component documentation
- `DATA_STRUCTURES.md`: Data schemas and relationships
- `GOOGLE_DRIVE_SETUP.md`: Google Drive integration setup
- `DEVELOPMENT.md`: Development guidelines
- `CHANGELOG.md`: Version history and changes

## Conclusion

This guide provides a high-level overview of the Precision Rifle Load Development application to help AI assistants understand the codebase and provide effective assistance. For more detailed information, refer to the specific documentation files in the `docs/` directory.
