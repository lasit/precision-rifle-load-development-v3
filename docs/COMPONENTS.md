# Precision Rifle Load Development Components

This document provides detailed documentation for the main components of the Precision Rifle Load Development application.

## Main Window

The main window (`pyqt_app/main.py`) is the central component of the application. It:

- Creates and manages the tab-based interface
- Sets up the menu bar with File and Help menus
- Coordinates communication between modules
- Handles settings and database management

### Key Methods

- `__init__()`: Initializes the main window and sets up the UI
- `setup_ui()`: Sets up the UI components and tab widget
- `setup_menu()`: Sets up the menu bar with File and Help menus
- `show_settings_dialog()`: Shows the settings dialog
- `refresh_after_settings_change()`: Refreshes the application after settings changes
- `update_active_database()`: Updates the active database indicator

## View Test Module

The View Test module (`pyqt_app/modules/view_test.py`) allows users to view and edit existing tests. It:

- Displays a list of available tests
- Shows test details in a two-column layout
- Allows editing of test parameters
- Provides interactive target image viewing with zoom and pan capabilities
- Saves changes back to the test file

### Key Classes

- `ViewTestWidget`: Main widget for viewing and editing tests
- `ZoomableImageLabel`: Custom QLabel that supports zooming and panning of target images

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components with a two-column layout
- `load_test()`: Loads a test from a file
- `save_test()`: Saves changes to a test file
- `refresh()`: Refreshes the list of available tests
- `refresh_component_lists()`: Refreshes the component dropdown lists
- `_create_image_group()`: Creates the target image group with zoom and pan capabilities
- `_create_results_target_group()`: Creates the Results Target group
- `_create_results_velocity_group()`: Creates the Results Velocity group

## Data Analysis Module

The Data Analysis module (`pyqt_app/modules/data_analysis.py`) provides tools for analyzing and visualizing test data. It:

- Displays test data in a table
- Provides filtering options for test data
- Generates charts and visualizations
- Allows exporting of analysis results

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components
- `load_tests()`: Loads all tests from the active database
- `filter_tests()`: Filters tests based on user criteria
- `generate_charts()`: Generates charts and visualizations
- `refresh()`: Refreshes the test data

## Create Test Module

The Create Test module (`pyqt_app/modules/create_test.py`) allows users to create new tests. It:

- Provides a form for entering test parameters
- Validates input data
- Generates a unique test ID
- Creates a new test file
- Emits a signal when a test is created

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components
- `validate_form()`: Validates the form input
- `generate_test_id()`: Generates a unique test ID
- `create_test()`: Creates a new test file
- `refresh()`: Refreshes the component dropdown lists

## Admin Module

The Admin module (`pyqt_app/modules/admin.py`) allows users to manage component lists. It:

- Displays the current component lists
- Allows adding, editing, and deleting components
- Saves changes to the component list file
- Emits a signal when component lists are updated

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components
- `load_component_lists()`: Loads the component lists from the file
- `save_component_lists()`: Saves changes to the component list file
- `add_component()`: Adds a new component
- `edit_component()`: Edits an existing component
- `delete_component()`: Deletes a component

## Settings Dialog

The Settings dialog (`pyqt_app/modules/settings.py`) allows users to configure application settings. It:

- Displays the current database pointers
- Allows adding, editing, and deleting database pointers
- Provides a way to set the active database
- Validates directory paths
- Saves settings to the configuration file

### Key Classes

- `DatabaseItem`: Custom list widget item for displaying database pointers
- `SettingsDialog`: Dialog for configuring application settings

### Key Methods

- `__init__()`: Initializes the dialog and sets up the UI
- `populate_database_list()`: Populates the database list with current databases
- `on_database_selected()`: Handles database selection
- `validate_directory()`: Validates a directory path
- `validate_label()`: Validates a database label
- `add_database()`: Adds a new database pointer
- `update_database()`: Updates an existing database pointer
- `delete_database()`: Deletes a database pointer
- `set_active_database()`: Sets the active database

## Settings Manager

The Settings Manager (`pyqt_app/utils/settings_manager.py`) handles application settings. It:

- Uses the singleton pattern to ensure consistent settings
- Stores settings in a platform-specific location
- Provides methods for accessing and modifying settings
- Supports multiple database pointers
- Handles migration from older settings formats

### Key Methods

- `get_instance()`: Gets the singleton instance of the SettingsManager
- `_get_config_file_path()`: Gets the platform-specific path for the configuration file
- `_load_settings()`: Loads settings from the configuration file
- `save_settings()`: Saves settings to the configuration file
- `get_tests_directory()`: Gets the tests directory path for the active database
- `get_active_database()`: Gets the label of the active database
- `set_active_database()`: Sets the active database by label
- `get_databases()`: Gets the list of database pointers
- `add_database()`: Adds a new database pointer
- `update_database()`: Updates an existing database pointer
- `delete_database()`: Deletes a database pointer

## Data Loader

The Data Loader (`pyqt_app/utils/data_loader.py`) handles loading and processing test data. It:

- Loads test data from YAML files
- Validates test data
- Provides error handling for missing or invalid files
- Supports loading from different database directories

### Key Methods

- `load_test()`: Loads a test from a file
- `load_all_tests()`: Loads all tests from the active database
- `save_test()`: Saves a test to a file
- `validate_test()`: Validates test data
- `get_test_list()`: Gets a list of available tests

## Conclusion

This document provides an overview of the main components of the Precision Rifle Load Development application. Each component is designed to handle a specific aspect of the application's functionality, with clear interfaces for communication between components.
